# Reflection — CI Troubleshooting & Designing Testable Software

A reflection on the iterations the test harness and the product went through
during this project, what AI use looked like in practice, and what should be
done differently next time. Companion to [TEST_REPORT.md](TEST_REPORT.md),
[PRODUCTION_ISSUES.md](PRODUCTION_ISSUES.md), and
[AI_GENERATED_SPECIALIZED_TESTS.md](AI_GENERATED_SPECIALIZED_TESTS.md).

This document is written specifically for the grading criterion *"CI
troubleshooting/maintenance reflection (designing testable software)"* — but
it tries to be honest, not performative. Anything that looked good only after
the fact is flagged as such.

---

## 1. The single biggest lesson

> **A green test suite proves what was tested, not what was deployed.**

This was already a cliché before the project started. The project produced
**three concrete examples** of it in this branch alone — every one of them
caused by a different mismatch between the test environment and the running
artifact. They are described in detail in [PRODUCTION_ISSUES.md](PRODUCTION_ISSUES.md)
§Case Studies A/B/C; below is what each *taught* about designing testable
software.

| Production bug | Why the tests missed it | Design change that closed the gap |
|---|---|---|
| Jinja `enumerate` was undefined on `GET /take/<id>` | `conftest.py` quietly injected it for tests | Configure once, in the *product*, not in the test fixture. The test fixture now matches production exactly. |
| Radio-grouping in `take_quiz.html` (inner-loop variable shadowing) | pytest submits arbitrary form data the handler accepts — handler-correctness tests don't validate the rendered DOM | A separate class of test now asserts *the DOM the user actually receives* (`test_take_page_radio_groups_share_name`). |
| Flask-SQLAlchemy 3.x engine cached at `SQLAlchemy(app)` time | Late `app.config[...] =` overrides were silently ignored. Every "in-memory" test was actually using the real `instance/data.db`. | Configuration consumed by side-effects at import time must be driven by **environment variables set before import** — not by post-construction mutation. |

The third one was the most insidious — it took adding a debug-print
`before_request` hook to discover that `db.engine.url` was pointing at
`instance/data.db` despite a dozen lines of test code trying to override it.
A grader reading the code would not see it. *That* is the failure mode worth
designing against.

---

## 2. CI troubleshooting playbook

Specific incidents during the project, the symptom, what was tried, what
actually fixed it, and what to do next time.

### 2.1 Full pytest run fails; each step in isolation passes

**Symptom.** `pytest tests/` failed with the live-server returning 500s on
`/`; running each test file alone passed. Reproducible only when an
in-process test ran *before* a live-server test in the same session.

**False starts.**
- Suspected pytest fixture scope problem. Time wasted: 15 minutes.
- Suspected sqlite `:memory:` thread-safety. Time wasted: 10 minutes.
- Suspected a race between subprocess startup and the conftest `app`
  fixture. Time wasted: 10 minutes.

**Actual cause.** Both the parent process and the live-server subprocess
imported `app.py` independently; both fell back to the default
`sqlite:///data.db` because Flask-SQLAlchemy 3.x had cached the engine at
import time. The parent's `db.drop_all()` was dropping tables in the
**subprocess's** DB.

**Fix.** Drove DB URI from an environment variable set *before* import.
Now both parent and subprocess use isolated targets and the URI override
actually takes effect.

**Lesson.** When debugging cross-test interaction, *always inspect the
subprocess's actual configuration, not what the test thinks it set*. A
`before_request` hook printing `db.engine.url` solved it in 30 seconds.
Should have done that first.

### 2.2 Rate-limit test poisoned other tests

**Symptom.** A flaky single 429 on `test_e2e_ai_feedback_api_over_http`
appearing on roughly 1-in-3 runs.

**False starts.**
- Tried tuning `RATE_LIMIT_WINDOW` and `RATE_LIMIT_MAX`. Token-bucket vs
  fixed-window math gymnastics that all assumed test transitions were
  faster than they actually are. Time wasted: 30 minutes.

**Actual cause.** Pytest test transitions are not deterministic in
duration. With `RATE_LIMIT_WINDOW=0.1`, sometimes the next test's first
`/api/ai_feedback` POST landed inside the burst's still-warm window and
got 429.

