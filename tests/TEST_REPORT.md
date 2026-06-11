# Final Test Report — Automated + Manual

**Project:** Dockerized Mock Quiz (AI-Powered Quiz & Study Assistant Platform — 508 final project)
**Branch:** `CI-CI-Pipeline-submission`
**Local validation environment:** macOS 14, Python 3.9.6 (`.venv`), pytest 8.4.2
**CI environment:** GitHub Actions `ubuntu-latest`, Python 3.10 (per [.github/workflows/ci.yml](../.github/workflows/ci.yml))

This report consolidates the results of the **automated** suites and the
state of the **manual** sign-off matrix. Companion docs:
[VALIDATION_OF_AUTOMATED_E2E_TESTS.md](VALIDATION_OF_AUTOMATED_E2E_TESTS.md),
[VALIDATION_OF_ AUTOMATED_UNIT_TESTS.md](VALIDATION_OF_%20AUTOMATED_UNIT_TESTS.md),
[GOLDEN_PATHS.md](GOLDEN_PATHS.md),
[MANUAL_TESTING_BEYOND_AUTOMATION.md](MANUAL_TESTING_BEYOND_AUTOMATION.md),
[REFLECTION.md](REFLECTION.md).

---

## 1. Executive summary

| Layer | Count | Status |
|---|---|---|
| **Unit + integration + accessibility** | 23 | ✅ all pass |
| **E2E (real-HTTP)** | 7 | ✅ all pass |
| **Specialised — security** | 8 | ✅ all pass |
| **Specialised — extended accessibility** | 10 | ✅ all pass |
| **Specialised — AI behaviour & safety** | 21 (incl. parametrised) | ✅ all pass |
| **Specialised — concurrency smoke** | 2 | ✅ all pass |
| **Static analysis (Bandit SAST)** | — | ✅ no findings |
| **Dependency CVE scan (pip-audit on requirements.txt)** | — | ✅ no vulnerabilities |
| **Total automated** | **71 pytest tests + 2 scanners** | **✅ 71 / 0 / 0 xfailed** |
| **Manual sign-off matrix** | 6 gates | 🟡 pending operator |

> The numbers above are stable across **5 consecutive full-suite runs** (no flakes); see §6.

---

## 2. Test environment and reproduction

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# 1. Unit + integration
pytest tests/ \
  --ignore=tests/test_e2e.py \
  --ignore=tests/test_security.py \
  --ignore=tests/test_a11y_extended.py \
  --ignore=tests/test_ai_safety.py \
  --ignore=tests/test_performance.py -v

# 2. E2E
pytest tests/test_e2e.py -v

# 3. Specialised
pytest tests/test_security.py tests/test_a11y_extended.py \
       tests/test_ai_safety.py tests/test_performance.py -v

