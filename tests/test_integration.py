import json
import pytest

def test_quiz_creation_and_take_flow(client, app):
    # Create a quiz
    questions = [
        {'text': 'What is 5 + 5?', 'choices': ['8', '9', '10', '11'], 'answer_index': 2}
    ]
    resp = client.post('/create', data={'title': 'Integration Quiz', 'questions': json.dumps(questions)}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Integration Quiz' in resp.data

    # Find the quiz in the DB
    from app import Quiz
    quiz = Quiz.query.filter_by(title='Integration Quiz').first()
    assert quiz is not None

    # Take the quiz (GET)
    resp = client.get(f'/take/{quiz.id}')
    assert resp.status_code == 200
    assert b'What is 5 + 5?' in resp.data

    # Take the quiz (POST, correct answer)
    resp = client.post(f'/take/{quiz.id}', data={'question-0': '2'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'score' in resp.data or b'Score' in resp.data
    assert b'Integration Quiz' in resp.data

    # Check AI feedback endpoint
    details = [{'index': 0, 'given': 2, 'expected': 2, 'ok': True}]
    feedback = client.post('/api/ai_feedback', json={'quiz_id': quiz.id, 'details': details})
    assert feedback.status_code == 200
    data = feedback.get_json()
    assert 'recommendations' in data