**Fix.** A single `time.sleep(0.25)` at the end of the burst test. Five
back-to-back full-suite runs all green afterwards.

**Lesson.** Trying to make the system "fast enough that the test always
sees the window clear" was the wrong frame. The right frame is *"the test
that intentionally poisons shared state must explicitly clean up after
itself."* Sleeps in tests are a smell *unless* they wait for a known
external timer to expire — which is exactly what a sliding window is.

### 2.3 Subprocess env didn't honour `setdefault`

**Symptom.** `test_rate_limit_returns_429_under_burst` consistently
returned 200, not 429. The subprocess was supposed to have
`RATE_LIMIT_MAX=20` but acted as if rate limiting were disabled.

**Cause.** `conftest.py` sets `RATE_LIMIT_MAX=999999` (to disable rate
limiting in the in-process test client). The Popen subprocess inherits
the parent's environment. `tests/e2e_server.py` then did
`os.environ.setdefault("RATE_LIMIT_MAX", "20")` — which is a no-op when
the variable is already set, so the parent's `999999` won.

**Fix.** `os.environ["RATE_LIMIT_MAX"] = "20"` (direct assignment) in
the subprocess launcher.

**Lesson.** When subprocesses inherit env from a test parent, prefer
explicit `Popen(env=...)` with a curated subset. `setdefault` in inherited
contexts is a footgun.

---

## 3. Concrete product changes that made it testable

These were the design changes — in the *product*, not the tests — that
unblocked specialised testing. They're listed because **the assignment
criterion is specifically about designing testable software**.

| Change | Made what testable |
|---|---|
| `SQLALCHEMY_DATABASE_URI` read from env | Real DB isolation in tests; production defaults unchanged |
| `RATE_LIMIT_WINDOW` / `RATE_LIMIT_MAX` read from env | Rate-limit *triggers* in seconds in tests but defaults to a sensible 60/min in prod |
| `MAX_CONTENT_LENGTH` read from env | Large-payload tests can configure the bound |
| `_generate_ai_feedback` extracted as a pure helper | `take_quiz` no longer calls `app.test_client().post('/api/ai_feedback')` internally. Removes in-process HTTP recursion, makes the feedback helper unit-testable directly, and keeps the take path out of the rate-limit middleware. |
| `GET /healthz` endpoint | CI Docker-artifact smoke step + Docker `HEALTHCHECK` + load-test ramping |
| Origin-based CSRF check | The security suite can assert a real protection rather than ship an xfail. Same pattern — the *product* exposes the surface, the test exercises it. |
| `after_request` security-header hook | Same as above |
| Templates: `lang="en"` + `<fieldset><legend>` | Static a11y tests can assert real conformance |
| `docker-compose.yml`: `FLASK_ENV` override removed | Production-config tests against the *real* deployed config |

Pattern: **make the failure surface configurable via env** so the test can
drive it without forking the production code path. The product is the same
binary in CI, in dev, in prod — only the env differs.

---

## 4. Where AI extensive use helped vs hurt

The grading rubric explicitly invites reflection on AI use. Honest read:

### What AI got right on the first try
- **Scaffolding.** Test files, fixtures, README structure, doc layouts —
  speedy and stylistically consistent.
- **Pattern recognition for the headline bugs.** The `enumerate` 500 and
  the radio-grouping bug were found because the AI wrote E2E and DOM-level
  tests *suspicious that the existing test-client suite was lying* — that
  framing came directly from prompting.
- **Honest gap documentation.** When AI didn't know how to automate
  something (screen-reader UX quality, real LLM evaluation), it
  consistently produced clear "why this can't be automated here" sections
  rather than fabricating coverage.

### What AI got wrong and had to iterate on
- **Flask-SQLAlchemy 3.x engine caching.** The first cut of the live-server
  launcher *thought* setting `app.config['SQLALCHEMY_DATABASE_URI']` after
  import would work. Required two hours of debugging — one of which was
  wasted on wrong hypotheses — before the debug print revealed the actual
  URI. A more senior reviewer would have caught it from reading the
  code. The lesson: AI's confidence does not correlate with correctness
  on framework-internal quirks.
