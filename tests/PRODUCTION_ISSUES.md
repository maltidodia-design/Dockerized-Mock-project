# Common Production Issues — AI-Powered EdTech Assessment Platforms

Purpose: a catalogue of the failure modes that bite *this class of product*
(AI-assisted online assessment, often serving minors) once it reaches real
users. The list is grounded in the actual codebase where applicable; each
item links to detection (test or tool) and mitigation. Companion to
[GOLDEN_PATHS.md](GOLDEN_PATHS.md), the
[E2E validation report](VALIDATION_OF_AUTOMATED_E2E_TESTS.md), and the
[manual gap plan](MANUAL_TESTING_BEYOND_AUTOMATION.md).

This is not a generic "web ops" list — it's the issues that disproportionately
affect *quizzes + AI + students*.

---

## 1. Correctness & data integrity (the trust-critical class)

For an assessment tool, wrong scoring is the worst possible defect — silent,
irreversible to the learner's experience, and legally consequential if grades
are recorded.

| Issue | Why it specifically happens here | Detection | Mitigation |
|---|---|---|---|
| **Dropped answers from broken radio grouping** | Template renders each choice with a unique `name` attribute, so a real browser doesn't group the radios for a question. Users select multiple, the handler ignores everything outside its expected key range, score = 0. | [test_a11y_extended.py](test_a11y_extended.py) `test_take_page_radio_groups_share_name`. Found in real code; see Case Study A below. | Template review + an automated test that asserts all radios for one question share a `name`. |
| **Missing template helper (Jinja `enumerate`)** | Test-only fixture injection masks the gap in production. Result: every GET on the take page is a 500. | [test_e2e.py](test_e2e.py) E2E-002/003 (real-HTTP). | Always run at least one Golden Path against a real server, not just the test client. Case Study B. |
| **Grading edge cases** — empty quiz, single-question, all-wrong, `answer_index` ≥ `len(choices)`, partial submission | The create route accepts any JSON; the handler does no boundary checks. | Currently thin in [test_edge_cases.py](test_edge_cases.py). | Add JSON-schema validation on create; expand grading tests to cover boundaries. |
| **Lost results on container recreate** | SQLite lives in `instance/`; [docker-compose.yml](../docker-compose.yml) bind-mounts the repo dir (dev mode); no named volume for production. A `docker compose down -v` wipes everything. | Manual P0-1 in [MANUAL_TESTING_BEYOND_AUTOMATION.md](MANUAL_TESTING_BEYOND_AUTOMATION.md). | Named volume in a production compose file; daily backup. |

### Case Study A — radio-grouping bug (caught during this sprint)
The take-quiz template used the *inner* Jinja loop's `loop.index0` for the
radio `name`, so each choice got a unique name and the browser couldn't form
a radio group. Existing unit/integration/E2E tests all passed — because
pytest submits arbitrary form-encoded data the handler accepts, regardless
of what the rendered form would actually transmit. The bug was caught only
when a specialised a11y test specifically asserted *"all radios for one
question share a name"* on the real-server HTML. **General lesson:** tests
that fabricate form data validate the handler, not the form. A separate
class of test must validate the rendered DOM.

### Case Study B — Jinja `enumerate` 500
Same pattern, different symptom: `conftest.py` quietly added `enumerate` to
Jinja for tests, hiding a production 500 on every quiz-take. Detection
required E2E over real HTTP. **General lesson:** keep your test
configuration as close to production configuration as the test environment
allows; whenever they diverge, add an E2E test that proves the divergence is
harmless.

### Case Study C — Flask-SQLAlchemy engine cached at import time
The most insidious of the three. [app.py](../app.py) used to hard-code
`app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'` *before*
`db = SQLAlchemy(app)`. Flask-SQLAlchemy 3.x builds the engine at
`SQLAlchemy(app)` construction time, so every later attempt to override the
URI — `conftest.py`'s `:memory:` setting, `test_app.py`'s `setup_function`,
`test_models.py`'s `tmp_path` URI, and `e2e_server.py`'s temp-file path —
was **silently ignored**. Effects:

