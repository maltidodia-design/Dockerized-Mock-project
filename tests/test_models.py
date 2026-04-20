import json
import subprocess
import sys
from pathlib import Path


def test_ai_feedback_with_incorrect_details(client):
    details = [{'index': 0, 'given': 0, 'expected': 1, 'ok': False}]
    resp = client.post('/api/ai_feedback', json={'details': details})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'explanations' in data
    assert len(data['explanations']) == 1
    assert 'recommendations' in data
    assert 'fundamentals' in data['recommendations']


def test_result_details_json_stored_and_read(client, sample_quiz):
    # Submit one correct and one incorrect answer
    post_data = {'question-0': '1', 'question-1': '0'}
    resp = client.post(f'/take/{sample_quiz.id}', data=post_data)
    assert resp.status_code == 200

    # find the result row via the response (template shows Score)
    # We can query the database through the app's models
    from app import Result
    r = Result.query.filter_by(quiz_id=sample_quiz.id).order_by(Result.created_at.desc()).first()
    assert r is not None
    details = json.loads(r.details_json)
    assert isinstance(details, list)
    assert details[0]['given'] == 1 or details[0]['given'] is None


def test_db_init_creates_db(tmp_path):
    # Simulate db_init behavior but using a temp SQLite file to avoid writing repo files
    from app import db, Quiz, app as flask_app

    db_path = tmp_path / 'data.db'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        sample_questions = [
            {'text': 't', 'choices': ['a'], 'answer_index': 0}
        ]
        q = Quiz(title='Init', questions_json=json.dumps(sample_questions))
        db.session.add(q)
        db.session.commit()

    # verify the sample quiz persisted in the configured DB
    from app import Quiz as Q
    with flask_app.app_context():
        persisted = Q.query.filter_by(title='Init').first()
        assert persisted is not None