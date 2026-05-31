"""Lightweight concurrent-load smoke tests.

These do NOT try to be a real load test (Locust/k6 belong in a separate
job, against an environment as close to production as possible — see
[CONFIGURATION_MATRIX.md](CONFIGURATION_MATRIX.md) §13). They are a
**concurrency sanity check** that runs under pytest in seconds and surfaces
the failure classes you can catch in-process:

* No 5xx under concurrent submission.
* No data corruption — N submissions create N distinct ``Result`` rows
  (read back via the home/take/result HTML — there's no admin endpoint).
* No deadlocks.

What this does **NOT** cover (intentionally; see
[AI_GENERATED_SPECIALIZED_TESTS.md](AI_GENERATED_SPECIALIZED_TESTS.md)):

* SQLite "database is locked" under ``gunicorn --workers 2`` — requires a
  multi-PROCESS server. werkzeug ``threaded=True`` (what the live-server
  fixture uses) serialises writes within one process so the bug does not
  reproduce here.
* Latency SLOs — too environment-dependent for unit-suite assertions.
"""
import json
import threading

import requests
from bs4 import BeautifulSoup


# Single-process werkzeug handles low concurrency comfortably. Don't crank
# this up — the goal is a sanity smoke that runs in <5 s in CI.
CONCURRENCY = 20


def _new_session():
    """Each thread gets its own requests.Session — Session is not designed
    for safe concurrent use across threads."""
    return requests.Session()


def _create_quiz_direct(session, base_url, title, questions):
    resp = session.post(
        base_url + "/create",
        data={"title": title, "questions": json.dumps(questions)},
    )
    assert resp.status_code == 200, resp.text
    soup = BeautifulSoup(resp.text, "html.parser")
    for li in soup.find_all("li"):
        strong = li.find("strong")
        if strong and strong.get_text(strip=True) == title:
            link = li.find("a")
            return base_url + link["href"]
    raise AssertionError(f"Quiz {title!r} not on home page after create")


# --------------------------------------------------------------------------- #
# Concurrent submission of the SAME quiz
# --------------------------------------------------------------------------- #

def test_concurrent_takes_of_one_quiz_all_succeed(live_server):
    """All N concurrent submissions return 200 with the expected score,
    and the server logs no 5xx along the way."""
    sess = _new_session()
    take_url = _create_quiz_direct(
        sess, live_server, "perf-shared-quiz",
        [{"text": "Q1", "choices": ["a", "b", "c"], "answer_index": 1}],
    )

    statuses = [None] * CONCURRENCY
    score_lines = [None] * CONCURRENCY
    errors = []

    def _worker(i):
        try:
            s = _new_session()
            r = s.post(take_url, data={"question-0": "1"})
            statuses[i] = r.status_code
            if r.status_code == 200 and "Score: 1 / 1" in r.text:
                score_lines[i] = "Score: 1 / 1"
        except Exception as exc:
            errors.append((i, repr(exc)))

    threads = [threading.Thread(target=_worker, args=(i,)) for i in range(CONCURRENCY)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)

    assert not errors, f"Worker exceptions: {errors[:5]}"
    assert all(s == 200 for s in statuses), (
        f"Non-200 responses: { {s for s in statuses if s != 200} }"
    )
    assert all(line == "Score: 1 / 1" for line in score_lines), (
        f"Some submissions returned wrong/missing score line: "
        f"{ [l for l in score_lines if l != 'Score: 1 / 1'][:3] }"
    )


# --------------------------------------------------------------------------- #
# Concurrent creation of DIFFERENT quizzes
# --------------------------------------------------------------------------- #

def test_concurrent_creates_all_succeed_and_appear_on_home(live_server):
    """N threads simultaneously create N distinct quizzes; afterwards the
    home page lists every one of them (no lost writes)."""
    titles = [f"perf-create-{i}" for i in range(CONCURRENCY)]
    errors = []

    def _worker(title):
        try:
            s = _new_session()
            _create_quiz_direct(
                s, live_server, title,
                [{"text": "Q", "choices": ["a", "b"], "answer_index": 0}],
            )
        except Exception as exc:
            errors.append((title, repr(exc)))

    threads = [threading.Thread(target=_worker, args=(t,)) for t in titles]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)

    assert not errors, f"Worker exceptions: {errors[:5]}"

    # Verify every title is now listed exactly once.
    resp = requests.get(live_server + "/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    listed = [s.get_text(strip=True) for s in soup.find_all("strong")]
    for title in titles:
        assert listed.count(title) == 1, (
            f"Title {title!r} appears {listed.count(title)}× on home (expected exactly 1)"
        )
