# Validation of Automated E2E Tests

Purpose: record how the automated end-to-end (E2E) tests were validated, what was
actually run, what the results were, and what defect was found while validating.
Written in plain English. Companion to
[VALIDATION_OF_ AUTOMATED_UNIT_TESTS.md](VALIDATION_OF_%20AUTOMATED_UNIT_TESTS.md)
and [GOLDEN_PATHS.md](GOLDEN_PATHS.md).

## Short summary

- A new E2E suite was added: [tests/test_e2e.py](test_e2e.py) (6 tests) plus a
  live-server launcher [tests/e2e_server.py](e2e_server.py).
- Unlike the older tests, these start the **real application as a separate
  process over real HTTP** and drive full user journeys like a browser would.
- All 6 E2E tests **passed**. The full project suite (29 tests) also **passed**.
- While validating, the E2E tests **found a real production bug** that every
  existing test had missed: taking any quiz returned a server error (HTTP 500)
  on the real server. It was fixed and the tests now confirm the fix.
- One honest caveat: these results are from **local runs**. The continuous
  integration (CI) pipeline has **not yet run the new E2E tests** because the
  pull request into `main` has not been opened.

## What was validated

The claim being checked: *"the E2E tests genuinely exercise the real app, are
reliable, are isolated from real data, and pass."*

| # | What we checked | How | Result |
|---|---|---|---|
| 1 | The tests hit the real running app, not the in-process test client | Launcher boots the app with werkzeug and serves over HTTP; tests use `requests` | Confirmed |
| 2 | Each Golden Path journey works end to end | Ran the 6 E2E tests | 6 / 6 passed |
| 3 | The new tests don't break the old ones | Ran the whole `tests/` suite | 29 / 29 passed |
| 4 | E2E run is isolated from real data | Launcher points the database at a throwaway temp file | `instance/data.db` untouched |
| 5 | Tests are repeatable, not flaky | Ran the suite multiple times (alone and with full suite, and as the two separate CI steps) | Stable, same result every time |
| 6 | The tests can actually catch a real failure | A genuine production bug surfaced during validation | Bug found, fixed, re-verified |

## How validation was performed

**Environment (local):** macOS, project virtual environment `.venv`,
Python 3.9.6, pytest 8.4.2, with `requests` and `beautifulsoup4` already in
[requirements.txt](../requirements.txt). The CI pipeline uses Python 3.10.

**Commands run and what was observed:**

1. **Reproduce the suspected real-app problem** (before any fix) — rendered
   `GET /take/<id>` through the real app without the test-only helper that
   `conftest.py` injects:
   - Observed: **HTTP 500**, exact error `UndefinedError: 'enumerate' is undefined`.

2. **Run the E2E suite alone:** `pytest tests/test_e2e.py -v`
   - Observed: **6 passed** in ~0.5s.

   | Test | Golden Path | Result |
   |---|---|---|
   | `test_e2e_home_page_renders_and_is_navigable` | GP-1 entry / GR | PASSED |
   | `test_e2e_full_quiz_journey_all_correct` | GP-1, GP-4 | PASSED |
   | `test_e2e_quiz_journey_with_wrong_answer_shows_feedback` | GP-2, GP-3 | PASSED |
   | `test_e2e_unknown_quiz_id_returns_404` | GR-1 | PASSED |
   | `test_e2e_invalid_questions_json_returns_400` | GR-2 | PASSED |
   | `test_e2e_ai_feedback_api_over_http` | GP-3 | PASSED |

3. **Run the entire project suite:** `pytest tests/`
   - Observed: **29 passed**, 13 warnings, ~0.6s (23 existing + 6 new E2E). No
     regressions in the unit / integration / accessibility tests.

4. **Run exactly as the CI pipeline will run it** (two separate steps from
   [.github/workflows/ci.yml](../.github/workflows/ci.yml)):
   - `pytest tests/ --ignore=tests/test_e2e.py -v` → **23 passed**.
   - `pytest tests/test_e2e.py -v` → **6 passed**.
   - This confirms the split CI steps behave correctly and the E2E step is
     reported on its own.

## Defect found during validation (key finding)

The most important validation outcome was **not** that the tests passed — it was
that they caught a real bug the older tests structurally could not:

- **Symptom:** On the real server (`gunicorn` / `python app.py`, i.e. how the app
  runs in Docker), opening any quiz to take it returned **HTTP 500**.
- **Cause:** [templates/take_quiz.html](../templates/take_quiz.html) uses
  `enumerate()`, which the template engine does not provide by default.
- **Why nobody noticed:** the existing unit/integration tests passed only because
  [tests/conftest.py](conftest.py) quietly adds `enumerate` for tests — code that
  never runs on the real server. The test suite was green while a core Golden
  Path (take a quiz) was completely broken in production.
- **Fix:** registered the missing global in [app.py](../app.py).
- **Re-verification:** E2E-002 and E2E-003, which open the take page over real
  HTTP, now pass — proving both that the bug existed and that the fix works.

This is the central evidence that the E2E layer adds real protection: it tests
the same path a user hits, so it sees failures the in-process tests cannot.

## Test quality checks

- **Isolation:** the launcher uses a temporary SQLite database in a temp folder;
  the project's real `instance/data.db` is never read or written by E2E runs.
- **Self-contained:** the test fixture starts the server, waits until it actually
  answers, yields the URL, then shuts the server down and deletes the temp files.
- **Deterministic:** each test creates its own uniquely-named quiz and asserts on
  that specific quiz, so tests do not interfere even though they share one server
  for speed.
- **Failure visibility:** if the server fails to start, the fixture fails loudly
  with the captured server log instead of hanging or giving a vague error.
- **No new dependencies:** uses libraries already declared in
  [requirements.txt](../requirements.txt), so CI needs no extra setup.

## Limitations / what was NOT validated

1. **CI has not yet executed these tests.** All results above are local. The
   historical CI log still shows the old 23-test run; the new E2E tests will only
   run in CI once the pull request into `main` is opened.
2. **No real browser / JavaScript.** The tests drive real HTTP and parse real
   HTML, but do not run a browser engine. Client-side behaviour and visual
   layout are out of scope (consistent with [TEST_PLAN.md](TEST_PLAN.md), which
   defers cross-browser E2E).
3. **AI feedback is a stub.** GP-3 validates the deterministic mock in
   [app.py](../app.py). A real AI model would need separate contract / UX tests
   for non-deterministic output.
4. **Single-process only.** Concurrency and load (many simultaneous quiz-takers)
   were not validated.
5. **Python version drift.** Validated locally on Python 3.9; CI runs Python
   3.10. No version-specific issues are expected, but this is only fully
   confirmed once CI runs.

## Conclusion

The automated E2E tests were validated by direct execution and judged
**fit for purpose**: they run against the real app over real HTTP, cover the
product's Golden Paths and guardrails, are isolated and repeatable, and have
already proven their value by catching a production-only defect that the existing
suite missed. The one open item is running them in CI, which happens
automatically once the pull request into `main` is opened.

| Item | Status |
|---|---|
| E2E tests pass locally (6/6) | ✅ |
| Full suite passes (29/29) | ✅ |
| Runs isolated from real data | ✅ |
| Real production bug found & fixed | ✅ |
| Verified as the two CI steps will run | ✅ |
| Executed by CI pipeline | ⏳ Pending PR into `main` |
