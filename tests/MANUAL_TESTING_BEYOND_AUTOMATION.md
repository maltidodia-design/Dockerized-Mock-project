# Manual Testing Required On Top of Automated Tests

Purpose: define the manual testing that **still must be done** once the
automated suite (unit + integration + E2E + the four specialized suites + the
two CI scanners) has run. This is a *coverage-gap* plan — it deliberately
does **not** re-list things automation already proves; it focuses on what
automation here structurally **cannot** or **does not** cover.

Relationship to other docs:
- [manual-tests-checklist.md](../manual-tests-checklist.md) — general manual
  procedures (kept). This document is the **prioritised, gap-driven** plan
  that sits on top of it and the automated suite.
- [AI_GENERATED_SPECIALIZED_TESTS.md](AI_GENERATED_SPECIALIZED_TESTS.md) —
  what was automated and the honest inventory of what was not.
- [GOLDEN_PATHS.md](GOLDEN_PATHS.md), [PRODUCTION_ISSUES.md](PRODUCTION_ISSUES.md),
  [CONFIGURATION_MATRIX.md](CONFIGURATION_MATRIX.md) — context.

---

## 1. What automation now covers (do NOT manually re-test)

After the product update that closed the 8 known gaps, automation covers
quite a lot. Manual effort spent re-checking the rows below is wasted.

| Area | Automated by | Confidence |
|---|---|---|
| Create → list → take → score → result (GP-1/2/4) | [test_e2e.py](test_e2e.py) E2E-002/003 | High (real HTTP) |
| Correct/partial scoring math | E2E-003, [test_edge_cases.py](test_edge_cases.py) | High |
| Form tampering (non-integer answer) gracefully handled | [test_security.py](test_security.py), [test_edge_cases.py](test_edge_cases.py) | High |
| Unknown quiz id → 404, bad JSON → 400 (GR-1/2) | E2E-004/005 | High |
| `/healthz` liveness | `test_e2e_healthz_endpoint` | High |
| Stored-XSS escape on **home / take / result** pages | [test_security.py](test_security.py) | High |
| Cross-origin CSRF rejection | [test_security.py](test_security.py) | High (Origin-based) |
| Security response headers (XCTO, XFO, CSP, Referrer) | [test_security.py](test_security.py) | High |
| AI feedback API: schema, robustness, injection-non-echo, leak canaries, rate-limit 429 | [test_ai_safety.py](test_ai_safety.py) | High **against the stub** — see P0-2 |
| Concurrency: N concurrent submissions → no 5xx, no lost writes | [test_performance.py](test_performance.py) | Medium (single-process) |
| HTML `lang`, page title, heading order, duplicate ids, fieldset/legend | [test_a11y_extended.py](test_a11y_extended.py) | High (static rules) |
| Static security analysis | Bandit in CI | High (within the rule set) |
| Dependency CVEs | pip-audit in CI | High (declared deps only) |

---

## 2. Why manual testing is still required

Even with the gaps closed, three classes of failure remain that automation
*here* cannot decide:

1. **The shipped artifact diverged from what we tested.** This product has
   already produced **three** "tests-green-yet-broken" bugs in this branch:
   `enumerate` undefined under the real server, broken radio grouping, and a
   Flask-SQLAlchemy engine cached at import time that made every "in-memory"
   test silently use the real DB. The pattern repeats. The first run of any
   shipped artifact needs a human walk-through.
2. **Quality of model behaviour and screen-reader experience.** Automation
   can verify *presence*; only a human can verify *quality*.
3. **Novel adversarial input.** A canned injection set catches its own
   categories; truly new attacks need exploratory testing.

---

## 3. Prioritised manual test plan

Priority: **P0** = must pass before merging to `main` / releasing. **P1** =
before release. **P2** = periodic / exploratory.

### P0-1 — Real deployment smoke (Docker / gunicorn)

**Why manual / why automation misses it.** The automated E2E suite still
runs under werkzeug in a subprocess with a temp DB. The deployment artifact
is `gunicorn` via [docker-compose.yml](../docker-compose.yml). Three of the
five real production bugs found in this branch were path-dependent; this
gap remains until a CI Docker-smoke step is added (see
[AI_GENERATED_SPECIALIZED_TESTS.md](AI_GENERATED_SPECIALIZED_TESTS.md) §2.2).

- [ ] `docker compose up --build`, open the app in a browser.
- [ ] Walk GP-1 end to end: create → see it on home → take → submit →
      result + AI feedback render.
