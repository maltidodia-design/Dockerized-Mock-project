import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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


@app.route('/')
def index():
    quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    return render_template('index.html', quizzes=quizzes)


@app.route('/create', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('title') or 'Untitled Quiz'
        # questions posted as JSON string in form field
        questions_raw = request.form.get('questions')
        try:
            questions = json.loads(questions_raw)
        except Exception:
            return "Invalid questions JSON", 400

        quiz = Quiz(title=title, questions_json=json.dumps(questions))
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for('index'))

    # sample question structure to show in form
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
            if v is not None:
                answers[str(i)] = int(v)

        # grade
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

        # call AI feedback stub (internal endpoint) to get explanations for incorrect
        feedback_resp = None
        try:
            # lightweight internal call
            from flask import url_for
            # send minimal data
            resp = app.test_client().post('/api/ai_feedback', json={'quiz_id': quiz.id, 'details': details})
            if resp.status_code == 200:
                feedback_resp = resp.get_json()
        except Exception:
            feedback_resp = {'error': 'feedback unavailable'}

        return render_template('result.html', quiz=quiz, score=score, total=total, details=details, feedback=feedback_resp)

    return render_template('take_quiz.html', quiz=quiz, questions=questions)


@app.route('/api/ai_feedback', methods=['POST'])
def ai_feedback():
    # This is a mock / stub for the AI behavior described in the product requirements.
    # It takes quiz_id and grading details and returns simple explanations and recommendations.
    payload = request.get_json() or {}
    details = payload.get('details', [])

    explanations = []
    improvement_topics = set()
    for d in details:
        if not d.get('ok'):
            idx = d.get('index')
            explanations.append({'index': idx, 'explanation': f"Review question {idx}: consider re-checking fundamentals."})
            improvement_topics.add('fundamentals')

    resp = {
        'explanations': explanations,
        'recommendations': list(improvement_topics) if improvement_topics else ['practice_more']
    }
    return jsonify(resp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
