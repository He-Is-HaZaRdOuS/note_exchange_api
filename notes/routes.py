from flask import Blueprint, request, jsonify
from config import db
from models import Note, User, Friend
from schemas import note_schema, notes_schema
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from common_responses import invalidJWT, noUser, noNote, notAuthorized, noJSON

notes_bp = Blueprint('notes', __name__)


@notes_bp.route("/friends", methods=["GET"])
@jwt_required()
def get_friends_notes():
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    friends_who_added_me_subquery = db.session.query(Friend.user_id).filter(Friend.friend_id == cuser.id).subquery()
    friends_notes_query = Note.query.filter(Note.user_id.in_(friends_who_added_me_subquery))
    friends_notes = friends_notes_query.all()
    return notes_schema.dump(friends_notes)


@notes_bp.route("/<note_id>", methods=["GET"])
@jwt_required()
def read_one(note_id):
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()
    note = Note.query.get(note_id)

    if not cuser:
        return invalidJWT()

    if note is not None:
        note_author = User.query.get(note.user_id)
        if note.user_id == cuser.id or note_author.is_friend(cuser.id):
            return note_schema.dump(note)
        else:
            return notAuthorized()
    else:
        return noNote(note_id)


@notes_bp.route("", methods=["GET"])
@jwt_required()
def read_all():
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    my_notes = Note.query.filter_by(user_id=cuser.id).all()

    return notes_schema.dump(my_notes, many=True)


@notes_bp.route("/<note_id>", methods=["PUT"])
@jwt_required()
def update(note_id):
    try:
        note = request.get_json()
    except BadRequest:
        return noJSON()
    existing_note = Note.query.get(note_id)
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    if existing_note:
        if existing_note.user_id != cuser.id:
            return notAuthorized()

        update_note = note_schema.load(note, session=db.session)
        existing_note.content = update_note.content
        db.session.merge(existing_note)
        db.session.commit()
        return note_schema.dump(existing_note), 201
    else:
        return noNote()


@notes_bp.route("/<note_id>", methods=["DELETE"])
@jwt_required()
def delete(note_id):
    existing_note = Note.query.get(note_id)
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return invalidJWT()

    if existing_note:
        if existing_note.user_id != cuser.id:
            return notAuthorized()

        db.session.delete(existing_note)
        db.session.commit()
        return jsonify(message=f"Note with id {note_id} successfully deleted"), 200
    else:
        return noNote()


@notes_bp.route("", methods=["POST"])
@jwt_required()
def create():
    try:
        note = request.get_json()
    except BadRequest:
        return noJSON()
    user_id = note.get("user_id")
    user = User.query.filter(User.id == user_id).one_or_none()
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if user:
        if cuser.id != int(user_id):
            return notAuthorized()

        new_note = note_schema.load(note, session=db.session)
        user.notes.append(new_note)
        db.session.commit()
        return jsonify(note_schema.dump(new_note)), 201
    else:
        return noUser()
