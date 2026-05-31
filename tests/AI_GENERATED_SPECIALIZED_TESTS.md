# AI-Generated Specialized Testing — What's Automated and What Isn't

This file is the deliverable for *"automated specialised testing, AI-generated,
or a description of why you can't automate it."* It does both: it lists
exactly what was generated and added to this repo, and it states clearly
which categories were **deliberately not** automated, with the reason in
each case.

Companion to
[CONFIGURATION_MATRIX.md](CONFIGURATION_MATRIX.md),
[PRODUCTION_ISSUES.md](PRODUCTION_ISSUES.md),
[GOLDEN_PATHS.md](GOLDEN_PATHS.md), and
[MANUAL_TESTING_BEYOND_AUTOMATION.md](MANUAL_TESTING_BEYOND_AUTOMATION.md).

---

## 1. What was generated and added

All of the following was authored by an AI assistant in this branch and runs
in CI under `.github/workflows/ci.yml` ([ci.yml](../.github/workflows/ci.yml)).
Each entry maps to a Pareto specialty from
[GOLDEN_PATHS.md](GOLDEN_PATHS.md): **accessibility**, **AI behaviour &
safety**, **security**.

### 1.1 Security testing — [tests/test_security.py](test_security.py)

| Test | Type | Outcome |
|---|---|---|
| Stored-XSS escape in quiz **title** on home | regression guard | ✅ passes — Jinja autoescape locked in |
| Stored-XSS escape in quiz **title** on result page | regression guard | ✅ passes |
| Stored-XSS escape in **question text** on take page | regression guard | ✅ passes |
| Stored-XSS escape in **choice text** on take page | regression guard | ✅ passes |
| Large quiz payload (200 questions) does not 500 | robustness | ✅ passes |
| **Form tampering → graceful, not 500** | known-gap (`xfail`) | ❌ xfail — fix is to wrap `int()` cast |
| **Cross-origin POST /create is rejected** | known-gap (`xfail`) | ❌ xfail — wire Flask-WTF CSRF |
| **Security response headers present** | known-gap (`xfail`) | ❌ xfail — add Flask-Talisman or `after_request` hook |

### 1.2 Extended accessibility — [tests/test_a11y_extended.py](test_a11y_extended.py)

| Test | Type | Outcome |
|---|---|---|
| Pages have non-empty `<title>` | conformance | ✅ passes |
| Heading levels don't skip (h1 → h2 → h3) | conformance | ✅ passes |
| No duplicate `id` attributes | conformance | ✅ passes |
| Radio inputs for one question share `name` | conformance | ✅ passes (**caught a real bug**) |
| **`<html lang>` attribute present** | known-gap (`xfail`) | ❌ xfail — one-line template change |
| **Radio groups use `<fieldset><legend>`** | known-gap (`xfail`) | ❌ xfail — template refactor |

### 1.3 AI behaviour & safety — [tests/test_ai_safety.py](test_ai_safety.py)

| Test | Type | Outcome |
|---|---|---|
| Response top-level schema (`explanations`, `recommendations`) | contract | ✅ passes |
| Explanation item shape (`index`, `explanation`) | contract | ✅ passes |
| Content-Type is `application/json` | contract | ✅ passes |
| Missing `details` returns default recommendation | robustness | ✅ passes |
| Oversized payload does not 500 | robustness | ✅ passes |
| 6 × prompt-injection payloads not echoed | injection-resistance | ✅ passes |
| 8 × canary substrings absent (`system prompt`, `API_KEY`, …) | leak-detection | ✅ passes |
| **Malformed `details` element returns 4xx not 500** | known-gap (`xfail`) | ❌ xfail — `.get()` on non-dict raises |
| **Rate-limit returns 429 under burst** | known-gap (`xfail`) | ❌ xfail — no rate limiting today |

Note: today the endpoint is a deterministic Python stub. The injection /
canary checks pass *trivially* against the stub; their value is that the
harness is in place when a real LLM is wired in, and the schema contract
prevents drift.

### 1.4 Concurrency smoke — [tests/test_performance.py](test_performance.py)

| Test | Type | Outcome |
|---|---|---|
| N concurrent submissions of one quiz → all 200, correct score | concurrency | ✅ passes |
| N concurrent creations of distinct quizzes → all listed exactly once | concurrency | ✅ passes |

### 1.5 Scanner integration in CI

| Tool | What it catches | Configured |
|---|---|---|
| **Bandit** (SAST) | Python security anti-patterns (eval, weak hashes, shell injection, hardcoded creds, …) | `.github/workflows/ci.yml` — runs `bandit -r app.py db_init.py tests/e2e_server.py --skip B104 -ll`. Currently clean. |
| **pip-audit** (SCA) | Known CVEs in declared runtime dependencies | `pip-audit --strict --requirement requirements.txt`. May surface real findings on this branch — that *is* the point. |

### 1.6 Suite totals after this work

| Layer | Tests |
|---|---|
| Unit + integration + accessibility | 23 pass |
| E2E (real HTTP) | 6 pass |
| Specialized (security + a11y + AI safety + perf) | 33 pass + 8 documented `xfail` |
| **Total pytest** | **62 pass + 8 xfail** |
| Plus CI scanners | Bandit + pip-audit |

---

## 2. What was **not** automated, and why

Each row below is something automation could not credibly produce on its
own. The reason is given honestly so the manual plan
([MANUAL_TESTING_BEYOND_AUTOMATION.md](MANUAL_TESTING_BEYOND_AUTOMATION.md))
inherits the right scope.

