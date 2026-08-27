from flask import request, make_response, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, create_access_token
from flask_restful import Resource
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from config import app, db, api, jwt
from models import *

@app.before_request
def check_logged_in():
    open_routes = [
        'login',
        'signup'
    ]

    if request.endpoint not in open_routes and not verify_jwt_in_request():
        return {'error':'401 Unauthorized'}, 401

class Signup(Resource):
    def post(self):
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        if not username or not password:
            return make_response({'error':'400 Bad Request'})
        user = User(username=username)
        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
            access_token = create_access_token(identity=str(user.id))
            return make_response(jsonify(token=access_token, user=UserSchema().dump(user)),201)
        except IntegrityError:
            return {'error':'400 Bad Request'}, 400

class Login(Resource):
    def post(self):
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            access_token = create_access_token(identity=str(user.id))
            return make_response(jsonify(token=access_token, user=UserSchema().dump(user)), 200)
        else:
            return make_response({'error':'401 Invalid login'}, 401)

class CheckToken(Resource):
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.filter(User.id==user_id).first()
        return UserSchema().dump(user), 200

class NoteList(Resource):
    def get(self):
        user_id = get_jwt_identity()
        notes = Note.query.filter(Note.user_id==user_id).all()
        return make_response([NotesSchema().dump(note) for note in notes], 200)
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.filter(User.id==user_id).first()
        request_body = request.get_json()

        note = Note(**request_body)
        note.user = user
        try:
            db.session.add(note)
            db.session.commit()
            return make_response(NotesSchema().dump(note), 201)
        except IntegrityError:
            return {'error':'400 Bad Request'}, 400

api.add_resource(Login,'/login',endpoint='login')
api.add_resource(Signup,'/signup',endpoint='signup')
api.add_resource(CheckToken,'/me',endpoint='me')
api.add_resource(NoteList,'/notes',endpoint='notes')


if __name__ == '__main__':
    # Run the app locally in debug mode
    app.run(debug=True, port=5555)
