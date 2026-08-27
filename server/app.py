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
        page = request.args.get('page',1,type=int)
        per_page = request.args.get('per_page',5,type=int)
        pagination = Note.query.filter(Note.user_id==user_id).paginate(page=page,per_page=per_page,error_out=False)
        notes = pagination.items
        return {
            'page':page,
            'per_page':per_page,
            'total': pagination.total,
            'total_pages':pagination.pages,
            'items':[NoteSchema().dump(note) for note in notes]
        }, 200
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.filter(User.id==user_id).first()
        request_body = request.get_json()

        note = Note(**request_body)
        note.user = user
        try:
            db.session.add(note)
            db.session.commit()
            return make_response(NoteSchema().dump(note), 201)
        except IntegrityError:
            return {'error':'400 Bad Request'}, 400

class NoteView(Resource):
    def get(self, id):
        user_id = get_jwt_identity()
        user = User.query.filter(User.id==user_id).first()
        note = Note.query.filter(Note.id==id).first()
        if not note:
            return {'error':f'404 Note {id} not found'}
        
        if note.user != user:
            return {'error':'403 Forbidden'}
        else:
            return NoteSchema().dump(note), 200

    def patch(self,id):
        user_id = get_jwt_identity()
        user = User.query.filter(User.id==user_id).first()
        note = Note.query.filter(Note.id==id).first()
        if not note:
            return {'error':f'404 Note {id} not found'}

        if note.user != user:
            return {'error':'403 Forbidden'}
        else:
            request_body = request.get_json()
            for k,v in request_body.items():
                if hasattr(note,k):
                    setattr(note,k,v)
            try:
                db.session.commit()
                return NoteSchema().dump(note), 200
            except IntegrityError:
                return {'error':'400 Bad Request'}

api.add_resource(Login,'/login',endpoint='login')
api.add_resource(Signup,'/signup',endpoint='signup')
api.add_resource(CheckToken,'/me',endpoint='me')
api.add_resource(NoteList,'/notes',endpoint='notes')
api.add_resource(NoteView,'/notes/<int:id>',endpoint='note')


if __name__ == '__main__':
    # Run the app locally in debug mode
    app.run(debug=True, port=5555)
