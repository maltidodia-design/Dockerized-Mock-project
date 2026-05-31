import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import pytest
import requests

# Ensure project root is on sys.path so tests can import app.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Force the in-process app to use an in-memory DB BEFORE importing app.py,
# because Flask-SQLAlchemy 3.x caches the engine at SQLAlchemy(app) — a late
# config override has no effect. Without this, in-process tests silently used
# the real instance/data.db and dropped its tables, breaking the live-server
# subprocess which (by default) also targets instance/data.db.
os.environ.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')

# Effectively disable the production rate limit for in-process unit tests
# (where many tests hit /api/ai_feedback through the same test client).
os.environ.setdefault('RATE_LIMIT_MAX', '999999')

from app import app as flask_app, db, Quiz

# --------------------------------------------------------------------------- #
# In-process fixtures (unit / integration / accessibility)
# --------------------------------------------------------------------------- #


@pytest.fixture
def app():
    """Return a Flask app configured for testing with an in-memory SQLite DB."""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    # Push an application context and create schema
    ctx = flask_app.app_context()
    ctx.push()
    db.drop_all()
    db.create_all()
    # make Python's enumerate available in templates used by tests
    flask_app.jinja_env.globals.update({'enumerate': enumerate})

    yield flask_app

    # Teardown
    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_quiz(app):
    """Create and return a simple seeded quiz."""
    sample_questions = [
        {
            'text': 'What is 1 + 1?',
            'choices': ['1', '2', '3', '4'],
            'answer_index': 1
        },
        {
            'text': 'What is the capital of France?',
            'choices': ['Berlin', 'Paris', 'Rome'],
            'answer_index': 1
        }
    ]
    q = Quiz(title='Seeded Quiz', questions_json=json.dumps(sample_questions))
    db.session.add(q)
    db.session.commit()
    return q


# --------------------------------------------------------------------------- #
# Live-server fixtures (E2E / specialized real-HTTP tests)
# --------------------------------------------------------------------------- #

SERVER_SCRIPT = os.path.join(ROOT, "tests", "e2e_server.py")
HOST = "127.0.0.1"


def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="session")
def live_server():
    """Start the real app in a subprocess against an isolated temp DB.

    Used by test_e2e.py and the specialized real-HTTP suites
    (test_security.py, test_a11y_extended.py).
    """
    port = _free_port()
    base_url = f"http://{HOST}:{port}"
    tmp_dir = tempfile.mkdtemp(prefix="quiz_e2e_")
    db_path = os.path.join(tmp_dir, "e2e.db")
    log_path = os.path.join(tmp_dir, "server.log")

    log_file = open(log_path, "w")
    proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT, HOST, str(port), db_path],
        cwd=ROOT,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )

    deadline = time.time() + 30
    last_err = None
    while time.time() < deadline:
        if proc.poll() is not None:
            log_file.flush()
            with open(log_path) as fh:
                raise RuntimeError(
                    f"E2E server exited early (code {proc.returncode}):\n{fh.read()}"
                )
        try:
            if requests.get(base_url + "/", timeout=1).status_code == 200:
                break
        except requests.RequestException as exc:
            last_err = exc
        time.sleep(0.25)
    else:
        proc.terminate()
        log_file.flush()
        with open(log_path) as fh:
            raise RuntimeError(
                f"E2E server did not become ready in time (last error: {last_err}):\n{fh.read()}"
            )

    try:
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        log_file.close()
        shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def http():
    """A fresh HTTP session per test (real cookies/redirects, like a browser)."""
    with requests.Session() as session:
        yield session


@pytest.fixture
def create_quiz(http, live_server):
    """Factory: submit the create form and return the /take URL of the new quiz."""
    from bs4 import BeautifulSoup

    def _create(title, questions):
        resp = http.post(
            live_server + "/create",
            data={"title": title, "questions": json.dumps(questions)},
        )
        assert resp.status_code == 200, resp.text
        soup = BeautifulSoup(resp.text, "html.parser")
        for li in soup.find_all("li"):
            strong = li.find("strong")
            if strong and strong.get_text(strip=True) == title:
                link = li.find("a")
                assert link and link.get("href", "").startswith("/take/")
                return live_server + link["href"]
        raise AssertionError(f"Quiz {title!r} not found on home page:\n{resp.text}")

    return _create
