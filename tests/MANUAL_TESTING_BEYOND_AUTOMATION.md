# Manual Testing Required On Top of Automated Tests

Purpose: define the manual testing that **still must be done** once the automated
suite (unit + integration + the new real-HTTP E2E suite + accessibility) has run.
This is a *coverage-gap* plan — it deliberately does **not** re-list things
automation already proves; it focuses on what automation here structurally
**cannot** or **does not** cover.

Relationship to other docs:
- [manual-tests-checklist.md](../manual-tests-checklist.md) — general manual
  procedures (kept). This document is the **prioritised, gap-driven** plan that
  sits on top of it and the automated suite.
- [GOLDEN_PATHS.md](GOLDEN_PATHS.md) — the value-ranked journeys referenced below.
- [VALIDATION_OF_AUTOMATED_E2E_TESTS.md](VALIDATION_OF_AUTOMATED_E2E_TESTS.md) —
  evidence of what the automation actually validated.

---

## 1. What automation already covers (do NOT manually re-test)

| Area | Automated by | Confidence |
|---|---|---|
| Create → list → take → score → result (GP-1/2/4) | [test_e2e.py](test_e2e.py) E2E-002/003, integration/routes | High (real HTTP) |
| Correct/partial scoring math | E2E-003, [test_edge_cases.py](test_edge_cases.py) | High |
| AI feedback *wiring* (endpoint reachable, shape) | E2E-003/006, [test_routes.py](test_routes.py) | High |
| Unknown quiz id → 404, bad JSON → 400 (GR-1/2) | E2E-004/005, edge cases | High |
| Basic 508: `h1`, input labels, named links/buttons | [test_accessibility.py](test_accessibility.py) | Partial only |

Manual effort spent re-checking the above is wasted. Spend it on Section 2+.

---

## 2. Why manual testing is still required

Automation here has hard limits, and validation already proved over-trust is
dangerous: the automated test-client suite was **fully green while a core Golden
Path returned HTTP 500 on the real server** (the `enumerate` bug — see
[VALIDATION_OF_AUTOMATED_E2E_TESTS.md](VALIDATION_OF_AUTOMATED_E2E_TESTS.md)).
Lesson: a green suite is necessary, not sufficient. The categories below are
where humans must still look.

---

## 3. Prioritised manual test plan

Priority: **P0** = must pass before merging to `main` / releasing. **P1** = before
release. **P2** = periodic / exploratory.

### P0-1 — Real deployment smoke (Docker / gunicorn)

**Why manual / why automation misses it.** The automated E2E suite runs the app
under werkzeug in a subprocess with a temp DB. The *actual* deployment artifact
is `gunicorn` via [docker-compose.yml](../docker-compose.yml) with the real
SQLite file — a **different run path**. The enumerate-class bug was exactly a
path-dependent failure. Automation does not exercise the shipped artifact.

- [ ] `docker compose up --build`, open the app in a browser.
- [ ] Walk GP-1 end to end by hand: create a quiz → see it on home → take it →
      submit → result + AI feedback render.
- [ ] Walk GP-2: submit with some wrong answers; confirm score and ✅/❌.
- [ ] Restart the container; confirm previously created quizzes/results persist
      (real `instance/data.db`, not the temp DB automation uses).

**Expected:** every Golden Path works on the real gunicorn/Docker artifact, no
500s, data persists across restarts.

### P0-2 — AI feedback quality (non-deterministic content)

**Why manual.** Automation can only assert the feedback *exists and has the right
shape*. It cannot judge whether the content is *correct, relevant, and
appropriately toned* (PRD §5.3, §13). When the mock is replaced by a real model
this becomes essential.

- [ ] Take a quiz, miss specific questions. Does the feedback address **those**
      questions, not generic filler?
- [ ] Is the tone encouraging/educational, per [product_requirements.md](../product_requirements.md) §5?
- [ ] Are recommendations sensible for the quiz's actual subject?
- [ ] Sample several quizzes/answer patterns (non-deterministic → sample, don't
      assert once).

### P0-3 — Section 508 manual audit (beyond label/heading checks)

**Why manual.** [test_accessibility.py](test_accessibility.py) only checks for an
`h1`, input labels, and named links/buttons. Automated tooling catches ~30–40%
of 508 issues. This is a **508 project** — the rest must be human-verified.

- [ ] **Keyboard only:** Tab through home, create, take, result. Order logical,
      nothing trapped, quiz submittable with Enter/Space.
