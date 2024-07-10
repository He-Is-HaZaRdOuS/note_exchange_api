from flask import Blueprint, abort, make_response, jsonify, request
from config import db, jwt
from models import User
from schemas import user_schema, user_schema_no_password, users_schema_no_password
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity

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
    users = User.query.all()
    return users_schema_no_password.dump(users)


@users_bp.route("/<user_id>", methods=["GET"])
def read_one(user_id):
    user = User.query.filter(User.username == user_id).one_or_none()

    if user is not None:
        return user_schema_no_password.dump(user)
    else:
        abort(404, f"user with username {user_id} not found")

@users_bp.route("/", methods=["PUT"])
@jwt_required()
def update():
    user = request.get_json()
    username = user.get("username")
    print(request.headers)
    current_user = get_jwt_identity()
    existing_user = User.query.filter(User.username == username).one_or_none()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return abort(404, f"JWT expired or outdated or user does not exist anymore")
    
    if existing_user:
        if username != current_user['username']:
            abort(404, f"not authorized to change this user")
        update_user = user_schema.load(user, session=db.session)
        existing_user.password = generate_password_hash(update_user.password)
        db.session.merge(existing_user)
        db.session.commit()
        return user_schema_no_password.dump(existing_user), 201
    else:
        abort(404, f"user with last name {username} not found")


@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete(user_id):
    existing_user = User.query.filter(User.id == user_id).one_or_none()
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return abort(404, f"JWT expired or outdated or user does not exist anymore")

    if existing_user.id != cuser.id:
        return abort(404, f"not authorized")

    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()
        return make_response(f"{existing_user.username} successfully deleted", 200)
    else:
        abort(404, f"user with id {existing_user.username} not found")