- [ ] Walk GP-2: submit with some wrong answers; score and ✅/❌ correct.
- [ ] Hit `/healthz` directly — should respond fast, no DB hit.
- [ ] Restart the container; confirm previously created quizzes/results
      persist on the real `instance/data.db` (not the test temp DB).
- [ ] Confirm the response carries the security headers
      (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
      `Content-Security-Policy: default-src 'self'`, `Referrer-Policy`).

### P0-2 — AI feedback quality (non-deterministic content)

**Why manual.** Automation asserts the feedback *exists and has the right
shape and resists known injection patterns*. It cannot judge whether the
content is *correct, relevant, age-appropriate, or pedagogically useful*
(PRD §5.3, §13). The harness in [test_ai_safety.py](test_ai_safety.py)
becomes load-bearing the day a real LLM replaces the stub; until then this
P0 verifies what no test can.

- [ ] Take a quiz, miss specific questions. Does the feedback address
      **those** questions, not generic filler?
- [ ] Is the tone encouraging/educational?
- [ ] Are recommendations sensible for the quiz's actual subject?
- [ ] Sample several quizzes/answer patterns — output is non-deterministic,
      so sample, don't rely on one example.

### P0-3 — Section 508 manual audit (beyond conformance rules)

**Why manual.** The new [test_a11y_extended.py](test_a11y_extended.py)
already covers what static tooling can decide: `lang`, page title, heading
order, dup ids, fieldset/legend, radio name grouping. The rest is human:
focus order, screen-reader announcement quality, forced-colors visibility.

- [ ] **Keyboard only.** Tab through `/`, `/create`, `/take/<id>`, result.
      Logical order. Nothing trapped. Submit via Enter / Space.
- [ ] **Visible focus.** Every link, button, radio shows a clear focus ring.
- [ ] **Screen reader** (VoiceOver / NVDA / JAWS depending on platform):
  - The `<legend>` is announced as the question and the radios are
    announced as a group.
  - ✅ / ❌ on the result page communicate result — currently these are
    Unicode glyphs with no `aria-label`. A real screen-reader will read
    them; the question is *whether what it reads is useful*.
  - `<title>` changes per page.
- [ ] **Forced-colors mode** (Windows): all interactive elements keep a
      visible boundary; `Content-Security-Policy: default-src 'self'` does
      not break our stylesheet.

### P0-4 — Content Security Policy (CSP) doesn't break the UI

**Why manual.** The new `Content-Security-Policy: default-src 'self'`
header is broad and aggressive. Any inline `<style>`, inline `<script>`,
`onclick=` handler, `eval()`, or third-party asset will be blocked by the
browser. Automation cannot tell you whether the page *looks right*; only a
human can.

- [ ] In Chrome / Safari / Firefox, open every page and **check the
      browser console** for CSP violations.
