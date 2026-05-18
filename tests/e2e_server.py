"""Live-server launcher for end-to-end (E2E) tests.

This starts the *real* Flask application over real HTTP (via werkzeug's
WSGI server) so E2E tests exercise the same code path a user hits through
gunicorn / `python app.py` — unlike the unit/integration tests which use the
in-process Flask test client.

It is run as a subprocess by `tests/test_e2e.py`:

    python tests/e2e_server.py <host> <port> <sqlite_db_path>

The database is pointed at an isolated temp SQLite file so E2E runs never
touch the project's `instance/data.db`.
"""
import os
import sys

# Ensure the project root is importable regardless of the subprocess cwd.
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

    from werkzeug.serving import make_server
    from app import app, db

    # Isolate the database before any request creates the engine.
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
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