# 4. SAST + 5. SCA
pip install bandit pip-audit
bandit -r app.py db_init.py tests/e2e_server.py --skip B104 -ll
pip-audit --strict --requirement requirements.txt
```

CI replicates this exact sequence (5 independent steps so each turns red on its own).

---

## 3. Automated suite — per-file results

| File | Tests | Pass | Fail | xfail | Notes |
|---|---|---|---|---|---|
| [test_app.py](test_app.py) | 4 | 4 | 0 | 0 | Smoke + index quiz listing |
| [test_routes.py](test_routes.py) | 4 | 4 | 0 | 0 | Happy-path routes + validation |
| [test_models.py](test_models.py) | 3 | 3 | 0 | 0 | DB CRUD, init |
| [test_edge_cases.py](test_edge_cases.py) | 6 | 6 | 0 | 0 | Includes form-tampering graceful handling |
| [test_integration.py](test_integration.py) | 1 | 1 | 0 | 0 | Cross-layer flow |
| [test_accessibility.py](test_accessibility.py) | 3 | 3 | 0 | 0 | Hand-rolled label/heading checks |
| [test_e2e.py](test_e2e.py) | 7 | 7 | 0 | 0 | Real-HTTP user journeys + `/healthz` |
| [test_security.py](test_security.py) | 8 | 8 | 0 | 0 | XSS lockdown, CSRF, headers, form-tamper, large payload |
| [test_a11y_extended.py](test_a11y_extended.py) | 10 | 10 | 0 | 0 | lang, title, headings, dup ids, fieldset, radio name |
| [test_ai_safety.py](test_ai_safety.py) | 21 | 21 | 0 | 0 | Schema + robustness + injection set + canaries + rate-limit |
| [test_performance.py](test_performance.py) | 2 | 2 | 0 | 0 | Concurrent submit + concurrent create |
| **Total** | **69** ¹ | **69** | **0** | **0** | |

¹ pytest reports **71** because two tests are parametrised (`injection × 6`, `canaries × 8`, `headings × 2`, `lang × 2`, `dup-ids × 2`, `title × 2`); counted as one row above but expanded by pytest.

---

## 4. Specialised testing — detail

### 4.1 Security ([test_security.py](test_security.py))

| Test | Asserts | Status |
|---|---|---|
| Stored-XSS escape — title on home | Jinja autoescape locked in | ✅ |
| Stored-XSS escape — title on result page | " | ✅ |
| Stored-XSS escape — question text on take page | " | ✅ |
| Stored-XSS escape — choice text on take page | " | ✅ |
| Large payload (200 questions) does not 500 | `MAX_CONTENT_LENGTH` allows it | ✅ |
| Form tampering (non-int answer) gracefully handled | `int()` wrapped in try/except | ✅ |
| Cross-origin POST `/create` rejected | Origin-based CSRF returns 403 | ✅ |
| Security response headers present (CSP, XCTO, XFO, Referrer) | `after_request` hook | ✅ |

### 4.2 Extended accessibility ([test_a11y_extended.py](test_a11y_extended.py))

| Test | Asserts | Status |
|---|---|---|
| Page has non-empty `<title>` × 2 paths | Browser tab / screen-reader announce | ✅ |
| `<html lang>` declared × 2 paths | WCAG 3.1.1 | ✅ |
| No skipped heading levels × 2 paths | WCAG 1.3.1 | ✅ |
| No duplicate id attributes × 2 paths | WCAG 4.1.1 | ✅ |
| Take page wraps radios in `<fieldset><legend>` | WCAG 1.3.1 / 3.3.2 | ✅ |
| Take page radios share `name` (real radio group) | Caught a previously hidden product bug | ✅ |

### 4.3 AI behaviour & safety ([test_ai_safety.py](test_ai_safety.py))

| Test | Asserts | Status |
|---|---|---|
| Schema top-level keys | Contract | ✅ |
| Explanation item shape | Contract | ✅ |
| Content-Type is JSON | Contract | ✅ |
| Missing `details` → default recommendation | Robustness | ✅ |
| Oversized payload does not 500 | Robustness | ✅ |
| Malformed `details` element gracefully handled | Robustness | ✅ |
| 6 × prompt-injection payloads — no echo, schema holds | Injection-resistance | ✅ |
| 8 × canary substrings absent | Leak-detection | ✅ |
| Rate limit returns 429 under burst | DoS / cost-amplification | ✅ |

### 4.4 Concurrency smoke ([test_performance.py](test_performance.py))

| Test | Asserts | Status |
|---|---|---|
| 20 concurrent submissions of one quiz → all 200, correct score | Server tolerates burst | ✅ |
| 20 concurrent creations → each listed exactly once on home | No lost writes / duplicates | ✅ |

### 4.5 Static / dependency scans

| Scanner | Scope | Result |
|---|---|---|
| Bandit (SAST) | `app.py`, `db_init.py`, `tests/e2e_server.py`; `--skip B104 -ll` | No issues identified |
| pip-audit (SCA) | `--requirement requirements.txt --strict` | No known vulnerabilities |

---

## 5. Manual test suite — sign-off matrix

Detailed plan in [MANUAL_TESTING_BEYOND_AUTOMATION.md](MANUAL_TESTING_BEYOND_AUTOMATION.md).

| Gate | What's verified | Owner | Status |
|---|---|---|---|
| **P0-1** Docker / gunicorn smoke (GP-1, GP-2, headers, `/healthz`, persistence across restart) | The shipped artifact actually works | QA / Dev | ☐ pending |
| **P0-2** AI feedback quality (relevance, tone, age-appropriateness) | Non-deterministic content judgement | QA / Subject reviewer | ☐ pending |
| **P0-3** 508 manual audit (keyboard order, focus rings, screen-reader announcement quality) | Beyond static conformance rules | Accessibility lead | ☐ pending |
| **P0-4** Content Security Policy does not break the UI | No CSP violations across Chrome/Safari/Firefox | Front-end / QA | ☐ pending |
| **P1** Cross-browser & responsive, AI failure UX, rate-limit UX, browser-side concurrency | Per [MANUAL_TESTING_BEYOND_AUTOMATION.md](MANUAL_TESTING_BEYOND_AUTOMATION.md) §3.P1 | QA | ☐ pending |
| **Release approval** | All P0 + P1 sign-offs complete | Maintainer | ☐ pending |

A failed **P0** blocks release.

---

## 6. Stability evidence (no flaky tests)

Five consecutive full-suite runs:

```
======================= 71 passed, 13 warnings in 1.10s ========================
======================= 71 passed, 13 warnings in 1.05s ========================
======================= 71 passed, 13 warnings in 1.07s ========================
======================= 71 passed, 13 warnings in 1.09s ========================
======================= 71 passed, 13 warnings in 1.06s ========================
```

The rate-limit burst test contains a 0.25 s post-pause so its sliding-window
state cannot poison subsequent `/api/ai_feedback` tests — the only known
test-ordering hazard, and the only deliberate sleep in the suite.

---

## 7. Real product defects found via testing

Three production-only bugs were caught by the test work and **fixed in the
product** during this branch. Detail and lessons in
[PRODUCTION_ISSUES.md](PRODUCTION_ISSUES.md) §1 and [REFLECTION.md](REFLECTION.md).

1. **`take_quiz.html` referenced Jinja's `enumerate` global** which Jinja
   does not expose — every `GET /take/<id>` was an HTTP 500 under real
   gunicorn. Masked because `conftest.py` injected it for tests.
2. **Radio-grouping in `take_quiz.html`** used the inner Jinja loop's
   `loop.index0` for the `name` attribute, so radios for one question got
   *different* names and didn't form a radio group in a real browser.
   Existing tests passed because pytest submits arbitrary form data the
   handler accepts.
3. **Flask-SQLAlchemy 3.x engine cache** — `SQLAlchemy(app)` in `app.py`
   bound the engine to the default URI at import time, so every later
   override (in conftest, in the live-server launcher, in `test_models`)
   was silently ignored. The "in-memory" tests were actually writing to
   the real `instance/data.db`; the live-server subprocess was *also*
   writing to it; the parent's `db.drop_all()` wiped tables out from
   under the subprocess mid-session.

In each case the test that caught the bug now guards the fix.

---

## 8. Coverage vs Golden Paths

Mapped against [GOLDEN_PATHS.md](GOLDEN_PATHS.md):

| Golden Path | E2E coverage | Specialised coverage | Manual P0 |
|---|---|---|---|
| GP-1 Full author→learner loop, all correct | E2E-002 | — | P0-1 |
| GP-2 Accurate grading on mixed answers | E2E-003 | concurrency smoke | P0-1 |
| GP-3 AI feedback on incorrect | E2E-003, E2E-006 | AI-safety (21 tests) | P0-2 |
| GP-4 Create & discover | E2E-002/003 | — | P0-1 |
| GP-5 508 accessibility on primary flow | — | extended-a11y (10) + accessibility (3) | P0-3 |
| Guardrails (404 / 400) | E2E-004/005 | — | — |
| `/healthz` | E2E-007 | — | P0-1 |

Every Golden Path has at least one real-HTTP automated test and at least
one manual P0 gate — the rule established in [GOLDEN_PATHS.md](GOLDEN_PATHS.md) §case-study.

---

## 9. Limitations and known operational gaps

Captured here for sign-off transparency (full discussion in
[AI_GENERATED_SPECIALIZED_TESTS.md](AI_GENERATED_SPECIALIZED_TESTS.md) §2):

- **CI runs `pytest` against the host runner, not the Docker artifact.**
  The single highest-leverage missing CI step is `docker compose up -d &&
  curl /healthz && curl /…`. This is what would have caught two of the
  three production bugs above without writing any test.
- **The AI endpoint is a deterministic stub.** Injection-resistance and
  canary tests pass trivially today; the harness becomes meaningful when
  a real LLM is wired in.
- **SQLite `database is locked` under `gunicorn --workers 2`** is a
  documented latent bug — the concurrency smoke uses werkzeug
  `threaded=True` (one process) so it does not reproduce. Manual P1 and
  the Docker-smoke step would surface it.
- **No real screen-reader / cross-browser automation.** Manual P0-3 / P1-1.

---

## 10. Sign-off

| Section | Status | Signed by |
|---|---|---|
| Automated suites green | ✅ | Maintainer (this report) |
| Bandit clean | ✅ | Maintainer |
| pip-audit clean (runtime) | ✅ | Maintainer |
| Production defects fixed and guarded | ✅ | Maintainer |
| **Manual P0 set** | 🟡 pending | QA / Accessibility lead |
| **Release approval** | 🟡 pending | Maintainer |
