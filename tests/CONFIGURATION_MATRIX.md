# Test Configuration Matrix

Purpose: define **every configuration** the product should be exercised in
before release — browsers, devices, operating systems, assistive
technologies, network conditions, server environments — and split them into
tiers so the test plan is finite, prioritised, and auditable.

Companion to [GOLDEN_PATHS.md](GOLDEN_PATHS.md),
[MANUAL_TESTING_BEYOND_AUTOMATION.md](MANUAL_TESTING_BEYOND_AUTOMATION.md),
and [PRODUCTION_ISSUES.md](PRODUCTION_ISSUES.md).

**Scope reality check.** The audience is EdTech: K-12 schools, universities,
self-learners. That biases the matrix toward Chromebooks, iPads, JAWS/NVDA,
slow filtered networks, and older managed devices — *not* the latest
flagship hardware.

---

## 1. How to read this document

Each table uses three tiers:

| Tier | Meaning | Cadence |
|---|---|---|
| **P0** | Must pass before any release. Block merge. | Every PR (where automatable) + pre-release manual gate |
| **P1** | Must pass before public release. | Nightly / pre-release |
| **P2** | Periodic / opportunistic; capture issues but don't block. | Monthly or per-feature |

Each row lists what changes between configurations and what *specifically*
to test in that combination — not just "test the app" but the **failure
modes** that configuration tends to surface.

---

## 2. Browsers

Source of truth for what schools and students actually use: NetMarketShare /
StatCounter education segment + GSA browser-share for public-sector users.
Bias toward Chromium and Safari; Firefox cannot be skipped for a11y
(JAWS/NVDA reference combinations rely on it).

| Tier | Browser | Versions | Why this matters here |
|---|---|---|---|
| **P0** | Chrome | latest, latest-1 | Default school-issued Chromebook browser; ~60% education share |
| **P0** | Safari | latest macOS + iOS | The only engine on iPads (WebKit-only iOS); large elementary share |
| **P0** | Firefox | latest ESR + latest | Reference pairing for NVDA screen reader testing |
| **P1** | Edge | latest | Default on Windows-managed school devices; JAWS reference pair |
| **P1** | Samsung Internet | latest | Default on Samsung Android tablets used in some districts |
| **P2** | Older Chrome | n-3, n-4 | Chromebooks past their auto-update horizon (still in classrooms) |
| **P2** | Brave / Firefox Focus | latest | Privacy-tracker testing; some cookies/third-party blocks affect SSO |

**What to test per browser** — the four Golden Path pages, form submission,
JS-free fallback (the app currently uses no JS but verify CSP/no-JS still
renders), and one a11y pass.

---

## 3. Operating systems (client side)

| Tier | OS | Versions | Notes specific to EdTech |
|---|---|---|---|
| **P0** | ChromeOS | latest stable + LTS channel | Dominant K-12 device; tabbed-only environment, limited extension support |
| **P0** | macOS | latest + latest-1 | Teacher laptops, university defaults; VoiceOver baseline |
| **P0** | iPadOS / iOS | latest + latest-1 | iPad classrooms (elementary); Safari-only; touch-first input |
| **P0** | Windows | 10, 11 | District-issued laptops; default for Edge + JAWS pairing |
| **P1** | Android | 13, 14, 15 | Tablet rollouts in some districts; Samsung Internet default |
| **P2** | Linux | Ubuntu 22.04 LTS + 24.04 | Some uni labs, developer machines, accessibility check |

---

## 4. Devices and screen sizes (responsive)

Quizzes are taken on whatever device a student has — including older,
small-screen, low-spec hardware. **Don't optimise only for desktop.**

| Tier | Class | Width × DPR | Representative device | Specific risks |
|---|---|---|---|---|
| **P0** | Small phone | 360×640 @ 2 | iPhone SE, low-end Android | Long quiz titles overflow; sticky keyboard hides the submit button |
| **P0** | Standard phone | 390×844 @ 3 | iPhone 13/14/15 | Touch target size on radio buttons |
| **P0** | Small tablet | 768×1024 @ 2 | iPad mini, 9th-gen iPad | School-rollout default; portrait/landscape switching |
| **P0** | Laptop | 1366×768 @ 1 | Chromebook | Default school device; verify nothing is cut off |
| **P0** | Desktop | 1920×1080 @ 1 | Teacher monitors | Large textarea on `/create` doesn't blow out the page |
| **P1** | Large tablet | 1024×1366 @ 2 | iPad Pro 11" | Multi-column layout regressions |
| **P1** | 4K desktop | 3840×2160 @ 1 | Newer faculty hardware | Type rendering, focus-ring visibility |
| **P2** | Tiny / wearable | 320×480 | Old smartphones still in K-12 | Hard but worth one manual check |

**Specific test areas:** the `<textarea>` in [create_quiz.html](../templates/create_quiz.html)
(known overflow risk), long question/choice text wrapping, focus rings under
mouse vs. keyboard, on-screen-keyboard hiding form submit.

