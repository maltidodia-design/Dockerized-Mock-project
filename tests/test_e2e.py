"""End-to-end (E2E) tests.

These differ from the unit/integration suites: instead of Flask's in-process
test client, they boot the *real* application as a separate process serving
over real HTTP, then drive complete user journeys with `requests` +
BeautifulSoup — the same way a browser/user would (follow links, submit the
rendered forms, read the resulting pages).

Live-server fixtures (`live_server`, `http`, `create_quiz`) are defined in
[tests/conftest.py](conftest.py) so the specialised suites
(`test_security.py`, `test_a11y_extended.py`) can reuse them.

Covered journeys (E2E flavour of the TEST_PLAN cases):

* E2E-001 Home page renders and is navigable
* E2E-002 Full happy path: create -> listed on home -> take -> all correct -> result
* E2E-003 Mixed answers: partial score + AI feedback explanations shown
* E2E-004 Unknown quiz id -> 404
* E2E-005 Invalid questions JSON on create -> 400
* E2E-006 AI feedback JSON API reachable over real HTTP
"""
from bs4 import BeautifulSoup


# --------------------------------------------------------------------------- #
# E2E-001
# --------------------------------------------------------------------------- #
def test_e2e_home_page_renders_and_is_navigable(live_server, http):
    resp = http.get(live_server + "/")
    assert resp.status_code == 200

    soup = BeautifulSoup(resp.text, "html.parser")
    assert soup.find("h1") is not None
    assert "Available quizzes" in resp.text
    create_link = soup.find("a", href="/create")
    assert create_link is not None
    assert http.get(live_server + create_link["href"]).status_code == 200


# --------------------------------------------------------------------------- #
# E2E-002 — full happy path, all answers correct
# --------------------------------------------------------------------------- #
def test_e2e_full_quiz_journey_all_correct(live_server, http, create_quiz):
    questions = [
        {"text": "What is 2 + 2?", "choices": ["1", "2", "3", "4"], "answer_index": 3},
        {"text": "Capital of France?", "choices": ["Berlin", "Paris", "Rome"], "answer_index": 1},
    ]
    take_url = create_quiz("E2E All Correct Quiz", questions)

    # GET the take page — this is the exact path that returned HTTP 500 before
    # the enumerate() Jinja fix; E2E catches what the test-client suite masked.
    page = http.get(take_url)
    assert page.status_code == 200, page.text
    soup = BeautifulSoup(page.text, "html.parser")
    assert "What is 2 + 2?" in page.text
    assert "Capital of France?" in page.text
    for i in range(len(questions)):
        assert soup.find("input", attrs={"name": f"question-{i}"}) is not None

    result = http.post(take_url, data={"question-0": "3", "question-1": "1"})
    assert result.status_code == 200
    assert "Result for: E2E All Correct Quiz" in result.text
    assert "Score: 2 / 2" in result.text
    assert "✅" in result.text
    assert "❌" not in result.text
    assert "No feedback available." in result.text


# --------------------------------------------------------------------------- #
# E2E-003 — mixed answers, partial score, AI feedback explanations
# --------------------------------------------------------------------------- #
def test_e2e_quiz_journey_with_wrong_answer_shows_feedback(live_server, http, create_quiz):
    questions = [
        {"text": "2 + 3 = ?", "choices": ["4", "5", "6"], "answer_index": 1},
        {"text": "Sky colour?", "choices": ["Blue", "Green"], "answer_index": 0},
    ]
    take_url = create_quiz("E2E Mixed Quiz", questions)

    assert http.get(take_url).status_code == 200

    result = http.post(take_url, data={"question-0": "1", "question-1": "1"})
    assert result.status_code == 200
    assert "Score: 1 / 2" in result.text
    assert "✅" in result.text
    assert "❌" in result.text
    assert "AI Feedback" in result.text
    assert "Review question" in result.text


# --------------------------------------------------------------------------- #
# E2E-004 — unknown quiz id
# --------------------------------------------------------------------------- #
def test_e2e_unknown_quiz_id_returns_404(live_server, http):
    assert http.get(live_server + "/take/999999").status_code == 404
    assert http.post(live_server + "/take/999999", data={}).status_code == 404


# --------------------------------------------------------------------------- #
# E2E-005 — invalid questions JSON
# --------------------------------------------------------------------------- #
def test_e2e_invalid_questions_json_returns_400(live_server, http):
    resp = http.post(
        live_server + "/create",
        data={"title": "Broken", "questions": "not valid json"},
    )
    assert resp.status_code == 400
    assert "Invalid questions JSON" in resp.text


# --------------------------------------------------------------------------- #
# E2E-007 — /healthz liveness probe
# --------------------------------------------------------------------------- #
def test_e2e_healthz_endpoint(live_server, http):
    """Health endpoint must respond 200 with a static JSON body and must not
    touch the database (so it's safe for orchestrator liveness probes)."""
    resp = http.get(live_server + "/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# --------------------------------------------------------------------------- #
# E2E-006 — AI feedback API over real HTTP
# --------------------------------------------------------------------------- #
def test_e2e_ai_feedback_api_over_http(live_server, http):
    resp = http.post(
        live_server + "/api/ai_feedback",
        json={
            "quiz_id": 1,
            "details": [{"index": 0, "given": 0, "expected": 1, "ok": False}],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["explanations"], data
    assert "fundamentals" in data["recommendations"]
