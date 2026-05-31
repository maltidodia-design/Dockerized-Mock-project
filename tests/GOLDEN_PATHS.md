# Golden Paths — Most Valuable Test Scenarios

> Location: `tests/GOLDEN_PATHS.md`
> Companion to [tests/TEST_PLAN.md](TEST_PLAN.md) and [tests/TEST_STRATEGY.md](TEST_STRATEGY.md).

## Purpose

This document identifies the **Golden Paths**: the small set of user journeys that
carry essentially all of the product's value. If a Golden Path breaks, the
application is effectively useless even if every other test is green. They are the
journeys that *must* be protected by real end-to-end tests and watched first in
CI.

The analysis is grounded in the product's stated value
([product_requirements.md](../product_requirements.md)) — *"combine assessment
(quizzes) with teaching (AI feedback)"* — and the behaviour actually implemented
in [app.py](../app.py).

## What makes a path "golden"

A scenario is ranked by four factors:

| Factor | Question |
|---|---|
| **Value** | Does this journey *deliver the core promise* of the product? |
| **Frequency** | Will real users hit this on (almost) every visit? |
| **Blast radius** | If it fails, how much of the product is dead? |
| **Irreversibility / trust** | Does failure corrupt data or destroy user trust (e.g. wrong scores)? |

Golden Paths score high on all four. "Guardrail" scenarios (further below) score
high only on blast radius — they don't deliver value, they *protect* the value.

## The core value loop

Everything the MVP is worth lives in one loop:

```
  Author                         Learner
  ──────                         ───────
  GET  /create  ─┐
  POST /create  ─┤ quiz persists
                 ▼
  GET  /        ◄────────────────  quiz is discoverable
                 │
                 ▼
                 GET  /take/<id>   render questions
                 POST /take/<id>   submit answers
                       │
                       ├─ grade  (score must be correct)
                       ├─ persist Result
                       └─ POST /api/ai_feedback   (teach on wrong answers)
                       ▼
                 result.html   score + AI feedback
```

Break any arrow and the product stops being "assessment + teaching".

---

## Golden Paths (ranked)

### GP-1 — Full author→learner loop, answers correct

**Scenario.** A teacher creates a quiz; it appears on the home page; a learner
opens it, answers everything correctly, and sees a correct score and result page.

**Why golden.** This *is* the product. Highest value, highest frequency, total
blast radius — if this fails there is no working app.

**Steps.** `POST /create` → `GET /` (quiz listed) → `GET /take/<id>` (questions
render) → `POST /take/<id>` (all correct) → result page shows `Score: N / N`.

**Expected.** Quiz persisted and discoverable; take page renders a radio group
per question; `Score` equals total; all ✅, no ❌.

**Blast radius if broken.** 100% — nobody can create or complete a quiz.

**Coverage.** [tests/test_e2e.py](test_e2e.py) `test_e2e_full_quiz_journey_all_correct`
(E2E-002); also [tests/test_integration.py](test_integration.py),
[tests/test_routes.py](test_routes.py) at test-client level. Maps to TEST_PLAN
TP-002/004/005.

---

### GP-2 — Accurate grading on mixed answers

**Scenario.** A learner answers some questions wrong; the score reflects the
*exact* number correct and the result page marks each question right/wrong.

**Why golden.** An assessment tool that mis-scores is worse than no tool — it
destroys trust irreversibly (the high "trust" factor). Partial scoring is the
realistic, common case, not the all-correct one.

**Steps.** `POST /take/<id>` with a mix of correct/incorrect answers → result
shows `Score: k / n` with per-question ✅/❌.

**Expected.** `score` = count of correct; `total` = number of questions; a
`Result` row is persisted with matching `details_json`.

**Blast radius if broken.** Product still "runs" but is fundamentally untrust­worthy
— the worst kind of failure because it is silent.

**Coverage.** [tests/test_e2e.py](test_e2e.py)
`test_e2e_quiz_journey_with_wrong_answer_shows_feedback` (E2E-003);
[tests/test_edge_cases.py](test_edge_cases.py) `test_take_quiz_partial_answers`;
[tests/test_routes.py](test_routes.py). TEST_PLAN TP-005.

---

### GP-3 — AI feedback on incorrect answers

**Scenario.** After submitting wrong answers, the learner receives explanations
and improvement recommendations on the result page.

**Why golden.** This is the product's *differentiator* — PRD §5.2/§5.3: *"Explain
incorrect answers… Recommend topics for improvement."* Without it the app is just
a generic quiz, not the "AI-Powered Study Assistant".

**Steps.** `POST /take/<id>` (≥1 wrong) → server calls `POST /api/ai_feedback` →
result page renders an explanation list, not "No feedback available."

**Expected.** `explanations` non-empty for wrong answers; `recommendations`
includes a topic (e.g. `fundamentals`); result page shows the "AI Feedback"
section with "Review question …".

**Blast radius if broken.** The unique value proposition is gone; grading still
works, so failure is partial but strategically critical.

**Coverage.** [tests/test_e2e.py](test_e2e.py)
`test_e2e_quiz_journey_with_wrong_answer_shows_feedback` (E2E-003) and
`test_e2e_ai_feedback_api_over_http` (E2E-006);
[tests/test_routes.py](test_routes.py) `test_ai_feedback_with_incorrect_details`.
*Note:* the AI is a deterministic stub ([app.py](../app.py) `ai_feedback`); when a
real model replaces it this path needs contract/UX tests for non-deterministic
output (PRD §13).

