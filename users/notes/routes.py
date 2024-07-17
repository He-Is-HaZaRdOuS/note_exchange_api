from flask import Blueprint, request, jsonify
from config import db
from models import Note, User, Friend
from schemas import note_schema, notes_schema
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from common_responses import invalidJWT, noUser, noNote, notAuthorized, noJSON, noUserID, invalidJSON

notes_bp = Blueprint('notes', __name__)


@notes_bp.route("/friends", methods=["GET"])
@jwt_required()
def get_friends_notes(user_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if existing_user is None:
        return noUserID(user_id)

    if not cuser:
        return invalidJWT()

    if not existing_user.is_friend(cuser.id) and existing_user.id != cuser.id:
            return notAuthorized()

    friends_who_added_me_subquery = db.session.query(Friend.user_id).filter(Friend.friend_id == cuser.id).subquery()
    friends_notes_query = Note.query.filter(Note.user_id.in_(friends_who_added_me_subquery))
    friends_notes = friends_notes_query.all()
    return notes_schema.dump(friends_notes)


@notes_bp.route("/<note_id>", methods=["GET"])
@jwt_required()
def read_one(user_id, note_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    note = Note.query.get(note_id)
    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if not cuser:
        return invalidJWT()

    if existing_user is None:
        return noUserID(user_id)

    if not existing_user.is_friend(cuser.id) and existing_user.id != cuser.id:
            return notAuthorized()

    if note is not None:
        note_author = User.query.get(note.user_id)
        return note_schema.dump(note)
    else:
        return noNote(note_id)


@notes_bp.route("", methods=["GET"])
@jwt_required()
def read_all(user_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    existing_user = User.query.filter(User.id == user_id).one_or_none()

    if not cuser:
        return invalidJWT()

    if existing_user is None:
        return noUserID(user_id)

    if not existing_user.is_friend(cuser.id) and existing_user.id != cuser.id:
        return notAuthorized()

    my_notes = Note.query.filter_by(user_id=existing_user.id).all()

    return notes_schema.dump(my_notes)


@notes_bp.route("/<note_id>", methods=["PUT"])
@jwt_required()
def update(user_id, note_id):
    try:
        note = request.get_json()
    except BadRequest:
        return noJSON()
    existing_note = Note.query.get(note_id)
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    if int(user_id) != cuser.id:
        return notAuthorized()

    if existing_note:
        if existing_note.user_id != cuser.id:
            return notAuthorized()

        update_note = note_schema.load(note, session=db.session)
        update_note.content = update_note.content.strip()
        existing_note.content = update_note.content
        db.session.merge(existing_note)
        db.session.commit()
        return note_schema.dump(existing_note), 200
    else:
        return noNote(note_id)


@notes_bp.route("/<note_id>", methods=["DELETE"])
@jwt_required()
def delete(user_id, note_id):
    existing_note = Note.query.get(note_id)
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    if int(user_id) != cuser.id:
        return notAuthorized()

    if existing_note:
        if existing_note.user_id != cuser.id:
            return notAuthorized()

        db.session.delete(existing_note)
        db.session.commit()
        return jsonify(message=f"Note with id {note_id} successfully deleted"), 200
    else:
        return noNote(note_id)


@notes_bp.route("", methods=["POST"])
@jwt_required()
def create(user_id):
    try:
        note = request.get_json()
        if note.get('content') is None:
            raise KeyError
    except BadRequest:
        return noJSON()
    except KeyError:
        return invalidJSON()
    note_user_id = note.get("user_id")
    user = User.query.filter(User.id == user_id).one_or_none()
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if user:
        if not cuser:
            return invalidJWT()
        if cuser.id != int(user_id):
            return notAuthorized()

        new_note = note_schema.load(note, session=db.session)
        new_note.content = new_note.content.strip()
        user.notes.append(new_note)
        db.session.commit()
        return jsonify(note_schema.dump(new_note)), 201
    else:
        return noUserID(user_id)
