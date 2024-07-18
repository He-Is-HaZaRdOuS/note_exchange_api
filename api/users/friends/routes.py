from flask import Blueprint, jsonify, make_response
from configuration.config import db
from application.models import User, Friend
from application.schemas import friend_schema, user_schema_private
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers.common_responses import invalidJWT, noUser, noUserID, notAuthorized

friends_bp = Blueprint('friends', __name__)


@friends_bp.route("", methods=["GET"])
@jwt_required()
def read_friends(user_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    if user_id != cuser.id and not cuser.admin:
        return notAuthorized()

    user_id = cuser.id
    friends_as_user = Friend.query.filter_by(user_id=user_id).all()
    friend_ids = {f.friend_id for f in friends_as_user}
    friend_ids.discard(user_id)
    friends = User.query.filter(User.id.in_(friend_ids)).all()
    return jsonify(user_schema_private.dump(friends, many=True)), 200


@friends_bp.route("/<int:friend_id>", methods=["POST"])
@jwt_required()
def add_friend(user_id, friend_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    fuser = User.query.filter(User.id == friend_id).one_or_none()

    if not cuser:
        return invalidJWT()

    if not fuser:
        return noUserID(friend_id)

    if user_id != cuser.id and not cuser.admin:
        return notAuthorized()

    if cuser.id == fuser.id:
        return make_response(jsonify({"error": "Bad Request", "message": "Cannot add yourself as a Friend"}), 406)

    try:
        friend = Friend(user_id=cuser.id, friend_id=fuser.id)
        db.session.add(friend)
        db.session.commit()
        return jsonify(friend_schema.dump(friend)), 201
    except IntegrityError:
        db.session.rollback()
        return make_response(jsonify({"error": "Conflict", "message": f"Already Friends with user {fuser.username}"}), 406)


@friends_bp.route("/<int:friend_id>", methods=["DELETE"])
@jwt_required()
def remove_friend(user_id, friend_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    fuser = User.query.filter(User.id == friend_id).one_or_none()

    if not cuser:
        return invalidJWT()

    if not fuser:
        return noUserID(friend_id)

    if user_id != cuser.id and not cuser.admin:
        return notAuthorized()

    friend_to_delete = Friend.query.filter_by(user_id=cuser.id, friend_id=fuser.id).first()

    if friend_to_delete:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return make_response(jsonify({"message": f"Removed Friend with user id {fuser.id}"}), 200)
    else:
        return make_response(jsonify({"error": "Bad request", "message": f"Not Friends with user id {fuser.id}"}), 400)
