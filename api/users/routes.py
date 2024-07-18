from flask import Blueprint, make_response, jsonify, request
from configuration.config import db, jwt
from application.models import User
from application.schemas import user_schema, user_schema_private
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers.common_responses import invalidJWT, noUser, noUserID, notAuthorized, noJSON, invalidJSON

users_bp = Blueprint('users', __name__)


@jwt.expired_token_loader
def expired_token_callback(header, payload):
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The token has expired'
    }), 401


@users_bp.route("", methods=["GET"])
@jwt_required()
def read_all():
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser.admin:
        return notAuthorized()

    users = User.query.filter(User.admin == False).all()
    return user_schema.dump(users, many=True)


@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def read_one(user_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    user = User.query.filter(User.id == user_id).one_or_none()
    if user is None:
        return noUserID(user_id)

    if cuser.admin:
        return user_schema.dump(user)

    if user.id != cuser.id:
        return notAuthorized()

    return user_schema_private.dump(user)


@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update(user_id):
    try:
        user = request.get_json()
        if user is None:
            raise BadRequest
        password = user.get("password")
        if password is None:
            raise KeyError
    except BadRequest:
        return noJSON()
    except KeyError:
        return invalidJSON()

    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if not cuser:
        return invalidJWT()

    if existing_user is None:
        return noUserID(user_id)

    if user_id != cuser.id and not cuser.admin:
        return notAuthorized()

    update_user = user_schema.load(user, session=db.session)
    existing_user.password = generate_password_hash(update_user.password)
    db.session.merge(existing_user)
    db.session.commit()

    if cuser.admin:
        return user_schema.dump(existing_user), 200

    return user_schema_private.dump(existing_user), 200


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete(user_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if not cuser:
        return invalidJWT()

    if existing_user is None:
        return noUserID(user_id)

    if existing_user.id != cuser.id and not cuser.admin:
        return notAuthorized()

    db.session.delete(existing_user)
    db.session.commit()

    response = jsonify({
        "message": f"{existing_user.username} successfully deleted"
    })
    return make_response(response, 200)