1. Every "in-memory" unit test was actually running against the real
   `instance/data.db`, dropping and recreating its tables on every test.
2. The live-server subprocess, intended to use an isolated temp file, was
   also pointed at `instance/data.db`.
3. As long as nothing else used the file simultaneously, all tests still
   passed — the file behaved like an inefficient scratch DB.
4. The moment the new specialised suites ran *in the same session* as the
   in-process tests, the parent's `db.drop_all()` wiped tables out from
   under the subprocess and the live tests started returning HTTP 500.

Detection required reading the subprocess server's actual `db.engine.url`
on every request (a debug hook), not just reading the source. **General
lesson:** any framework that does *implicit lazy initialisation at object
construction* — Flask-SQLAlchemy, ORMs with global metadata, connection
pools, cache clients — is a strong candidate for *"my override didn't
actually apply"* bugs. Configure such objects via environment variables
that are set **before import**, not via post-construction mutation. The
fix here was a one-line env-var read in [app.py](../app.py) and
`os.environ.setdefault(...)` lines in conftest.py and the live-server
launcher.

---

## 2. AI behaviour (the differentiator that breaks first)

These dominate post-launch incident counts in AI-EdTech.

| Issue | Why it specifically happens here | Detection | Mitigation |
|---|---|---|---|
| **Hallucinated explanations** — confident, wrong feedback on missed questions | Models invent facts; in an *assessment* context, students treat AI feedback as authoritative. | Golden-dataset eval (rubric + LLM-as-judge), human spot-check on rotation. | Retrieval-grounded prompts; explicit "if unsure, say so" guardrails; teacher review queue. |
| **Off-topic / age-inappropriate output** | Models can drift, especially with minors in the user base. | Adversarial probe set (OWASP LLM Top 10 + child-safety set); output moderation classifiers. | Pre-prompt safety policy; output filter; tested refusal patterns. |
| **Prompt injection via user content** | Quiz titles, question text, and answers are all user-controllable and reach the model context. A crafted quiz can hijack the AI feedback. | Test a curated prompt-injection set against `/api/ai_feedback`; OWASP LLM01. | Strict input separation (data vs instruction), allow-list output schema, rate-limit. |
| **Latency spikes / timeouts** | Real LLM calls add seconds; the current stub call is in-process inside `take_quiz` (`app.test_client().post(...)`), so a real model would block the user's response thread. | Load test the take path with a simulated slow AI; SLO on p95 latency. | Async/background job for feedback; UI shows result first, feedback streams in. |
| **Cost runaway** | Per-call cost × bot/abuse traffic can become a four-figure surprise overnight. | Rate-limit + per-user/IP cap; alerting on token spend per hour. | Quota system, captcha on `/api/ai_feedback`, kill switch. |
| **Model deprecation / vendor outage** | Providers retire models without warning; outages happen. | Synthetic monitor; circuit breaker test. | Multi-provider or graceful degrade to "feedback unavailable" (PRD §10 envisions this; the current stub doesn't implement it). |
| **Non-deterministic regressions on model upgrade** | A new model version shifts behaviour; subtle quality regressions are silent. | Golden-dataset eval re-run on every model/prompt change. | Pin model version; canary new versions; require eval delta in PRs. |

---

## 3. Security & privacy (highest legal blast radius)

| Issue | Why it specifically happens here | Detection | Mitigation |
|---|---|---|---|
| **Stored XSS via quiz title / question / choice** | All three render user-supplied strings into HTML. Jinja autoescape protects us today; one `\|safe` filter or HTML-export feature reopens the hole. | [test_security.py](test_security.py) `test_stored_xss_*` — *locks the protection in*. | Keep autoescape on; review any export path; CSP header. |
| **CSRF on form POSTs** | No CSRF token on `/create` or `/take/<id>`. Once auth lands, third-party sites can forge submissions. | [test_security.py](test_security.py) `test_cross_origin_post_create_is_rejected` (xfail until fixed). | Flask-WTF / CSRFProtect; SameSite cookies. |
| **Form tampering → 500** | `int()` cast on form value with no try/except. Existing tests *enshrine* the crash. | [test_security.py](test_security.py) `test_form_tampering_non_int_answer_is_handled_gracefully` (xfail). | Validate as int with fallback; return 400 or treat as unanswered. |
| **Missing security response headers** | Flask sets none of `X-Content-Type-Options`, `X-Frame-Options`, `CSP` by default. | [test_security.py](test_security.py) `test_security_response_headers_present` (xfail). | Flask-Talisman or `after_request` hook. |
| **PII / minor data in logs** | Default Flask logging includes request paths and form data via stack traces. For a service handling minors, this is a regulatory issue (FERPA, COPPA, GDPR DPIA). | Log-review checklist; redact-on-write helpers; audit logging policy. | Structured logs with PII redaction; never log raw form bodies. |
| **Prompt-injection ex-filtration** | A crafted quiz instructs the model to reveal system prompt or another student's data once context is shared. | Adversarial set; output schema enforcement. | Hard-separate user data from instructions; never share context across students. |
| **Authn / Authz gaps** (when added) | Role confusion (student becomes teacher), insecure direct object reference on `/take/<id>`. | Authz test matrix per role. | Centralised access decisions; tests asserting *forbidden* paths, not just allowed ones. |

---

## 4. Performance & scale (exam-day failure modes)

EdTech traffic is **bursty**: a teacher posts a quiz and 30–300 students hit
it within minutes. The product must survive this even with otherwise low
average load.

| Issue | Why it specifically happens here | Detection | Mitigation |
|---|---|---|---|
| **SQLite "database is locked" under writes** | `docker-compose.yml` runs `gunicorn --workers 2`; two processes writing one SQLite file deadlock. Submissions burst exactly at the wrong time. | Load test with concurrent submissions (Locust/k6). | Single-worker for SQLite *or* migrate to Postgres before any real launch. |
| **Synchronous internal HTTP call** | [app.py](../app.py) `take_quiz` does `app.test_client().post('/api/ai_feedback', ...)` inline. Each submission consumes a worker for the duration of the AI call. With a real model that's seconds. | Load test; thread/worker utilisation metric. | Background job (Celery/RQ); stream feedback to the UI separately. |
| **Unbounded home-page listing** | `index` renders *all* quizzes. With hundreds of teachers, the page grows without limit. | Smoke test with N=1000 quizzes. | Pagination; archive flag. |
| **Large quiz payloads** | No max-content-length set; 10 MB of JSON persists into a Text column. | [test_security.py](test_security.py) `test_large_quiz_payload_does_not_500` covers basic robustness. | Cap `MAX_CONTENT_LENGTH`; enforce per-question size limits. |
| **AI cost amplification** | A single hot quiz can drive 200 model calls/minute. | Per-user/IP rate-limit metric. | Token bucket; cache identical-question feedback. |

---

## 5. Operational / observability (what makes 3am pages worse)

| Issue | Why it bites this product | Mitigation |
|---|---|---|
| **No health/readiness endpoint** | Orchestrators can only probe `/`, which hits the DB and is unrepresentative. | Add `/healthz` returning 200 statically. |
| **No structured logs / request IDs** | When a parent reports "Jamie's quiz didn't grade," there's no way to trace it. | JSON logging; per-request ID propagated to AI calls. |
| **No error monitoring / alerting** | A spike in 500s on exam day is invisible until a teacher emails. | Sentry / Datadog; alert on 5xx rate, AI failure rate. |
| **Broken `db_init.py`** | Module-level `db.create_all()` lacks an app context; the README's first-time setup command likely errors. | Wrap in `with app.app_context():`. |
| **No DB migration tooling** | `db.create_all()` only — any schema change breaks existing data silently. | Alembic; pre-deploy migration check. |
| **Config drift** | [Dockerfile](../Dockerfile) sets `FLASK_ENV=production`; [docker-compose.yml](../docker-compose.yml) overrides to `development`. If anyone ever runs `python app.py` in that env, Werkzeug debugger is reachable — known RCE surface. | Remove the override; lint compose files. |

---

## 6. Compliance & regulatory (the slow-burn class)

| Issue | Why it bites this product | Detection / Mitigation |
|---|---|---|
| **"Permanent" data retention** (PRD §8) | Directly conflicts with GDPR / CCPA / FERPA / state student-privacy laws. | Retention schedule; user-initiated deletion endpoint; cron purge. |
| **No age gate** | COPPA defaults to assuming you collect under-13 data without verifiable parental consent. | Age-gate flow; parental-consent path; documented data-minimisation. |
| **No AI-interaction disclosure** | EU AI Act Article 50 and FTC guidance both expect a clear "you are interacting with AI" notice on the result page. | Visible disclosure label; audit log of presentation. |
| **Accessibility regressions** | A redesign drops `lang` attribute or breaks radio fieldsets → the product fails Section 508 / WCAG 2.1 AA, blocking public-school procurement. | axe/pa11y in CI; the `xfail`-marked tests in [test_a11y_extended.py](test_a11y_extended.py) flip to pass when fixed and then guard them. |
| **No DPA / VPAT** | Schools won't sign without a Data Processing Agreement and an Accessibility Conformance Report. | Adopt SDPC NDPA template; publish a VPAT/ACR. |
| **Breach-notification readiness** | State and EU clocks (often 72 hours) can't be met without an incident-response plan. | Written runbook; tabletop exercise. |

---

## 7. User-experience traps (high frequency, low severity individually)

- **Browser back/forward after submission** re-submits the form and creates duplicate `Result` rows. Mitigate with POST-Redirect-GET.
- **Double-click submit** creates duplicates (no idempotency token).
- **Long text in titles / questions** breaks layout — manual check; eventual CSS truncation.
- **Session timeouts during a long quiz** lose answers — once auth lands, autosave.

---

## 8. Detection / prevention at a glance

| Category | Best-in-class detection | Cheapest first step |
|---|---|---|
| Correctness | Real-HTTP E2E + DOM-level form contract tests | The new [test_a11y_extended.py](test_a11y_extended.py) radio-grouping test |
| AI behaviour | Golden-dataset eval, adversarial set, output classifier | A ~30-case rubric eval re-run on every prompt/model change |
| Security | SAST (Bandit) + DAST (ZAP) + targeted threat tests | The new [test_security.py](test_security.py) XSS lockdown + xfail-marked gap tests |
| Performance | Locust/k6 load on Golden Paths | A 50-line concurrent-submit script |
| Operational | Structured logs + Sentry + `/healthz` | Add `/healthz` and turn on JSON logging |
| Compliance | DPIA + retention engine + AI disclosure | Add the AI-interaction notice and a deletion endpoint |

---

## 9. Pattern recognition — the meta-lesson

Three unrelated production bugs found in this codebase while writing the
specialised suites (`enumerate` undefined, broken radio grouping, engine
cached at import) shared the same shape:

> **The automated test environment papered over the production
> environment, so green CI proved nothing about what users would see.**

That pattern — *"my tests configure something the real server doesn't"* — is
the single most expensive recurring class of EdTech production incident. The
mitigation is not "more tests"; it is **at least one test per Golden Path
that runs against an environment as close to production as possible** —
ideally the actual shipped Docker artifact. Every other failure mode in this
document is a known one; this pattern is the *hidden* one.
