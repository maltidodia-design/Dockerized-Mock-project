import json
import pytest

from app import Quiz, Result, db


def test_take_invalid_quiz_id_get_404(client):
    resp = client.get('/take/99999')
    assert resp.status_code == 404


def test_take_invalid_quiz_id_post_404(client):
    resp = client.post('/take/99999', data={})
    assert resp.status_code == 404


def test_create_quiz_no_title_defaults(client):
    questions = []
    resp = client.post('/create', data={'questions': json.dumps(questions)}, follow_redirects=True)
    assert resp.status_code == 200
    # Should create an "Untitled Quiz"
    q = Quiz.query.filter_by(title='Untitled Quiz').first()
    assert q is not None


def test_create_quiz_empty_questions(client):
    questions = []
    resp = client.post('/create', data={'title': 'Empty Questions', 'questions': json.dumps(questions)}, follow_redirects=True)
    assert resp.status_code == 200
    q = Quiz.query.filter_by(title='Empty Questions').first()
    assert q is not None
    assert q.questions() == []


def test_take_quiz_partial_answers(client, sample_quiz):
    # Answer only the first question correctly
    post_data = {
        'question-0': '1'
        # question-1 omitted
    }
    resp = client.post(f'/take/{sample_quiz.id}', data=post_data, follow_redirects=True)
    assert resp.status_code == 200
    # The result page should show Score and a Result row should be created
    assert b'Score:' in resp.data
    r = Result.query.filter_by(quiz_id=sample_quiz.id).first()
    assert r is not None
    assert r.total == 2
    assert r.score == 1


def test_take_quiz_non_int_answer_raises(client, sample_quiz):
    # Submitting a non-integer value will raise ValueError when casting to int
    with pytest.raises(ValueError):
        client.post(f'/take/{sample_quiz.id}', data={'question-0': 'a', 'question-1': '1'})


def test_db_commit_failure_on_create_quiz_raises(monkeypatch, client):
    # simulate DB commit failure
    def fail_commit():
        raise Exception("DB commit failed")

    monkeypatch.setattr(db.session, 'commit', fail_commit)
    questions = [{'text': 'x', 'choices': ['a'], 'answer_index': 0}]
    with pytest.raises(Exception):
        client.post('/create', data={'title': 'Will Fail', 'questions': json.dumps(questions)})


def test_api_ai_feedback_handles_empty_details(client):
    resp = client.post('/api/ai_feedback', json={'details': []})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'recommendations' in data
    assert data['recommendations'] == ['practice_more']

