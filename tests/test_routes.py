import json
from app import Quiz, Result


def test_index_shows_links(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Create a new quiz" in rv.data
    assert b"Available quizzes" in rv.data


def test_create_quiz_happy_path(client):
    questions = [
        {'text': 'What is 2 + 2?', 'choices': ['1', '2', '3', '4'], 'answer_index': 3}
    ]
    resp = client.post('/create', data={'title': 'Test Quiz', 'questions': json.dumps(questions)}, follow_redirects=True)
    assert resp.status_code == 200
    # index page should now list the new quiz
    assert b'Test Quiz' in resp.data

    # verify DB record
    q = Quiz.query.filter_by(title='Test Quiz').first()
    assert q is not None
    parsed = q.questions()
    assert isinstance(parsed, list) and parsed[0]['text'] == 'What is 2 + 2?'


def test_create_quiz_validation(client):
    # invalid JSON for questions should return 400
    resp = client.post('/create', data={'title': 'Bad Quiz', 'questions': 'not a json'})
    assert resp.status_code == 400
    assert b'Invalid questions JSON' in resp.data


def test_take_quiz_flow(client, sample_quiz):
    # GET the take page
    resp = client.get(f'/take/{sample_quiz.id}')
    assert resp.status_code == 200
    assert b'Seeded Quiz' in resp.data
    assert b'What is 1 + 1?' in resp.data

    # Submit answers: answer index 1 for first question, 1 for second -> both correct
    post_data = {
        'question-0': '1',
        'question-1': '1'
    }
    resp2 = client.post(f'/take/{sample_quiz.id}', data=post_data, follow_redirects=True)
    assert resp2.status_code == 200
    assert b'Score:' in resp2.data
    assert b'Result for:' in resp2.data

    # verify a Result row was created
    r = Result.query.filter_by(quiz_id=sample_quiz.id).first()
    assert r is not None
    assert r.total == 2
    assert r.score == 2