---

### GP-4 — Quiz creation persists and is discoverable

**Scenario.** A valid quiz submitted via the create form is saved and immediately
listed on the home page for learners to find.

**Why golden.** The author half of the loop and the entry point for every learner
journey. High frequency for teachers; if discovery breaks, quizzes exist but are
unreachable (GP-1 becomes impossible).

**Steps.** `POST /create` (title + questions JSON) → redirect to `/` → new quiz
appears with a working `/take/<id>` link.

**Expected.** `Quiz` row persisted; title rendered on home; link resolves to a
200 take page.

**Blast radius if broken.** Authors cannot publish; the learner loop has no
content. Effectively total over time.

**Coverage.** [tests/test_e2e.py](test_e2e.py) `_create_quiz` helper exercised by
E2E-002/003; [tests/test_routes.py](test_routes.py)
`test_create_quiz_happy_path`; [tests/test_app.py](test_app.py)
`test_index_lists_quiz_after_creation`. TEST_PLAN TP-002.

---

### GP-5 — Primary flow is accessible (Section 508)

**Scenario.** Every page in the GP-1 loop (home, create, take, result) meets
baseline 508 expectations: a heading, labelled form controls, named
links/buttons.

**Why golden.** This is a **508 final project** — accessibility is a stated
acceptance criterion ([TEST_STRATEGY.md](TEST_STRATEGY.md)), not a nice-to-have.
An inaccessible golden path fails the project's core requirement even when
functionality is perfect.

**Steps.** Render `/`, `/create`, `/take/<id>`, result → assert `h1`, every
input/textarea has a label, buttons/links have accessible names.

**Expected.** No missing-label / unnamed-control violations on any primary page.

**Blast radius if broken.** Functionally fine but the project's headline
requirement is unmet — high value, project-defining.

**Coverage.** [tests/test_accessibility.py](test_accessibility.py)
(index / create / take / result). TEST_PLAN TP-007.

---

## Guardrail scenarios (protect the Golden Paths)

These deliver no value themselves; they ensure a bad input degrades *gracefully*
instead of taking down a Golden Path with a 500.

| ID | Scenario | Expected | Coverage |
|---|---|---|---|
| GR-1 | Unknown quiz id | `GET/POST /take/999999` → **404**, not a crash | E2E-004, [test_edge_cases.py](test_edge_cases.py) |
| GR-2 | Invalid questions JSON | `POST /create` bad JSON → **400** + message, author can recover | E2E-005, [test_routes.py](test_routes.py) |
| GR-3 | Missing/empty inputs | Missing title → "Untitled Quiz"; empty questions accepted | [test_edge_cases.py](test_edge_cases.py) |

---

## Coverage matrix

| Path | Value | Freq | Blast | E2E (real HTTP) | Test-client | Status |
|---|---|---|---|---|---|---|
| GP-1 Full loop, correct | ★★★ | ★★★ | Total | E2E-002 | integration/routes | ✅ Covered |
| GP-2 Accurate grading | ★★★ | ★★★ | Silent/Trust | E2E-003 | edge_cases/routes | ✅ Covered |
| GP-3 AI feedback (wrong) | ★★★ | ★★ | Strategic | E2E-003, E2E-006 | routes | ✅ Covered (stub) |
| GP-4 Create & discover | ★★★ | ★★ | Total (slow) | E2E-002/003 | routes/app | ✅ Covered |
| GP-5 508 accessibility | ★★★ | ★★★ | Project-defining | — | accessibility | ✅ Covered (test-client) |
| GR-1/2/3 Guardrails | — | ★ | Protective | E2E-004/005 | edge_cases | ✅ Covered |

---

## Case study: why Golden-Path E2E matters

GP-1 contains `GET /take/<id>`. The test-client suites all passed on it, yet the
**real server returned HTTP 500** there: [take_quiz.html](../templates/take_quiz.html)
calls `enumerate()`, which Jinja2 does not expose by default. The unit/integration
tests only passed because [tests/conftest.py](conftest.py) injects `enumerate`
into Jinja globals — an injection that never runs under `gunicorn` /
`python app.py`.

A green test suite reported a Golden Path that was, in production, completely
broken — *taking any quiz crashed*. Only a test that exercises the real path over
real HTTP ([tests/test_e2e.py](test_e2e.py) E2E-002/003) catches this class of
defect. This is the central justification for maintaining E2E coverage on every
Golden Path, not just unit coverage. (Fixed in [app.py](../app.py) by registering
the Jinja global.)

**Rule of thumb:** every Golden Path must have at least one test that runs against
the real running app, not only the in-process test client.

---

## Not yet golden — gaps & future paths

The PRD describes value the MVP has **not implemented**; these become Golden Paths
the moment they ship and currently have *no* coverage by design:

- **Authentication & roles** (PRD §5.4, §11) — no login exists in [app.py](../app.py).
  When added, "Login → create/take → feedback" becomes the top Golden Path
  (PRD §9 explicitly names this as the E2E scenario).
- **AI practice-question generation** (PRD §5.2) — not implemented.
- **Real (non-deterministic) AI** (PRD §13) — GP-3 currently tests a deterministic
  stub. A real model needs contract tests (shape/latency) and UX assertions, not
  exact-string matches.
- **Concurrency / load** (PRD §9) — multiple simultaneous takers untested.

These are listed so the Golden-Path set is revisited whenever the product scope
grows — the matrix above is a living artifact, not a one-time analysis.
