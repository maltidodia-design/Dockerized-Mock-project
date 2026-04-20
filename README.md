# Dockerized Mock Quiz MVP

This is a minimal Dockerized mock implementation of the AI-Powered Quiz & Study Assistant Platform MVP from `product_requirements.md`.

Features included:
- Create quizzes (by pasting JSON)
- Take quizzes (radio choices)
- Automatic grading and simple result storage
- Mock AI-feedback endpoint that returns simple explanations

Quick start (macOS / zsh):

1. Build and run with docker-compose:

```bash
docker-compose up --build
```

2. Initialize the database and add a sample quiz (in a separate terminal):

```bash
docker-compose exec web python db_init.py
```

3. Visit http://localhost:8000

Running tests:

```bash
pytest -q
```

Notes:
- This is a mock/stub implementation intended for demos and early testing. The AI endpoint is a placeholder.
- For production, add authentication, input validation, and a real AI service integration.
