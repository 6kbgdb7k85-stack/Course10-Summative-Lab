from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)

    notes = db.relationship('Note', back_populates='user', cascade='all, delete-orphan')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hash may not be viewed')

    @password_hash.setter
    def password_hash(self,password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self,password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.id}, {self.username}>'

class UserSchema(Schema):
    id = fields.Int()
    username = fields.String()
    notes = fields.List(fields.Nested(lambda: NotesSchema(exclude=('user',))))

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User',back_populates='notes')

    def __repr__(self):
        return f'<Note {self.id}, {self.title}, {self.content}, {self.user_id}>'

class NotesSchema(Schema):
    id = fields.Int()
    title = fields.String()
    content = fields.String()
    user = fields.Nested(lambda: UserSchema(exclude=('notes',)))