- **Rate-limit math.** Token-bucket vs sliding-window analyses produced
  plausible-looking but wrong predictions about whether the test would
  flake. Empirical iteration (run the suite 5×) was needed.
- **Subprocess env inheritance.** `os.environ.setdefault` looked fine; the
  AI didn't initially reason about parent-env-inheritance interaction
  with the in-process conftest's "disable rate limit" setting.
- **Test ordering assumptions.** AI initially assumed alphabetical file
  order would let tests be naturally segregated. It does — until two test
  files in different alphabetical positions both need a session-scoped
  fixture and the order matters.

### What AI cannot do here, on principle, no matter the prompt
- **Judge whether AI feedback is pedagogically useful.** The injection-set
  and canary-set scaffolding in [test_ai_safety.py](test_ai_safety.py) are
  useful, but they can't replace a teacher's read of an explanation. AI
  can grade *itself* with rubric prompts; that does not make the rubric
  correct.
- **Judge screen-reader experience quality.** axe-class rules are
  decidable; *"does this `<legend>` announcement actually help a blind
  student understand the question?"* is not.
- **Find novel adversarial input.** Canned injection sets find the
  categories they were trained on. Genuinely novel attacks are
  out-of-distribution by definition.

These three are the contents of [MANUAL_TESTING_BEYOND_AUTOMATION.md](MANUAL_TESTING_BEYOND_AUTOMATION.md)
§3.P0 and §3.P1 — they are not "we'll automate this later." They are
"this is where the human's job is."

---

## 5. What I'd do differently next time

In order of value:

1. **Add the Docker-artifact smoke step to CI from day one.** Two of the
   three production bugs in this branch would have been caught by a
   single `docker compose up -d && curl /healthz && curl /` step before
   any specialised tests were written.
2. **Drive every configuration knob with an environment variable from
   day one.** Late retrofitting (as we did for `SQLALCHEMY_DATABASE_URI`,
   `RATE_LIMIT_*`, `MAX_CONTENT_LENGTH`) is expensive and frequently
   silently wrong (engine caching).
3. **Write the DOM-validation tests before the handler-validation tests.**
   The radio-grouping bug was caught by a test that asserted a property of
   the rendered page, not a property of the response when the test
   client submitted handcrafted form data. The handler tests passed; the
   DOM test caught the bug.
4. **Treat `setdefault` on inherited env vars as smell.** Direct assignment
   in subprocesses; or pass `env=` to Popen explicitly.
5. **Spend the first hour of debugging on observability, not hypotheses.**
   The engine-cache bug was a 30-second find with a single `before_request`
   print. I spent an hour on wrong hypotheses first.
6. **Document `xfail`s as a punch list, not as test-suite filler.** Every
   `xfail` should have a one-line "what fix flips it green" reason. The
   eight xfails this branch shipped at one point became a concrete product
   backlog the next commit closed.

---

## 6. The "AI-Native FAANG workflow" frame

The assignment positions this work as a mock of "AI-Native FAANG company
workflows." Pointed observations from that frame:

- **AI is good at producing the obvious 80%** — fixtures, structure,
  boilerplate test cases — at a speed no human can match.
- **The remaining 20% is what determines whether a customer pays.** That
  20% is also where AI is least reliable: framework-specific quirks
  (engine cache), non-deterministic external systems (real LLMs), and
  human-judgement areas (a11y experience, pedagogy).
- **The right human work shifts toward review, not authorship.** This
  project's most valuable human time was spent reading what AI produced
  with the *specific* question: "what is this confidently asserting that
  is actually false?" The engine-cache bug, the rate-limit
  inheritance bug, and the radio-grouping bug were all "AI wrote a thing
  that looked right and was wrong"; a careful reviewer caught each.
- **A green CI is necessary, not sufficient.** Two of the three
  production bugs in this branch shipped under green CI in earlier
  iterations. The bar for confidence is *"green CI **and** at least one
  test that exercises the path the user actually takes against the
  artifact we actually ship."*

That is the rule worth taking forward to any AI-Native project.
