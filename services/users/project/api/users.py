from flask import Blueprint, request, render_template
from flask_restful import Resource, Api
from sqlalchemy import exc

from project import db

from project.api.models import User

users_blueprint = Blueprint('users', __name__, template_folder='./templates')
api = Api(users_blueprint)


class UsersList(Resource):

    @users_blueprint.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            post_data = request.get_json(force=True)
            username = post_data.get('username')
            email = post_data.get('email')
            db.session.add(User(username=username, email=email))
            db.sesssion.commit()
        users = User.query.all()
        return render_template('index.html', users=users)

    def get(self):
        """Get all users"""
        response_object = {
           'status': 'success',
           'data': {
               'users': [user.to_json() for user in User.query.all()]
           }
        }
        return response_object, 200

    """Creates a user"""
    def post(self):
        post_data = request.get_json(force=True)
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        if not post_data:
            return response_object, 400
        username = post_data.get('username')
        email = post_data.get('email')
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                new_user = User(username=username, email=email)
                db.session.add(new_user)
                db.session.commit()
                response_object = {
                    'status': 'success',
                    'message': f'{email} was added!'
                }
                return response_object, 201
            else:
                response_object['message'] = 'Sorry, that email already exists'
                return response_object, 400
        except exc.IntegrityError:
            db.session.rollback()
            return response_object, 400


class Users(Resource):
    def get(self, user_id):
        """Get a single user"""

        response_object = {
                    'status': 'fail',
                    'message': 'User does not exist'
                }

        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return response_object, 404
            else:
                response_object = {
                    'status': 'success',
                    'data': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'active': user.active
                    }
                }
                return response_object, 200
        except ValueError:
            return response_object, 400


class UsersPing(Resource):
    """Pings a user"""
    def get(self):
        return {
            'status':  'success',
            'message': "PONG"
        }


api.add_resource(UsersPing, '/users/ping')
api.add_resource(UsersList, '/users')
api.add_resource(Users, '/users/<user_id>')
