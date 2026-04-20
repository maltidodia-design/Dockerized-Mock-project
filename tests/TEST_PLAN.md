# Test Plan — Flask Quiz App

Location: `tests/TEST_PLAN.md`

## Purpose
This Test Plan documents the testing approach, scope, schedule, responsibilities, and acceptance criteria for the Flask Quiz App in this repository. It is derived from `tests/TEST_STRATEGY.md` and provides actionable test items, traceability, and a prioritized list of test cases to execute during development and CI.

## Objectives
- Validate core functionality: quiz creation, quiz-taking flow, and result calculation.
- Ensure DB schema and CRUD operations behave correctly and safely under test conditions.
- Detect regressions early via unit and integration tests.
- Automate accessibility (508) checks for the main user-facing pages and identify items for manual review.
- Enforce code quality gates (lint, coverage) in CI.

## Scope
In-scope:
- `app.py` (routes and app factory)
- `models.py` (data model helpers and DB access)
- `db_init.py` (schema creation)
- Templates: `templates/index.html`, `templates/create_quiz.html`, `templates/take_quiz.html`, `templates/result.html`
- Tests and test harness in `tests/`

Out-of-scope (initial):
- Cross-browser end-to-end tests (deferred to next phase)
- Performance and load testing
- Full manual 508 audits (recommended as periodic activity)

## Test Items (Features to Test)
- Home page rendering and navigation
- Create quiz form: validation, persistence, redirect behavior
- Take quiz: question rendering, answer submission, scoring logic, result display
- Database initialization and migration (`db_init.py`)
- Error handling for invalid quiz IDs and malformed inputs
- Accessibility checks for the main pages (automated scans)
- Linting and dependency checks

## Test Approach
- Unit tests (pytest): small units in `models.py` and helper functions.
- Integration tests (pytest + Flask test client): route behaviors, DB interactions, and end-to-end flows.
- Accessibility tests (automated): run axe/pa11y scans against rendered HTML in tests or headless browser.
- CI validations: lint (flake8), tests with coverage (coverage.py), and pip-audit/safety for dependencies.

## Test Environment
- Local development: Python 3.8+ (match project's version); virtualenv recommended.
- Test DB: in-memory SQLite or temporary file (controlled by pytest fixtures).
- CI: GitHub Actions (recommended) with job(s) to run lint/tests/coverage and an a11y job that uses headless Chrome + axe.

## Test Data and Fixtures
- Fixtures to add in `tests/`:
  - `app` fixture: configured Flask app for testing (TESTING=True, use test DB)
  - `client` fixture: Flask test client
  - `db` fixture: create/drop schema per test module or function
  - `sample_quiz` fixture: seed a minimal quiz with 1–3 questions

## Test Case Suite (Prioritized)
Each test case should be implemented as a pytest unit/integration test in `tests/` with clear IDs.

1. TP-001: Home page content
   - Type: Integration
   - Steps: GET `/`
   - Expected: 200, contains "Create Quiz" and "Take Quiz"
   - Files: `app.py`, `templates/index.html`

2. TP-002: Create quiz — happy path
   - Type: Integration
   - Steps: POST `/create` with valid form data
   - Expected: redirect or success, DB contains record
   - Files: `app.py`, `models.py`, `templates/create_quiz.html`

3. TP-003: Create quiz — validation
   - Type: Integration
   - Steps: POST `/create` with missing required fields
   - Expected: form re-render with error message, no DB record

4. TP-004: Take quiz render
   - Type: Integration
   - Steps: GET `/take/<quiz_id>` for seeded quiz
   - Expected: 200, displays questions and accessible form controls

5. TP-005: Take quiz submit and result
   - Type: Integration
   - Steps: POST answers -> expect scoring and result page with correct score
   - Expected: result calculation matches expected output

6. TP-006: DB init
   - Type: Unit/Integration
   - Steps: run `db_init.py` against tmp path
   - Expected: DB file created with expected tables

7. TP-007: Accessibility scan — main pages
   - Type: Automated a11y
   - Steps: render pages and run axe scan
   - Expected: no critical/serious violations

8. TP-008: Invalid quiz ID handling
   - Type: Integration
   - Steps: GET/POST with non-existent quiz ID
   - Expected: 404 or friendly error page

## Traceability Matrix
- Feature: Create quiz — Tests: TP-002, TP-003 — Files: `app.py`, `models.py`, `templates/create_quiz.html`
- Feature: Take quiz / Scoring — Tests: TP-004, TP-005 — Files: `app.py`, `models.py`, `templates/take_quiz.html`, `templates/result.html`
- Feature: DB init — Test: TP-006 — Files: `db_init.py`
- Feature: Accessibility — Test: TP-007 — Files: all main templates

## Entry Criteria
- All required code is merged into the feature branch.
- `requirements.txt` exists and is installable.
- Test fixtures are present and usable locally.

## Exit Criteria
- All tests in the test plan marked as Must-Pass are green in CI.
- Coverage meets threshold (default 85%) or explicit waiver.
- No outstanding critical defects.
- Accessibility: no critical a11y violations for main user flows.

## Test Schedule & Milestones (example)
This is a lightweight schedule for implementing tests in this small project.
- Day 0: Create `tests/TEST_STRATEGY.md` and `tests/TEST_PLAN.md` (done).
- Day 1: Add pytest fixtures (`app`, `client`, `db`) and implement TP-001, TP-002, TP-003.
- Day 2: Implement TP-004, TP-005, TP-006.
- Day 3: Add TP-007 (axe scan) and wire up CI for lint/tests/coverage.
- Day 4: Address flaky tests and finalize CI; test sign-off.

Adjust schedule to match team capacity.

## Roles & Responsibilities
- Developer: implement tests, fix defects found, and update tests on behavior changes.
- QA/Accessibility lead: review automated a11y results and perform manual 508 checks when needed.
- Repo owner / Maintainer: merge PRs and ensure CI gating is enforced.

## Defect Severity & Priority
- Critical: app crash, data loss, severe security/a11y violation
- Major: incorrect scoring, broken primary flows
- Minor: layout, non-essential template issues

## Defect Lifecycle
- Filed in the issue tracker with reproducible steps, test case ID, severity, and owner.
- Developer fixes, pushes a PR with tests, CI runs, and reviewer verifies fix.

## Metrics & Reporting
- Test pass rate (per run)
- Coverage percentage
- Number of open defects by severity
- Accessibility violations by severity

## Risks & Mitigations
- Automated a11y misses context-specific issues: schedule manual audits pre-release.
- Tests that rely on file-based DB may leak state: enforce fixtures that create isolated DBs.
- Slow CI due to E2E: limit E2E to smoke flows in PR CI and run full E2E nightly.

## Test Deliverables
- `tests/` (pytest tests)
- `tests/TEST_STRATEGY.md` (strategy)
- `tests/TEST_PLAN.md` (this document)
- CI workflow file (recommended: `.github/workflows/ci.yml`)
- Test reports and coverage artifacts (uploaded by CI)

## Approvals & Sign-off
Acceptance by the owner/maintainer after the exit criteria are met. Sign-off should include verification of automated accessibility results and test coverage.

