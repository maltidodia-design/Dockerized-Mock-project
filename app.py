import json
import os
import threading
import time
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Read the DB URI from env so tests (in-process AND live-server subprocess) can
# point it at an isolated SQLite before SQLAlchemy(app) below builds the engine.
# Flask-SQLAlchemy 3.x caches the engine at construction time, so a late
# app.config[...] override is silently ignored.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI', 'sqlite:///data.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Hard cap on POST body size to limit abuse / accidental memory blow-up.
app.config['MAX_CONTENT_LENGTH'] = int(
    os.environ.get('MAX_CONTENT_LENGTH', str(1 * 1024 * 1024))  # 1 MiB
)

db = SQLAlchemy(app)

# take_quiz.html uses enumerate() in a Jinja loop; Jinja2 does not expose it by
# default, so register it as a global. Without this, GET /take/<id> raises
# UndefinedError and returns HTTP 500 under a real server (gunicorn / python app.py).
app.jinja_env.globals.update(enumerate=enumerate)


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    questions_json = db.Column(db.Text, nullable=False)  # list of questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def questions(self):
        return json.loads(self.questions_json)


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    details_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --------------------------------------------------------------------------- #
# Cross-cutting middleware: security headers, Origin-based CSRF, rate limit.
# Kept hand-rolled (no Flask-WTF / Flask-Limiter dep) so the mock product
# remains dependency-light; the test suites exercise the real protections.
# --------------------------------------------------------------------------- #

_RATE_LIMIT_WINDOW = float(os.environ.get('RATE_LIMIT_WINDOW', '60'))   # seconds
_RATE_LIMIT_MAX = int(os.environ.get('RATE_LIMIT_MAX', '60'))           # requests per window per IP
_rate_state = defaultdict(list)  # ip -> sorted list of timestamps
_rate_lock = threading.Lock()


def _is_rate_limited(ip):
    if _RATE_LIMIT_MAX <= 0:
        return False  # disabled
    now = time.time()
    cutoff = now - _RATE_LIMIT_WINDOW
    with _rate_lock:
        recent = [t for t in _rate_state[ip] if t > cutoff]
        if len(recent) >= _RATE_LIMIT_MAX:
            _rate_state[ip] = recent
            return True
        recent.append(now)
        _rate_state[ip] = recent
        return False


@app.before_request
def _csrf_origin_check():
    """Minimal CSRF mitigation: reject state-changing requests whose Origin
    header is set and points to a different host. Same-origin requests (which
    is what a real form submit from this site produces) are allowed; legacy
    clients that omit Origin are allowed (Referer fallback could be layered in)."""
    if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
        origin = request.headers.get('Origin')
        if origin:
            origin_host = urlparse(origin).netloc
            if origin_host and origin_host != request.host:
                return ('Cross-origin request rejected', 403)


@app.before_request
def _api_rate_limit():
    if request.path == '/api/ai_feedback' and request.method == 'POST':
        ip = request.remote_addr or 'unknown'
        if _is_rate_limited(ip):
            return jsonify(error='rate_limited'), 429


@app.after_request
def _security_headers(resp):
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    resp.headers.setdefault('X-Frame-Options', 'DENY')
    resp.headers.setdefault('Content-Security-Policy', "default-src 'self'")
    resp.headers.setdefault('Referrer-Policy', 'no-referrer')
    return resp


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.route('/healthz')
def healthz():
    """Liveness/readiness probe.

    Returns 200 without touching the DB so orchestrators (Docker HEALTHCHECK,
    k8s liveness, CI smoke) get a meaningful, dependency-free signal.
    """
    return jsonify(status='ok'), 200


@app.route('/')
def index():
    quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    return render_template('index.html', quizzes=quizzes)


@app.route('/create', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('title') or 'Untitled Quiz'
        questions_raw = request.form.get('questions')
        try:
            questions = json.loads(questions_raw)
        except Exception:
            return "Invalid questions JSON", 400

        quiz = Quiz(title=title, questions_json=json.dumps(questions))
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for('index'))

    sample_questions = [
        {
            'text': 'What is 2 + 2?',
            'choices': ['1', '2', '3', '4'],
            'answer_index': 3
        }
    ]
    return render_template('create_quiz.html', sample=json.dumps(sample_questions, indent=2))


@app.route('/take/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions()
    if request.method == 'POST':
        answers = {}
        for i in range(len(questions)):
            v = request.form.get(f'question-{i}')
            if v is None:
                continue
            # Form tampering: non-integer values used to surface as HTTP 500
            # (ValueError). Treat as unanswered so the user sees a normal
            # result page and an audit trail is still recorded.
            try:
                answers[str(i)] = int(v)
            except (ValueError, TypeError):
                continue

        correct = 0
        details = []
        for i, q in enumerate(questions):
            expected = q.get('answer_index')
            given = answers.get(str(i))
            ok = (given == expected)
            if ok:
                correct += 1
            details.append({'index': i, 'given': given, 'expected': expected, 'ok': ok})

        score = correct
        total = len(questions)
        result = Result(quiz_id=quiz.id, score=score, total=total, details_json=json.dumps(details))
        db.session.add(result)
        db.session.commit()

        # Call the AI feedback helper directly (NOT via app.test_client().post,
        # which was an in-process HTTP-to-itself antipattern: it doubled worker
        # usage, looped through middleware (rate limit!) unnecessarily, and
        # masked real failure modes).
        try:
            feedback_resp = _generate_ai_feedback(details)
        except Exception:
            feedback_resp = {'error': 'feedback unavailable'}

        return render_template('result.html', quiz=quiz, score=score, total=total, details=details, feedback=feedback_resp)

    return render_template('take_quiz.html', quiz=quiz, questions=questions)


def _generate_ai_feedback(details_raw):
    """Pure helper that produces the mock AI feedback payload.

    Kept separate so take_quiz can call it directly (no internal HTTP
    recursion) AND the public /api/ai_feedback endpoint can call it. Non-dict
    elements in `details_raw` are skipped — a malformed input used to surface
    as HTTP 500 (AttributeError on .get for non-dict elements).
    """
    explanations = []
    improvement_topics = set()
    for d in details_raw or []:
        if not isinstance(d, dict):
            continue
        if not d.get('ok'):
            idx = d.get('index')
            explanations.append({'index': idx, 'explanation': f"Review question {idx}: consider re-checking fundamentals."})
            improvement_topics.add('fundamentals')
    return {
        'explanations': explanations,
        'recommendations': list(improvement_topics) if improvement_topics else ['practice_more']
    }


@app.route('/api/ai_feedback', methods=['POST'])
def ai_feedback():
    # Non-silent on purpose: a non-JSON request body returns 415 (Flask's
    # default behaviour); a valid-JSON-but-empty body falls through to `or {}`.
    payload = request.get_json() or {}
    return jsonify(_generate_ai_feedback(payload.get('details', [])))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
