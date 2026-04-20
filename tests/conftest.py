import json
import os
import sys
import pytest

# Ensure project root is on sys.path so tests can import app.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app as flask_app, db, Quiz

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