---

## 5. Assistive technologies (508 critical)

This is the **defining requirement** of the project. Each AT/browser
combination is a separate test target because issues are pair-specific
(JAWS+Edge ≠ JAWS+Chrome, etc.).

| Tier | AT + browser | Platform | Specific things to verify |
|---|---|---|---|
| **P0** | VoiceOver + Safari | macOS, iOS | Reads quiz title, question, then choice labels; announces ✅/❌; landmark navigation |
| **P0** | NVDA + Firefox (and Chrome) | Windows | Form mode entry/exit on radios; reads result page correctly |
| **P0** | JAWS + Edge (and Chrome) | Windows | Reference combination for K-12 districts that licence JAWS |
| **P0** | Keyboard-only (no AT) | All | Tab order across all four Golden Path pages; visible focus; Submit via Enter |
| **P0** | High-contrast / Forced Colors | Windows + browser | Buttons, radios, links still visible when system forces colors |
| **P1** | TalkBack + Chrome | Android | Reading order, swipe navigation |
| **P1** | VoiceOver + Chrome | iOS | Some iPads default Chrome via MDM |
| **P1** | Browser zoom 200% / 400% | All | Layout reflow without horizontal scroll (WCAG 1.4.10) |
| **P1** | Dragon NaturallySpeaking | Windows | Voice control: "click Submit" must work |
| **P2** | ZoomText / Magnifier | Windows | Focus tracking under magnification |
| **P2** | Read&Write / Co:Writer | Chromebook | Common K-12 reading-aid extensions; should not break form |

---

## 6. User-agent accessibility / system settings

Browsers and OSes expose preferences that the page should respect.

| Tier | Setting | What to verify |
|---|---|---|
| **P0** | OS-level larger text (125–200%) | Layout reflows; nothing clipped |
| **P0** | Prefers reduced motion | No animation (none today; lock it in for the future) |
| **P0** | Forced-colors mode (Windows) | All interactive elements keep visible boundary |
| **P0** | Dark mode (OS) | If site adopts `prefers-color-scheme`, contrast holds |
| **P1** | Custom font (user stylesheet) | Layout doesn't collapse |
| **P1** | Color-filter (color-blind simulation) | Status colors (✅/❌) communicate via more than colour |
| **P2** | Reduced data / Data Saver | Pages still functional with images stripped |

---

## 7. Network conditions

EdTech is bandwidth-constrained: school Wi-Fi is throttled, CIPA-filtered,
and rural users have inconsistent connections.

| Tier | Profile | Why test it |
|---|---|---|
| **P0** | Fast Wi-Fi (50 Mbps + ≤30 ms) | Baseline |
| **P0** | School Wi-Fi (10 Mbps, 100 ms RTT, packet loss <1%) | Realistic representative |
| **P0** | Slow 3G (1 Mbps, 300 ms RTT) | Many rural learners; submit page should not time out |
| **P1** | Flaky / lossy (5% packet loss) | Form re-submit behaviour; ensure no duplicate `Result` rows |
| **P1** | Captive portal (login required) | App should fail gracefully before submit |
| **P1** | Behind a strict content filter | Some districts strip cookies / block third-party requests — relevant when AI is wired to an external provider |
| **P2** | Offline mid-quiz | Confirm what happens to in-progress answers |

---

## 8. Backend / server environment

Each combination here is a *deployment* configuration. The product must be
tested against the artifact that actually ships, not just the dev setup.

| Tier | Environment | Specific risk |
|---|---|---|
| **P0** | Docker (gunicorn, 1 worker) | Default release artifact; smoke all Golden Paths against the built image |
| **P0** | Python 3.10 (CI target) | What CI runs on |
| **P0** | Python 3.11 (Dockerfile base) | What the image runs |
| **P0** | SQLite (current backend) | Concurrency / "database is locked" risk under multi-worker — see [PRODUCTION_ISSUES.md](PRODUCTION_ISSUES.md) §4 |
| **P1** | Python 3.12 / 3.13 | Forward-compat smoke |
| **P1** | Docker with 2+ gunicorn workers | Surface the known SQLite lock bug deliberately |
| **P1** | Postgres backend (post-migration) | Once switched, regression-test all Golden Paths |
| **P1** | Behind a reverse proxy (nginx/Cloudflare) | `X-Forwarded-*` handling; HTTPS termination; large-payload limits |
| **P2** | Different time zones (TZ=America/Los_Angeles, Asia/Tokyo, UTC) | `created_at` display |
| **P2** | Locale variations (LANG=es_ES.UTF-8, ar_SA.UTF-8) | Date formatting; RTL preparation |

---

## 9. Data / load profiles

