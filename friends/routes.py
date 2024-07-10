from flask import Blueprint, abort, make_response, request, jsonify
from config import db
from models import Note, User, Friend
from schemas import friend_schema, users_schema_no_password
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

friends_bp = Blueprint('friends', __name__)


@friends_bp.route("/", methods=["GET"])
@jwt_required()
def get_friends():
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    print(current_user)

    if not cuser:
        return abort(404, f"JWT expired or outdated or user does not exist anymore")
    
    user_id = cuser.id
    
    friends_as_user = Friend.query.filter_by(user_id=user_id).all()
    
    # Extract friend IDs
    friend_ids = {f.friend_id for f in friends_as_user}
    friend_ids.discard(user_id)  # Remove the original user's ID if present
    
    # Query for user objects
    friends = User.query.filter(User.id.in_(friend_ids)).all()
    
    # Serialize the result
    return jsonify(users_schema_no_password.dump(friends)), 200


@friends_bp.route("/<friend_id>", methods=["POST"])
@jwt_required()
def add_friend(friend_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    fuser = User.query.filter(User.id == friend_id).one_or_none()
    print(current_user)

    if not cuser:
        return abort(404, f"JWT expired or outdated or user does not exist anymore")
    
    if not fuser:
        return abort(404, f"user with id {friend_id} does not exist")
    
    try:
        user_id = cuser.id
        friend = Friend(user_id=user_id, friend_id=friend_id)
        db.session.add(friend)
        db.session.commit()
        return friend_schema.dump(friend), 201
    except IntegrityError:
        db.session.rollback()
        return abort(409, f"error: already friends with user id {friend_id}")


@friends_bp.route("/<friend_id>", methods=["DELETE"])
@jwt_required()
def remove_friend(friend_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    fuser = User.query.filter(User.id == friend_id).one_or_none()
    print(current_user)

    if not cuser:
        return abort(404, f"JWT expired or outdated or user does not exist anymore")
    
    if not fuser:
        return abort(404, f"user with id {friend_id} does not exist")
    
    if cuser.id == fuser.id:
        return abort(403, f"cannot befriend self")
    
    friend_to_delete = Friend.query.filter((Friend.user_id == cuser.id) & (Friend.friend_id == friend_id)).first()

    if friend_to_delete:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return make_response(f"user with id {friend_id} unfriended", 200)
    else:
        return abort(404, f"user with id {friend_id} is not a friend already")