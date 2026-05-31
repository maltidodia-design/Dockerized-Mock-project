"""Specialized security tests.

These run against the real running app (the live-server fixture in
[conftest.py](conftest.py)) so they exercise the actual HTTP / template
rendering / persistence stack a real attacker would interact with.

Scope (per [GOLDEN_PATHS.md](GOLDEN_PATHS.md) and the second-reviewer pass):

* Stored-XSS escaping of user-supplied quiz content (must PASS — Jinja
  autoescape is the only thing protecting us; lock it in so a future
  ``|safe`` filter or HTML export silently re-opens the hole).
* Known security gaps from the second-reviewer pass, deliberately written
  as the test that **should** pass once the gap is closed and marked
  ``xfail`` with a reason until then. Removing the ``xfail`` is part of
  fixing the bug — the test then guards the fix forever.
* Robustness against large payloads.

These tests do NOT attempt to be exhaustive — they cover the items the
Pareto / threat-model analysis ranked highest for this product (an
AI-powered assessment platform potentially used by minors).
"""
import json

import pytest
from bs4 import BeautifulSoup


XSS_PAYLOAD = '<script>alert("xss")</script>'
XSS_ESCAPED_FRAGMENT = '&lt;script&gt;alert('


# --------------------------------------------------------------------------- #
# Stored-XSS — these MUST pass. Jinja autoescape is doing the work; we lock
# the protection in so a future template change can't silently open a hole.
# --------------------------------------------------------------------------- #

def test_stored_xss_in_quiz_title_is_escaped_on_home(live_server, http, create_quiz):
    create_quiz(XSS_PAYLOAD + " title", [
        {"text": "Q1", "choices": ["a", "b"], "answer_index": 0},
    ])
    home = http.get(live_server + "/")
    assert home.status_code == 200
    assert "<script>alert" not in home.text, "Raw <script> tag reached the response — stored XSS"
    assert XSS_ESCAPED_FRAGMENT in home.text, "Title not present escaped — autoescape may be off"


def test_stored_xss_in_question_text_is_escaped_on_take_page(live_server, http, create_quiz):
    take_url = create_quiz("XSS-Q Quiz", [
        {"text": XSS_PAYLOAD, "choices": ["a", "b"], "answer_index": 0},
    ])
    page = http.get(take_url)
    assert page.status_code == 200
    assert "<script>alert" not in page.text
    assert XSS_ESCAPED_FRAGMENT in page.text


def test_stored_xss_in_choice_text_is_escaped_on_take_page(live_server, http, create_quiz):
    take_url = create_quiz("XSS-Choice Quiz", [
        {"text": "Pick one", "choices": [XSS_PAYLOAD, "safe"], "answer_index": 1},
    ])
    page = http.get(take_url)
    assert page.status_code == 200
    assert "<script>alert" not in page.text
    assert XSS_ESCAPED_FRAGMENT in page.text


def test_stored_xss_in_title_is_escaped_on_result_page(live_server, http, create_quiz):
    take_url = create_quiz("XSS-Title Result " + XSS_PAYLOAD, [
        {"text": "Q", "choices": ["a", "b"], "answer_index": 0},
    ])
    result = http.post(take_url, data={"question-0": "0"})
    assert result.status_code == 200
    assert "<script>alert" not in result.text
    assert XSS_ESCAPED_FRAGMENT in result.text


# --------------------------------------------------------------------------- #
# Known gaps — written as tests that SHOULD pass when the gap is closed,
# marked xfail until then. Remove the xfail decorator as part of the fix PR.
# --------------------------------------------------------------------------- #

def test_form_tampering_non_int_answer_is_handled_gracefully(live_server, http, create_quiz):
    """Non-integer answer must NOT 500 — it should be treated as unanswered,
    score reflects that, and the user sees a normal result page."""
    take_url = create_quiz("Tamper Quiz", [
        {"text": "Q", "choices": ["a", "b"], "answer_index": 1},
    ])
    resp = http.post(take_url, data={"question-0": "not-a-number"})
    assert resp.status_code == 200, resp.text
    # Treated as unanswered -> score 0/1 -> a single ❌ on the result page.
    assert "Score: 0 / 1" in resp.text


def test_cross_origin_post_create_is_rejected(live_server, http):
    """Origin-based CSRF mitigation: a POST whose Origin header doesn't match
    the host is rejected before it reaches the handler."""
    resp = http.post(
        live_server + "/create",
        data={"title": "csrf-probe", "questions": json.dumps([])},
        headers={"Origin": "https://evil.example", "Referer": "https://evil.example/"},
    )
    assert resp.status_code in (400, 403), (
        f"Cross-origin POST /create accepted (status {resp.status_code}); "
        "CSRF protection missing."
    )


def test_security_response_headers_present(live_server, http):
    """Baseline security headers must be set on every response."""
    resp = http.get(live_server + "/")
    assert resp.status_code == 200
    headers = {k.lower(): v for k, v in resp.headers.items()}
    missing = [h for h in (
        "x-content-type-options",
        "x-frame-options",
        "content-security-policy",
    ) if h not in headers]
    assert not missing, f"Missing security headers: {missing}"


# --------------------------------------------------------------------------- #
# Robustness — large payload should not 500. Flask's default
# MAX_CONTENT_LENGTH is None (no cap); behaviour should still be graceful.
# --------------------------------------------------------------------------- #

def test_large_quiz_payload_does_not_500(live_server, http):
    big_questions = [
        {"text": f"Question {i}", "choices": ["a", "b", "c", "d"], "answer_index": i % 4}
        for i in range(200)
    ]
    resp = http.post(
        live_server + "/create",
        data={"title": "Big Quiz", "questions": json.dumps(big_questions)},
    )
    assert resp.status_code < 500, f"Large payload caused server error {resp.status_code}"
    home = http.get(live_server + "/")
    assert home.status_code == 200
    soup = BeautifulSoup(home.text, "html.parser")
    assert any(
        s.get_text(strip=True) == "Big Quiz" for s in soup.find_all("strong")
    ), "Big quiz not listed on home page"
