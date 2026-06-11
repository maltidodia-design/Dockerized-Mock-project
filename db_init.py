"""
Initialize the SQLite database and create a sample quiz.
Run inside the container: docker-compose exec web python db_init.py
Or locally:                python db_init.py
"""
import json

from app import app, db, Quiz

# Flask-SQLAlchemy 3.x requires an application context for db.create_all() and
# any DB access. Without this wrapper the script raises:
#   RuntimeError: Working outside of application context.
with app.app_context():
    db.create_all()

    sample_questions = [
        {
            'text': 'What is 2 + 2?',
            'choices': ['1', '2', '3', '4'],
            'answer_index': 3,
        },
        {
            'text': 'Which planet is known as the Red Planet?',
            'choices': ['Earth', 'Mars', 'Jupiter', 'Saturn'],
            'answer_index': 1,
        },
    ]

    q = Quiz(title='Sample Math & Space Quiz', questions_json=json.dumps(sample_questions))
    db.session.add(q)
    db.session.commit()
    print('Initialized DB and added sample quiz (id=', q.id, ')')
