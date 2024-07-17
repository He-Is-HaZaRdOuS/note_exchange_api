from flask import Blueprint, make_response, jsonify
from config import db
from models import User, Friend
from schemas import friend_schema, users_schema_no_password
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from common_responses import invalidJWT, noUser, noUserID, noJSON

friends_bp = Blueprint('friends', __name__)


@friends_bp.route("", methods=["GET"])
@jwt_required()
def get_friends(user_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    user_id = cuser.id
    friends_as_user = Friend.query.filter_by(user_id=user_id).all()
    friend_ids = {f.friend_id for f in friends_as_user}
    friend_ids.discard(user_id)
    friends = User.query.filter(User.id.in_(friend_ids)).all()

    return jsonify(users_schema_no_password.dump(friends)), 200


@friends_bp.route("/<friend_id>", methods=["POST"])
@jwt_required()
def add_friend(user_id, friend_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    fuser = User.query.filter(User.id == friend_id).one_or_none()

    if not cuser:
        return invalidJWT()

    if not fuser:
        return noUserID(friend_id)

    if cuser.id == fuser.id:
        response = jsonify({
            "error": "Bad Request",
            "message": "Cannot add yourself as a Friend"
        })
        return make_response(response, 406)

    try:
        user_id = cuser.id
        friend = Friend(user_id=user_id, friend_id=fuser.id)
        db.session.add(friend)
        db.session.commit()
        return jsonify(friend_schema.dump(friend)), 201
    except IntegrityError:
        db.session.rollback()
        response = jsonify({
            "error": "Conflict",
            "message": f"Already Friends with user {fuser.username}"
        })
        return make_response(response, 406)


@friends_bp.route("/<friend_id>", methods=["DELETE"])
@jwt_required()
def remove_friend(user_id, friend_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    fuser = User.query.filter(User.id == friend_id).one_or_none()

    if not cuser:
        return invalidJWT()

    if not fuser:
        return noUserID(friend_id)

    friend_to_delete = Friend.query.filter((Friend.user_id == cuser.id) & (Friend.friend_id == fuser.id)).first()

    if friend_to_delete:
        db.session.delete(friend_to_delete)
        db.session.commit()
        response = jsonify({
            "message": f"Removed Friend {fuser.username}"
        })
        return make_response(response, 200)
    else:
        response = jsonify({
            "error": "Bad request",
            "message": f"Not Friends with user {fuser.username}"
        })
        return make_response(response, 400)
