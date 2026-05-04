# Test Strategy — Flask Quiz App

> Location: `tests/TEST_STRATEGY.md`

## Overview
This document captures the test strategy for the Flask quiz application in this repository. It is intended to be a living reference for developers and CI. The goals are correctness, accessibility (508), maintainability, and safe deployment.

## High-level goals
- Verify core functionality: quiz creation, taking quizzes, result calculation, and database operations.
- Detect regressions quickly with fast unit and integration tests.
- Ensure primary pages meet automated accessibility checks (508/a11y) and identify items for manual review.
- Enforce code quality via linting and (optionally) type checking.

## Acceptance criteria
- Unit + integration tests pass on every PR.
- Coverage >= 85% for backend Python code (configurable).
- No critical/serious automated accessibility violations on main pages (index, create_quiz, take_quiz, result).
- Lint passes (flake8) and no high-severity dependency vulnerabilities (pip-audit / safety).

## Scope
- Files in scope: `app.py`, `models.py`, `db_init.py`, templates in `templates/`, and critical static assets that affect accessibility.
- Out of scope for now: full E2E cross-browser tests, performance tests, and manual 508 audits (these are recommended later).

## Test types and recommended tools
- Unit tests
  - Purpose: test small helpers, pure functions, and model helper functions.
  - Tool: pytest.
- Integration tests
  - Purpose: test Flask routes using the Flask test client, DB interactions, and end-to-end request flows (create -> take -> result).
  - Tool: pytest with Flask test client. Use in-memory or temporary SQLite DB for isolation.
- Accessibility tests (automated)
  - Purpose: detect common 508 issues: missing labels, ARIA issues, color contrast, semantic structure.
  - Tools: axe-core via `axe-selenium-python`, or `pa11y` for a lightweight CLI scan. For CI, headless Chrome + axe is recommended.
- Static analysis and security
  - Lint: `flake8` (or `pylint` if preferred)
  - Type checking (optional): `mypy`
  - Dependency security: `pip-audit` or `safety`
- Coverage
  - Tool: `coverage.py` to enforce coverage thresholds in CI.

## Mapping tests to repository files
- `app.py` — tests: app creation, configuration, register blueprints/routes, basic route responses.
- `models.py` — tests: CRUD helpers, query logic, and any data transformation functions.
- `db_init.py` — tests: DB schema creation against a temporary DB file.
- `templates/*.html` — tests: ensure rendered templates contain required elements (labels, headings) and pass automated a11y checks.
- `static/` (CSS) — not directly unit-tested, but included in a11y scans affecting contrast/visibility.

## Test design
Contract (concise)
- Inputs: HTTP requests, form data, DB seeded rows.
- Outputs: HTTP status codes, rendered HTML content, DB side-effects (records created/updated), redirect behavior.
- Error modes: missing/invalid form data, invalid IDs, DB errors.

Fixtures to add (pytest)
- `app` fixture: a Flask app configured for testing (`TESTING=True`) and pointing to an in-memory or temporary SQLite DB.
- `client` fixture: a Flask test client.
- `db` fixture: creates schema and tears it down per test (or per-module, depending on speed).
- `sample_quiz` fixture: seeds a simple quiz for the take-quiz flow.

Edge cases to cover
- Empty form submissions and validation messages.
- Invalid quiz IDs => 404 handling.
- Templates rendered with missing optional context.
- Database unavailable/read-only (simulate) and graceful error handling.

## Concrete test cases (examples)
1. Home page
   - GET `/` => status 200, contains "Create Quiz" and "Take Quiz" links.
2. Create quiz — happy path
   - POST `/create` with valid data => redirect (or success) and DB contains new quiz.
3. Create quiz — validation
   - POST `/create` with missing required fields => form re-rendered with error messages.
4. Take quiz flow
   - GET `/take/<quiz_id>` => status 200, contains expected questions.
   - POST answers => correct result calculation and display.
5. DB initialization
   - Run `db_init.py` against a temp path => DB file created with expected tables.
6. Accessibility checks
   - Run axe scan for each main page; assert no critical/serious violations.

## Example pytest snippet (place in `tests/test_routes.py` or expand `tests/test_app.py`)

```python
def test_home_shows_links(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Create Quiz" in rv.data
    assert b"Take Quiz" in rv.data
```

## CI recommendations (GitHub Actions example)
Trigger: run on PRs and pushes to `main`.
Jobs:
- Setup Python, install dependencies from `requirements.txt`.
- Run lint (`flake8`).
- Run tests with coverage: `coverage run -m pytest` and `coverage report --fail-under=85`.
- Run accessibility scan (headless Chrome + axe) against the running app (or the HTML output from test client).
- Run dependency audit: `pip-audit` or `safety check`.

Notes on a11y in CI
- Running axe requires a headless browser. Use a job that installs Chrome/Chromium, starts the app (or serves the built HTML) and runs axe scans.
- Alternatively, use `pa11y-ci` (Node) for a faster, lighter scan of static pages.

## Test data & environment setup
- For tests, prefer sqlite in-memory or a temporary file under pytest's `tmp_path` fixture.
- Ensure tests set `FLASK_ENV`/config appropriately (e.g., `TESTING=True`, `WTF_CSRF_ENABLED=False` if using Flask-WTF to simplify form posts).

## How to run tests locally (zsh)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
coverage run -m pytest
coverage report --fail-under=85
flake8
```

## Accessibility (508) checklist (automated + manual)
Automated checks (use axe/pa11y):
- form controls have associated labels
- buttons/links have accessible names
- proper heading order and presence of main heading (`h1`)
- no duplicate IDs
- color contrast for key text/background combinations

Manual checks (recommended):
- Keyboard navigation: tab order, focus visibility
- Screen reader review (VoiceOver, NVDA)
- Logical flow and semantics (landmarks, headings)

## Maintenance & ownership
- Put tests under `tests/` with descriptive filenames: `test_routes.py`, `test_models.py`, `test_accessibility.py`.
- Require tests and updates when behavior changes.
- Run accessibility checks regularly (weekly) and on major UI PRs.

## Risks & mitigations
- Automated a11y tools miss context-specific 508 issues: schedule periodic manual audits.
- DB state leakage: use isolated DB fixtures per test.
- Slow E2E tests: keep them minimal in PR CI and run full suites nightly.

## Next steps (I can implement these for you)
- Add pytest fixtures (`app`, `client`, `db`) and a small set of unit+integration tests.
- Add an automated axe-based accessibility test.
- Scaffold a GitHub Actions CI workflow running lint/tests/coverage/a11y.

---


