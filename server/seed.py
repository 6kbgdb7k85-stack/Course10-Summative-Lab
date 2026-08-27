#!/usr/bin/env python3

from random import randint, choice as rc

from faker import Faker

from app import app
from models import db, Note, User

fake = Faker()

with app.app_context():

    users = []
    usernames = []

    User.query.delete()
    Note.query.delete()

    for i in range(20):
        username = fake.first_name()

        while username in usernames:
            username = fake.first_name()
        usernames.append(username)

        user = User(username=username)
        user.password_hash = user.username+'password'
        users.append(user)

    db.session.add_all(users)

    notes = []
    for i in range(20):
        note = Note(title=fake.word(),content=fake.paragraph())
        note.user = rc(users)
        notes.append(note)

    db.session.add_all(notes)
    db.session.commit()