- [ ] Confirm `/static/style.css` loads (it's same-origin, so it should).
- [ ] If anything is broken, decide between: relax CSP, move inline to
      external file, or add a hash/nonce — and re-test.

---

### P1-1 — Cross-browser & responsive / visual

**Why manual.** No browser engine in CI. The same fieldset/legend refactor
that fixed the a11y test renders differently across browsers; verify it
still looks acceptable.

- [ ] Functionality + layout in Chrome, Firefox, Safari (incl. iOS), Edge.
- [ ] Mobile / tablet widths — container + the large `<textarea>` in
      [create_quiz.html](../templates/create_quiz.html) scale without
      horizontal scroll.
- [ ] Very long quiz titles / question text wrap rather than break layout.
- [ ] Hover / focus states are visually clear.
- [ ] **New:** `<fieldset>` default browser styling (border, padding) is
      acceptable, or replace with utility CSS.

### P1-2 — AI service failure / degradation

**Why manual.** `take_quiz` now catches exceptions from
`_generate_ai_feedback` and shows `{'error': 'feedback unavailable'}`. With
a real model wired in, network failure / timeout paths must be smoke-tested
end-to-end: the user must still see their score and result page.

- [ ] Simulate the AI call failing / timing out (env-var kill switch, or
      block the provider in firewall). Confirm result page renders
      gracefully with "No feedback available."

### P1-3 — Rate-limit UX

**Why manual.** Automation verifies the 429 fires
([test_ai_safety.py](test_ai_safety.py) `test_rate_limit_returns_429_under_burst`).
It does **not** judge whether a real user understands what's happening when
their feedback request is throttled.

- [ ] Trigger rate-limit (lower `RATE_LIMIT_MAX` in dev to do this easily).
      Does the user see a sensible error, or does the result page silently
      drop AI feedback?
- [ ] Are the limits sensible for an exam-day burst — 30 students
      submitting in 90 seconds should *not* be rate-limited.

### P1-4 — Concurrency in a real browser

**Why manual.** [test_performance.py](test_performance.py) covers
*server-side* concurrency. Browser-side double-clicks / Back-and-resubmit
behaviour is a different concern.

- [ ] Rapidly double-click "Submit". Are duplicate `Result` rows created?
- [ ] Browser **Back** after submission and re-submit. Behaviour
      predictable, no confusing duplicate result?
- [ ] Two browsers / two tabs taking the same quiz simultaneously — both
      land on their own result page.

---

### P2-1 — Adversarial / exploratory security

**Why manual.** The automated set covers known canonical attacks. Novel
attacks by definition aren't in any test set.

- [ ] HTML / script in quiz **title**, **question text**, **choice text**
      (already automated for echo-escape — exploratory means looking for
      *new* sinks: response headers, redirect targets, etc.).
- [ ] Tamper the form `name` attribute (e.g. send `question-99`) — does
      anything blow up?
- [ ] Submit JSON with extra/missing keys, deeply nested structures, very
      long strings.
- [ ] Unicode, RTL, control characters, NULs in titles and questions
      persist and render correctly.
- [ ] Try the **CSRF Origin check** edge cases: missing Origin header,
      mismatched scheme, IPv6 literal host, port mismatch.

### P2-2 — Navigation, sessions, browser features

- [ ] Browser back/forward during a quiz.
- [ ] Page reload mid-quiz — answers lost; acceptable today, but a known
      UX gap when sessions/auth ships.
- [ ] Direct-URL access to a quiz that was deleted (when deletion ships).

### P2-3 — Compliance pre-flight (when relevant features land)

Currently unimplemented; listed so this plan is the home for that work
when it arrives:

- [ ] **GDPR/CCPA**: data export and deletion paths exist and work.
- [ ] **COPPA**: age gate + parental-consent flow before child accounts.
- [ ] **AI Act §50**: "you are interacting with AI" disclosure on result
      page.
- [ ] **FERPA**: school-IdP integration; admin access logging.
- [ ] **VPAT/ACR**: filled in after the P0-3 audit.

---

## 4. Pre-release manual gate (mandatory minimum)

Before merging to `main` / releasing, **these must be signed off** even
under time pressure:

- [ ] **P0-1** Docker / gunicorn smoke of GP-1, GP-2, `/healthz` and the
      security headers (the artifact users actually get).
- [ ] **P0-2** AI feedback sampled and judged relevant / appropriate.
- [ ] **P0-3** Keyboard-only pass + one screen-reader pass of the primary
      flow.
- [ ] **P0-4** No CSP violations in the browser console on any page.

Rationale: P0-1 directly guards the failure class that automation has
provably missed three times in this branch; P0-2 and P0-3 guard the
product's two defining promises (AI tutoring + 508 compliance) that
automation cannot judge; P0-4 is the gate that catches the
**self-inflicted** breakage the strict CSP can cause if any inline
asset appears.

---

## 5. Recording results

Follow the convention in [manual-tests-checklist.md](../manual-tests-checklist.md)
§6. For each executed case record:

| Field | Example |
|---|---|
| Date | 2026-05-31 |
| Environment | Docker (gunicorn) / Chrome 124 / macOS 14 |
| Case ID | P0-1 |
| Status | Pass / Fail / Waived |
| Notes / Bug | Steps to reproduce + screenshot if Fail |

File completed reports next to this plan
(e.g. `tests/manual-run-YYYY-MM-DD.md`) and link any defects found.
A failed **P0** blocks release.

---

## 6. Sign-off

| Gate | Owner | Status |
|---|---|---|
| P0-1 Deployment smoke (Docker + headers + healthz) | QA / Dev | ☐ |
| P0-2 AI feedback quality | QA / Subject reviewer | ☐ |
| P0-3 508 manual audit (keyboard + screen reader) | Accessibility lead | ☐ |
| P0-4 CSP doesn't break the UI | Front-end / QA | ☐ |
| P1 set | QA | ☐ |
| Release approved | Maintainer | ☐ |