| Tier | Profile | Why test it |
|---|---|---|
| **P0** | 1 quiz, 1 question | Smallest happy path |
| **P0** | 1 quiz, 50 questions | Realistic exam length |
| **P0** | 100 existing quizzes on home | Home page unbounded-list risk |
| **P1** | 1 question, 20 choices | Long radio group rendering |
| **P1** | Unicode (emoji, CJK, Arabic, accents) in title/text/choices | Encoding round-trip, RTL prep |
| **P1** | Large content in fields (HTML escaped) | Stored-XSS protection holds (already in [test_security.py](test_security.py)) |
| **P1** | 200 concurrent submissions (load) | SQLite lock + sync internal HTTP-to-itself bug |
| **P2** | 10 000-quiz database | Index performance |

---

## 10. User roles & sessions (when auth ships)

Currently no auth (anonymous). Once roles land per PRD §5.4 the matrix
expands:

| Tier | Persona | Things to verify |
|---|---|---|
| **P0** | Anonymous | Reasonable behaviour or blocked, depending on policy |
| **P0** | Student | Cannot access teacher routes; cannot view other students' results |
| **P0** | Teacher | Cannot escalate to admin; can view students' results per FERPA scope |
| **P1** | Admin | Audit logs, role-management UI |
| **P1** | SSO via school IdP (SAML/OIDC) | Federation works in Chrome, Safari, Edge — third-party cookie limits matter |
| **P2** | Parent (COPPA flow) | Consent capture before child-account creation |

---

## 11. AI provider / model configuration (when real model ships)

| Tier | Variation | Risk |
|---|---|---|
| **P0** | Primary model (e.g. claude-sonnet-4-6) | Behaviour baseline; golden-dataset eval |
| **P0** | Primary model + safety filters on | Refusal handling |
| **P1** | Fallback model / provider | Failover path |
| **P1** | Model returning timeout / 5xx | "Feedback unavailable" path |
| **P1** | Prompt injection set (OWASP LLM Top 10) | Output schema holds |
| **P2** | Reduced-cost model (e.g. Haiku) | Quality degradation acceptable on hot path |

---

## 12. Localisation (when i18n ships)

Currently English only.

| Tier | Locale | Reason |
|---|---|---|
| **P1** | es-MX, es-US | Largest US bilingual education segment |
| **P1** | en-GB | UK quote / date formatting |
| **P1** | RTL pseudo-locale (e.g. `ar-XB`) | Catch layout that doesn't flip |
| **P2** | zh-CN, ja, fr, de | Future markets |

---

## 13. Compressed matrix at a glance

What *must* be on the test matrix the day this product is called
"releasable" — pulled from the P0 rows above:

| Layer | Configurations |
|---|---|
| Browsers | Chrome (latest, n-1), Safari (macOS + iOS), Firefox (ESR + latest), Edge (latest) |
| OS | ChromeOS, macOS, iPadOS, Windows |
| Form factors | 360-px phone, 768-px tablet, 1366-px Chromebook, 1920-px desktop |
| Assistive | VoiceOver+Safari, NVDA+Firefox, JAWS+Edge, keyboard-only, forced-colors |
| Network | Fast Wi-Fi, school Wi-Fi (10 Mbps + 100 ms), slow 3G |
| Server | Docker gunicorn artifact, Python 3.10 + 3.11, SQLite |
| Data | 1 question, 50 questions, 100 quizzes on home, unicode content |

That's ~40 cells. Don't multiply naively — test the **product against each
dimension once** holding others at baseline, and add a small number of
**multi-axis combos** for the highest-risk intersections (e.g.
NVDA + Firefox + slow 3G + 50-question quiz).

---

## 14. What's already automated vs gap

| Dimension | Automated today | Gap |
|---|---|---|
| Browsers | None (no headless browser in CI) | All — add Playwright (Chromium + WebKit + Firefox) |
| Form factors | None | Playwright `deviceScaleFactor` / viewport matrix |
| Assistive | Hand-rolled checks only ([test_a11y_extended.py](test_a11y_extended.py)) | axe-core via Playwright; manual for screen-reader UX |
| Network | None | Playwright network-throttling profiles in CI |
| Server | One target (`pytest` on `ubuntu-latest`) | Docker-built image; Python matrix |
| Data scale | Tiny (1–2 question quizzes) | Parametrised load fixtures |
| AI variations | Stub only | Provider-pinned golden eval; injection set |

**Highest-leverage gap to close first:** add a Playwright CI job that runs
the Golden Paths against `Chromium + WebKit + Firefox` at three viewports
(phone / tablet / desktop) with `axe-core` injected. That single addition
covers ~70 % of the automatable cells above, with one workflow file and one
test file.

---

## 15. Configuration sign-off (pre-release)

Before any release, this matrix is the auditable checklist:

| Tier | Block release if any cell fails? |
|---|---|
| **P0** | Yes — full pass required |
| **P1** | Yes for public release; can be waived for an internal pilot with a documented owner |
| **P2** | No — record findings, prioritise |

A "configuration test report" should be appended to each release with the
matrix marked Pass / Fail / Waived / N-A and tester signatures.
