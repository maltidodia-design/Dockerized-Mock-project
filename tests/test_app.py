import os
import sys
import json

# Ensure project root is on sys.path so tests can import app.py reliably.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app, db, Quiz


def setup_function():
    # use test config
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # create DB within app context
    with app.app_context():
        db.create_all()


def teardown_function():
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_home_empty():
    client = app.test_client()
    r = client.get('/')
    assert r.status_code == 200


def test_create_and_take_quiz():
    client = app.test_client()
    # create quiz
    questions = [
        {'text': '1+1', 'choices': ['1','2'], 'answer_index': 1}
    ]
    r = client.post('/create', data={'title': 'T1', 'questions': json.dumps(questions)}, follow_redirects=True)
    assert r.status_code == 200

    # query the DB within the app context
    with app.app_context():
        quiz = Quiz.query.first()
    assert quiz is not None

    # take quiz with correct answer
    r = client.post(f'/take/{quiz.id}', data={'question-0': '1'})
    assert r.status_code == 200
    assert b'Score' in r.data


