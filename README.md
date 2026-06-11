# Dockerized Mock Quiz MVP

A minimal Dockerized mock implementation of the AI-Powered Quiz & Study
Assistant Platform from [product_requirements.md](product_requirements.md).
Built as a 508 final-project artifact with a deliberate focus on
*testability*, *accessibility*, and *value-ranked test coverage* — the kind of
testing a paying customer would expect for an assessment platform serving
minors.

## Features

- Create quizzes (by pasting question JSON)
- Take quizzes (radio choices, grouped by `<fieldset>` for screen readers)
- Automatic grading and persistent result storage
- Mock AI-feedback endpoint returning explanations for incorrect answers
- `GET /healthz` liveness probe
- Origin-based CSRF mitigation, per-IP rate limiting on `/api/ai_feedback`,
  baseline security response headers, and 1 MiB request-body cap

## Quick start (Docker)

```bash
docker-compose up --build
# in another shell, populate the sample quiz:
docker-compose exec web python db_init.py
# visit http://localhost:8000
```

## Local development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python db_init.py
python app.py
```

## Running the tests

CI mirrors the local invocation in 5 distinct steps so each layer fails
independently. See [.github/workflows/ci.yml](.github/workflows/ci.yml).

```bash
# 1) Unit + integration
pytest tests/ --ignore=tests/test_e2e.py \
              --ignore=tests/test_security.py \
              --ignore=tests/test_a11y_extended.py \
              --ignore=tests/test_ai_safety.py \
              --ignore=tests/test_performance.py -v

# 2) E2E (boots the real app over HTTP)
pytest tests/test_e2e.py -v

# 3) Specialised: security + extended a11y + AI safety + concurrency
pytest tests/test_security.py tests/test_a11y_extended.py \
       tests/test_ai_safety.py tests/test_performance.py -v

# 4) SAST + 5) SCA
pip install bandit pip-audit
bandit -r app.py db_init.py tests/e2e_server.py --skip B104 -ll
pip-audit --strict --requirement requirements.txt
```

Current totals: **71 passed, 0 xfailed**, Bandit clean.

## Documentation

Strategy, plan, golden paths, gap analyses, and final reports all live in
[tests/](tests/):

| Document | What's in it |
|---|---|
| [tests/TEST_STRATEGY.md](tests/TEST_STRATEGY.md) | Overall test strategy |
| [tests/TEST_PLAN.md](tests/TEST_PLAN.md) | Test plan with TP-IDs and traceability |
| [tests/GOLDEN_PATHS.md](tests/GOLDEN_PATHS.md) | Value-ranked user journeys (what a paying customer expects to work) |
| [tests/CONFIGURATION_MATRIX.md](tests/CONFIGURATION_MATRIX.md) | Browsers / OS / AT / network / server configurations to test |
| [tests/PRODUCTION_ISSUES.md](tests/PRODUCTION_ISSUES.md) | Common failure modes for AI-EdTech assessment platforms, with case studies |
| [tests/AI_GENERATED_SPECIALIZED_TESTS.md](tests/AI_GENERATED_SPECIALIZED_TESTS.md) | What was AI-automated and an honest inventory of what wasn't |
| [tests/VALIDATION_OF_AUTOMATED_E2E_TESTS.md](tests/VALIDATION_OF_AUTOMATED_E2E_TESTS.md) | E2E validation report |
| [tests/VALIDATION_OF_ AUTOMATED_UNIT_TESTS.md](tests/VALIDATION_OF_%20AUTOMATED_UNIT_TESTS.md) | Unit-suite validation report |
| [tests/TEST_REPORT.md](tests/TEST_REPORT.md) | **Unified automated + manual final test report** |
| [tests/REFLECTION.md](tests/REFLECTION.md) | CI troubleshooting and designing-testable-software reflection |
| [manual-tests-checklist.md](manual-tests-checklist.md) | Baseline manual procedures |
| [tests/MANUAL_TESTING_BEYOND_AUTOMATION.md](tests/MANUAL_TESTING_BEYOND_AUTOMATION.md) | Coverage-gap manual plan (P0/P1/P2 + pre-release sign-off) |

## Notes

This is a mock/stub implementation intended for demos, early testing, and
508 coursework. The AI endpoint is a deterministic Python stub; the
[REFLECTION.md](tests/REFLECTION.md) and
[AI_GENERATED_SPECIALIZED_TESTS.md](tests/AI_GENERATED_SPECIALIZED_TESTS.md)
documents discuss what's automated, what's beyond automation, and what
would need to change before a real customer release (auth, real model,
deletion endpoint, schema migrations).
