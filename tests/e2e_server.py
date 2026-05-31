"""Live-server launcher for end-to-end (E2E) tests.

This starts the *real* Flask application over real HTTP (via werkzeug's
WSGI server) so E2E tests exercise the same code path a user hits through
gunicorn / `python app.py` — unlike the unit/integration tests which use the
in-process Flask test client.

It is run as a subprocess by `tests/conftest.py` via the `live_server`
fixture:

    python tests/e2e_server.py <host> <port> <sqlite_db_path>

The database is pointed at an isolated temp SQLite file so E2E runs never
touch the project's `instance/data.db`. The override is set in the
environment BEFORE importing `app`, because Flask-SQLAlchemy 3.x caches the
engine at SQLAlchemy(app) construction time and a late
`app.config[SQLALCHEMY_DATABASE_URI] = ...` would be silently ignored.
"""
import os
import sys

# Project root on sys.path regardless of subprocess cwd.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    if len(sys.argv) != 4:
        print("usage: e2e_server.py <host> <port> <db_path>", file=sys.stderr)
        raise SystemExit(2)

    host = sys.argv[1]
    port = int(sys.argv[2])
    db_path = os.path.abspath(sys.argv[3])

    # MUST be set before `from app import ...` — see module docstring.
    os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    # Rate-limit knobs tuned for tests: small window so successive tests don't
    # see leftover timestamps; max chosen so the rate-limit test can trigger
    # 429 within a tight burst without starving the rest of the suite.
    # Direct assignment (NOT setdefault): the pytest parent process sets these
    # high to disable rate-limiting in in-process tests; we must override that.
    os.environ["RATE_LIMIT_WINDOW"] = "0.1"
    os.environ["RATE_LIMIT_MAX"] = "20"

    from werkzeug.serving import make_server
    from app import app, db

    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

    # threaded=True so the readiness poll (and the in-process test_client call
    # that take_quiz makes to /api/ai_feedback) cannot deadlock the server.
    server = make_server(host, port, app, threaded=True)
    print(f"E2E_SERVER_READY {host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