- [ ] **Visible focus:** every link, button, and radio shows a clear focus ring.
- [ ] **Screen reader** (VoiceOver/NVDA): on the result page, are ✅/❌ announced
      meaningfully? (icons currently have no `aria-label` — likely a finding).
- [ ] **Semantic structure:** content uses real landmarks, not just
      `div.container`; `<title>` changes per page and is announced.
- [ ] **Error announcement:** the "Invalid questions JSON" 400 page is reachable
      and understandable with a screen reader.

### P1-1 — Cross-browser & responsive / visual

**Why manual.** No browser engine or visual rendering in the automated suite.

- [ ] Functionality + layout in Chrome, Firefox, Safari (incl. iOS), Edge.
- [ ] Mobile/tablet widths: container and the large `textarea` on
      [create_quiz.html](../templates/create_quiz.html) scale without horizontal
      scroll.
- [ ] Very long quiz titles / question text wrap instead of breaking layout.
- [ ] Hover/focus states are visually clear.

### P1-2 — AI service failure / degradation

**Why manual.** The automated path always has the in-process stub available;
real network failure of an external AI service is not simulated.

- [ ] Simulate the AI call failing/timing out. Confirm the result page still
      loads gracefully with a "feedback unavailable" style message (per
      [app.py](../app.py) it should not 500).

### P1-3 — Concurrency & double-submit

**Why manual.** The automated suite is single-process and sequential.

- [ ] Rapidly double-click "Submit" on a quiz — are duplicate `Result` rows
      created? Note behaviour (idempotency is a known risk).
- [ ] Two browsers taking/creating quizzes at the same time behave sanely.

### P2-1 — Input robustness & security (exploratory)

**Why manual / important.** Quiz title and question text are user-supplied and
rendered into HTML; answers are cast with `int()` server-side.

- [ ] Enter HTML/script in a quiz **title** and **question text** (e.g.
      `<script>alert(1)</script>`); take the quiz and view result. Confirm it is
      escaped, not executed (stored-XSS check; PRD §11).
- [ ] Tamper a submitted answer to a non-integer value (e.g. via devtools) — the
      `int()` cast can raise and produce a 500 (see
      [test_edge_cases.py](test_edge_cases.py) `test_take_quiz_non_int_answer_raises`).
      Record actual real-server behaviour.
- [ ] Quiz JSON with missing `choices` / wrong key names (`ans_idx`) / 50+
      questions — system stays responsive and does not corrupt data.
- [ ] Unicode / very long strings in titles and questions persist and render
      correctly.

### P2-2 — Navigation & state

- [ ] Browser Back/Forward during a quiz, and re-submitting via Back — predictable
      behaviour, no confusing duplicate results.
- [ ] Direct-URL access to `/take/<id>` for a deleted/never-existing quiz behaves
      (404, not crash) in a real browser session.

---

## 4. Pre-release manual gate (mandatory minimum)

Before merging to `main` / releasing, **these must be signed off** even under
time pressure:

- [ ] **P0-1** Docker/gunicorn smoke of GP-1 + GP-2 (the artifact users actually get)
- [ ] **P0-2** AI feedback sampled and judged relevant/appropriate
- [ ] **P0-3** Keyboard-only pass + one screen-reader pass of the primary flow

Rationale: P0-1 directly guards the failure class that automation provably
missed; P0-2 and P0-3 guard the product's two defining promises (AI tutoring +
508 compliance) that automation cannot judge.

---

## 5. Recording results

Follow the convention in [manual-tests-checklist.md](../manual-tests-checklist.md)
§6. For each executed case record:

| Field | Example |
|---|---|
| Date | 2026-05-17 |
| Environment | Docker (gunicorn) / Chrome 124 / macOS |
| Case ID | P0-1 |
| Status | Pass / Fail |
| Notes / Bug | Steps to reproduce + screenshot if Fail |

File completed reports next to this plan (e.g. `tests/manual-run-YYYY-MM-DD.md`)
and link any defects found. A failed **P0** blocks release.

---

## 6. Sign-off

| Gate | Owner | Status |
|---|---|---|
| P0-1 Deployment smoke | QA / Dev | ☐ |
| P0-2 AI feedback quality | QA / Subject reviewer | ☐ |
| P0-3 508 manual audit | Accessibility lead | ☐ |
| P1 set | QA | ☐ |
| Release approved | Maintainer | ☐ |
