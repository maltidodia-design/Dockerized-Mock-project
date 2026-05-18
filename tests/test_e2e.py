"""End-to-end (E2E) tests.

These differ from the unit/integration suites: instead of Flask's in-process
test client, they boot the *real* application as a separate process serving
over real HTTP, then drive complete user journeys with `requests` +
BeautifulSoup — the same way a browser/user would (follow links, submit the
rendered forms, read the resulting pages).

Covered journeys (E2E flavour of the TEST_PLAN cases):

* E2E-001 Home page renders and is navigable
* E2E-002 Full happy path: create -> listed on home -> take -> all correct -> result
* E2E-003 Mixed answers: partial score + AI feedback explanations shown
* E2E-004 Unknown quiz id -> 404
* E2E-005 Invalid questions JSON on create -> 400
* E2E-006 AI feedback JSON API reachable over real HTTP
"""
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import shutil

import pytest
import requests
from bs4 import BeautifulSoup

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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

    Yields the base URL. The server is shut down and the temp DB removed on
    teardown.
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

    # Wait until the server answers, or fail with the captured server log.
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
        except requests.RequestException as exc:  # not up yet
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


def _create_quiz(http, base_url, title, questions):
    """Submit the create form and return the new quiz's /take URL.

    Mirrors what a user does: post the form, land back on the home page,
    then click that quiz's "Take quiz" link.
    """
    resp = http.post(
        base_url + "/create",
        data={"title": title, "questions": json.dumps(questions)},
    )
    assert resp.status_code == 200, resp.text
    # After the redirect we should be on the home page listing the new quiz.
    soup = BeautifulSoup(resp.text, "html.parser")
    for li in soup.find_all("li"):
        strong = li.find("strong")
        if strong and strong.get_text(strip=True) == title:
            link = li.find("a")
            assert link and link.get("href", "").startswith("/take/")
            return base_url + link["href"]
    raise AssertionError(f"Quiz {title!r} not found on home page:\n{resp.text}")


# --------------------------------------------------------------------------- #
# E2E-001
# --------------------------------------------------------------------------- #
def test_e2e_home_page_renders_and_is_navigable(live_server, http):
    resp = http.get(live_server + "/")
    assert resp.status_code == 200

    soup = BeautifulSoup(resp.text, "html.parser")
    assert soup.find("h1") is not None
    assert "Available quizzes" in resp.text
    # The "Create a new quiz" link must point at the working /create route.
    create_link = soup.find("a", href="/create")
    assert create_link is not None
    assert http.get(live_server + create_link["href"]).status_code == 200


# --------------------------------------------------------------------------- #
# E2E-002 — full happy path, all answers correct
# --------------------------------------------------------------------------- #
def test_e2e_full_quiz_journey_all_correct(live_server, http):
    questions = [
        {"text": "What is 2 + 2?", "choices": ["1", "2", "3", "4"], "answer_index": 3},
        {"text": "Capital of France?", "choices": ["Berlin", "Paris", "Rome"], "answer_index": 1},
    ]
    take_url = _create_quiz(http, live_server, "E2E All Correct Quiz", questions)

    # GET the take page — this is the exact path that returned HTTP 500 before
    # the enumerate() Jinja fix; E2E catches what the test-client suite masked.
    page = http.get(take_url)
    assert page.status_code == 200, page.text
    soup = BeautifulSoup(page.text, "html.parser")
    assert "What is 2 + 2?" in page.text
    assert "Capital of France?" in page.text
    # Every question must render a radio group.
    for i in range(len(questions)):
        assert soup.find("input", attrs={"name": f"question-{i}"}) is not None

    # Submit all correct answers.
    result = http.post(
        take_url, data={"question-0": "3", "question-1": "1"}
    )
    assert result.status_code == 200
    assert "Result for: E2E All Correct Quiz" in result.text
    assert "Score: 2 / 2" in result.text
    assert "✅" in result.text          # ✅ for the correct answers
    assert "❌" not in result.text      # no ❌
    # All correct -> stub returns no explanations -> template's empty state.
    assert "No feedback available." in result.text


# --------------------------------------------------------------------------- #
# E2E-003 — mixed answers, partial score, AI feedback explanations
# --------------------------------------------------------------------------- #
def test_e2e_quiz_journey_with_wrong_answer_shows_feedback(live_server, http):
    questions = [
        {"text": "2 + 3 = ?", "choices": ["4", "5", "6"], "answer_index": 1},
        {"text": "Sky colour?", "choices": ["Blue", "Green"], "answer_index": 0},
    ]
    take_url = _create_quiz(http, live_server, "E2E Mixed Quiz", questions)

    assert http.get(take_url).status_code == 200

    # First correct, second wrong.
    result = http.post(
        take_url, data={"question-0": "1", "question-1": "1"}
    )
    assert result.status_code == 200
    assert "Score: 1 / 2" in result.text
    assert "✅" in result.text   # the correct one
    assert "❌" in result.text   # the wrong one
    # The AI feedback stub should produce an explanation for the wrong answer.
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
