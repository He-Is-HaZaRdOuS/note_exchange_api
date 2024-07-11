from flask import Blueprint, make_response, jsonify, request
from config import db, jwt
from models import User
from schemas import user_schema, user_schema_no_password, users_schema_no_password
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required, get_jwt_identity
from common_responses import invalidJWT, noUser, notAuthorized, noJSON

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
        return noUser()


@users_bp.route("/", methods=["PUT"])
@jwt_required()
def update():
    try:
        user = request.get_json()
    except BadRequest:
        return noJSON()    
    username = user.get("username")
    print(request.headers)
    current_user = get_jwt_identity()
    existing_user = User.query.filter(User.username == username).one_or_none()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()
    
    if existing_user:
        if username != current_user['username']:
            return notAuthorized()
        
        update_user = user_schema.load(user, session=db.session)
        existing_user.password = generate_password_hash(update_user.password)
        db.session.merge(existing_user)
        db.session.commit()
        return user_schema_no_password.dump(existing_user), 201
    else:
        return noUser()


@users_bp.route("/<username>", methods=["DELETE"])
@jwt_required()
def delete(username):
    existing_user = User.query.filter(User.username == username).one_or_none()
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    if existing_user.id != cuser.id:
            return notAuthorized()

    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()
        response = jsonify({
            "message": f"{existing_user.username} successfully deleted"
        })
        return make_response(response, 200)
    else:
        return noUser()