### 2.1 Inherently human-judgement testing — *cannot* be automated even in principle

| Category | Why automation can't substitute |
|---|---|
| **Screen-reader experience quality** | Tools can verify a label exists; only a human can judge whether the announcement *makes sense* (correct pronunciation, useful tab-stop order, intelligible focus changes). |
| **Pedagogical fit of AI feedback** | A model's explanation can be perfectly safe and on-topic and still be *unhelpful* for the specific learner. Rubric eval and LLM-as-judge approximate this; they don't replace teacher review. |
| **Age-appropriate tone for minors** | Detectable extremes can be classified; the centre of the distribution requires human judgement, especially in education. |
| **Novel jailbreaks / creative attacks** | An LLM-generated adversarial set catches the categories it was trained on. Genuinely novel attacks are by definition outside its distribution. |
| **Visual / brand consistency** | Pixel-perfect rendering and aesthetic judgement need a designer's eye. Visual-regression tools catch *differences*, not *quality*. |
| **Real-user usability** | Latency under specific cognitive loads, confusion on edge cases — only measurable with users. |

### 2.2 Could be automated, but **deliberately not in this branch** — heavy infrastructure

The right tool exists; integrating it is multi-day work and a separate
engineering decision. Documented so future work has a clear shopping list.

| Category | What's needed | Why deferred |
|---|---|---|
| **axe-core a11y scan** | Playwright + axe-core injection | Adds a Node toolchain to a Python project and a heavy CI dependency. The hand-rolled checks in [test_a11y_extended.py](test_a11y_extended.py) cover the rules a maintainer would most likely break; axe is the obvious *next* step. |
| **Cross-browser (Chromium / WebKit / Firefox)** | Playwright matrix in CI | Same — biggest single ROI for cross-browser, but a separate workflow file. |
| **Responsive / viewport testing** | Playwright `deviceScaleFactor` matrix | Same toolchain dependency. |
| **Visual regression** | Playwright snapshots + image diffing (or Percy / Chromatic) | Requires baselines + storage; high false-positive rate without tuning. |
| **Real load test** | Locust / k6 against a Docker-built artifact in a separate job | The concurrency smoke catches in-process failures. A real load test should run against gunicorn + multi-worker — the configuration where the known SQLite-lock bug actually surfaces. |
| **Docker artifact smoke in CI** | Workflow step that runs `docker compose up -d` and curls the running app | Highest-leverage missing CI step — it would have caught the `enumerate` 500 by itself. Single follow-up PR. |
| **DAST (OWASP ZAP baseline scan)** | ZAP container in a CI job against the live server | Useful breadth coverage; needs careful baseline tuning to avoid noise. Bandit + the targeted threat tests cover the high-frequency Python issues today. |
| **Real LLM golden-dataset eval** | Pinned model + LLM-as-judge harness + ~30–50 graded cases | Only meaningful once the stub is replaced. Harness shape is in [test_ai_safety.py](test_ai_safety.py); add the model layer next to it. |
| **Mutation testing (mutmut/cosmic-ray)** | A test-quality measurement loop | Useful signal on assertion strength, but expensive to run; Pareto loses to writing more targeted tests until coverage stabilises. |
| **Accessibility under assistive tech automation (NVDA/JAWS/VoiceOver)** | AT scripting frameworks exist (Guidepup, NV Access tooling, AppleScript for VoiceOver) but are brittle and hard to maintain. | Manual audit is honestly cheaper and more reliable here; see P0-3 in [MANUAL_TESTING_BEYOND_AUTOMATION.md](MANUAL_TESTING_BEYOND_AUTOMATION.md). |

### 2.3 Currently impossible against the deployed configuration

| Category | Why it can't be automated *here* |
|---|---|
| **`gunicorn --workers 2` + SQLite "database is locked"** | The known production bug requires a **multi-process** server. The live-server fixture uses werkzeug `threaded=True` (one process). Reproducing the bug in pytest would mean spawning gunicorn workers from a test — out of scope; documented in [PRODUCTION_ISSUES.md](PRODUCTION_ISSUES.md) §4 and the Docker-smoke gap above. |
| **Real network throttling / packet loss** | Requires either Playwright network conditions or a separate test environment with `tc netem`. The concurrency smoke is the closest in-process approximation. |
| **Real prompt injection against a real LLM** | The injection harness in [test_ai_safety.py](test_ai_safety.py) is built; only the model is missing. |
| **Compliance behaviour (GDPR/COPPA/FERPA retention & deletion)** | The product currently has no deletion endpoint. There is nothing to test until the feature exists. The harness for the test is one line — `DELETE /quiz/<id>` then `GET /` must not list it. |

---

## 3. Honest summary

Automation in this branch covers the *deterministic, repeatable* portion of
the three Pareto specialties:

- **Security** — stored-XSS regression guards, robustness, a known-gap
  shelf, plus Bandit and pip-audit in CI.
- **Accessibility** — page-level conformance rules a static scan can
  decide, plus the radio-grouping test that caught a real product bug.
- **AI safety** — schema contracts, robustness, injection-resistance and
  leak-canary scaffolding ready for a real model.

It deliberately does **not** try to automate human-judgement work
(screen-reader UX, pedagogical fit, novel attacks). Those are scoped to
the manual plan, which is where the project's accessibility-lead /
teacher-reviewer time is best spent.

The single largest remaining gap is **not** more pytest tests — it is a CI
step that builds and curls the actual Docker artifact. That one addition
covers the failure class that has *already* caused two of the three
production bugs found this sprint.
