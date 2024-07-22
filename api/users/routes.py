from flask import Blueprint, make_response, jsonify, request
from configuration.config import db, jwt
from application.models import User
from application.schemas import user_schema, user_schema_private
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers.common_responses import invalidJWT, noUser, noUserID, notAuthorized, noJSON, invalidJSON
from helpers.decorators import permission_required, admin_required

# Create blueprint
users_bp = Blueprint('users', __name__)

# Callback function if a valid but expired JWT is recieved
@jwt.expired_token_loader
def expired_token_callback(header, payload):
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The token has expired'
    }), 401


# Retrieve all users
@users_bp.route("", methods=["GET"])
@jwt_required()
@admin_required("can_read_users")
def read_all():
    users = User.query.filter(User.admin == False).all()
    return user_schema_private.dump(users, many=True)


# Retrieve one user
@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@permission_required("can_read_users")
def read_one(user_id):
    user = User.query.filter(User.id == user_id).one_or_none()
    if user is None:
        return noUserID(user_id)

    return user_schema_private.dump(user)


# Update user password
@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
@permission_required("can_update_users")
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

    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if existing_user is None:
        return noUserID(user_id)

    update_user = user_schema.load(user, session=db.session)
    existing_user.password = generate_password_hash(update_user.password)
    db.session.merge(existing_user)
    db.session.commit()

    return user_schema_private.dump(existing_user), 200


# Delete user
@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@permission_required("can_delete_users")
def delete(user_id):
    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if existing_user is None:
        return noUserID(user_id)

    db.session.delete(existing_user)
    db.session.commit()

    response = jsonify({
        "message": f"{existing_user.username} successfully deleted"
    })
    return make_response(response, 200)
