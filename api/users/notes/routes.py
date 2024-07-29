from flask import Blueprint, request, jsonify
from configuration.config import db
from application.models import Note, User, Friend
from application.schemas import note_schema
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy import select
from helpers.common_responses import badRequest, unauthorized, forbidden, notFound
from helpers.decorators import permission_required, access_required

# Create blueprint
notes_bp = Blueprint('notes', __name__)


# Retrieve all notes of user friends
@notes_bp.route("/friends", methods=["GET"])
@jwt_required()
@access_required("can_read_notes")
def get_friends_notes(user_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if existing_user is None:
        return notFound()

    friends_who_added_me_subquery = db.session.query(Friend.user_id).filter(Friend.friend_id == cuser.id).subquery()
    friends_notes_query = Note.query.filter(Note.user_id.in_(select(friends_who_added_me_subquery)))
    friends_notes = friends_notes_query.all()
    return note_schema.dump(friends_notes, many=True)


# Create note for user
@notes_bp.route("", methods=["POST"])
@jwt_required()
@permission_required("can_create_notes")
def create(user_id):
    try:
        note_data = request.get_json()
        if not note_data:
            raise BadRequest
        content = note_data.get('content')
        if not content:
            raise KeyError
    except BadRequest:
        return badRequest("Could not load JSON from request")
    except KeyError:
        return badRequest("Invalid JSON body")

    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if existing_user is None:
        return notFound()

    new_note = Note(
        content=content.strip(),
        user_id=user_id
    )
    db.session.add(new_note)
    db.session.commit()
    return jsonify(note_schema.dump(new_note)), 201


# Retrieve all notes of user
@notes_bp.route("", methods=["GET"])
@jwt_required()
@access_required("can_read_notes")
def read_all(user_id):
    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if existing_user is None:
        return notFound()

    my_notes = Note.query.filter_by(user_id=existing_user.id).all()
    return note_schema.dump(my_notes, many=True)


@notes_bp.route("/<int:note_id>", methods=["GET"])
@jwt_required()
@access_required("can_read_notes")
def read_one(user_id, note_id):
    existing_user = User.query.filter(User.id == user_id).one_or_none()
    note = Note.query.get(note_id)

    if existing_user is None:
        return notFound()

    if note is None:
        return notFound()

    if note.user_id != user_id:
        return forbidden()

    return note_schema.dump(note)


# Retrieve one note for user
@notes_bp.route("/<int:note_id>", methods=["PUT"])
@jwt_required()
@permission_required("can_update_notes")
def update(user_id, note_id):
    try:
        note_data = request.get_json()
    except BadRequest:
        return badRequest("Could not load JSON from request")

    existing_note = Note.query.get(note_id)

    if existing_note is None:
        return notFound()

    if existing_note.user_id != user_id:
        return forbidden()

    existing_note.content = note_data.get('content').strip()
    db.session.commit()
    return note_schema.dump(existing_note)


# Delete note from user
@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@jwt_required()
@permission_required("can_delete_notes")
def delete(user_id, note_id):
    existing_note = Note.query.get(note_id)

    if existing_note is None:
        return notFound()

    if existing_note.user_id != user_id:
        return forbidden()

    db.session.delete(existing_note)
    db.session.commit()
    return jsonify(message=f"Note with id {note_id} successfully deleted"), 200
