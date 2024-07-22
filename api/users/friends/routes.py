from flask import Blueprint, jsonify, make_response
from configuration.config import db
from application.models import User, Friend
from application.schemas import friend_schema, user_schema_private
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers.common_responses import invalidJWT, noUser, noUserID, notAuthorized
from helpers.decorators import permission_required

# Create blueprint
friends_bp = Blueprint('friends', __name__)


# Add friend to user
@friends_bp.route("/<int:friend_id>", methods=["POST"])
@jwt_required()
@permission_required("can_create_friends")
def create(user_id, friend_id):
    fuser = User.query.filter(User.id == friend_id).one_or_none()

    if not fuser:
        return noUserID(friend_id)

    if user_id == fuser.id:
        return make_response(jsonify({"error": "Bad Request", "message": "Cannot add yourself as a Friend"}), 406)

    try:
        friend = Friend(user_id=user_id, friend_id=fuser.id)
        db.session.add(friend)
        db.session.commit()
        return jsonify(friend_schema.dump(friend)), 201
    except IntegrityError:
        db.session.rollback()
        return make_response(jsonify({"error": "Conflict", "message": f"Already Friends with user {fuser.username}"}), 406)


# Retrieve all friends of user
@friends_bp.route("", methods=["GET"])
@jwt_required()
@permission_required("can_read_friends")
def read_all(user_id):
    friends_as_user = Friend.query.filter_by(user_id=user_id).all()
    friend_ids = {f.friend_id for f in friends_as_user}
    friend_ids.discard(user_id)
    friends = User.query.filter(User.id.in_(friend_ids)).all()
    return jsonify(user_schema_private.dump(friends, many=True)), 200


# Delete friend from user
@friends_bp.route("/<int:friend_id>", methods=["DELETE"])
@jwt_required()
@permission_required("can_delete_friends")
def delete(user_id, friend_id):
    fuser = User.query.filter(User.id == friend_id).one_or_none()

    if not fuser:
        return noUserID(friend_id)

    friend_to_delete = Friend.query.filter_by(user_id=user_id, friend_id=fuser.id).first()

    if friend_to_delete:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return make_response(jsonify({"message": f"Removed Friend with user id {fuser.id}"}), 200)
    else:
        return make_response(jsonify({"error": "Bad request", "message": f"Not Friends with user id {fuser.id}"}), 400)
