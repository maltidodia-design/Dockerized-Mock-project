"""
Initialize the SQLite database and create a sample quiz.
Run: python db_init.py
"""
from app import db, Quiz
import json

db.create_all()

sample_questions = [
    {
        'text': 'What is 2 + 2?',
        'choices': ['1', '2', '3', '4'],
        'answer_index': 3
    },
    {
        'text': 'Which planet is known as the Red Planet?',
        'choices': ['Earth', 'Mars', 'Jupiter', 'Saturn'],
        'answer_index': 1
    }
]

q = Quiz(title='Sample Math & Space Quiz', questions_json=json.dumps(sample_questions))
db.session.add(q)
db.session.commit()
print('Initialized DB and added sample quiz (id=', q.id, ')')
