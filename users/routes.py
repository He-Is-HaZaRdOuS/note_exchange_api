from flask import Blueprint, abort, make_response, jsonify, request
from config import db, jwt
from models import User
from schemas import user_schema, users_schema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__)


@jwt.expired_token_loader
def expired_token_callback(header, payload):
    # token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The token has expired'
    }), 401


@users_bp.route("/", methods=["GET"])
def read_all():
    print(request.headers)
    users = User.query.all()
    return users_schema.dump(users)


def read_one(username):
    user = User.query.filter(User.username == username).one_or_none()

    if user is not None:
        return user_schema.dump(user)
    else:
        abort(404, f"user with last name {username} not found")

@jwt_required()
def update(username, user):
    print(request.headers)
    print("er")
    current_user = get_jwt_identity()
    existing_user = User.query.filter(User.username == username).one_or_none()
    
    if existing_user:
        if username != current_user['username']:
            abort(404, f"not authorized to change this user")
        update_user = user_schema.load(user, session=db.session)
        existing_user.password = update_user.password
        db.session.merge(existing_user)
        db.session.commit()
        return user_schema.dump(existing_user), 201
    else:
        abort(404, f"user with last name {username} not found")


def delete(username):
    existing_user = User.query.filter(User.username == username).one_or_none()

    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()
        return make_response(f"{username} successfully deleted", 200)
    else:
        abort(404, f"user with last name {username} not found")
