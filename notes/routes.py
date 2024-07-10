from flask import Blueprint, abort, make_response, request, jsonify
from config import db
from models import Note, User
from schemas import note_schema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

notes_bp = Blueprint('notes', __name__)


@notes_bp.route("/<note_id>")
@jwt_required()
def read_one(note_id):
    current_user = get_jwt_identity()
    user = User.query.filter(User.username == current_user['username']).one_or_none()
    note = Note.query.get(note_id)

    if not user:
        return abort(404, f"JWT expired or outdated or user does not exist anymore")

    if note is not None:
        if note.user_id != user.id:
            return abort(404, f"JWT not authorized to access this note")
        return note_schema.dump(note)
    else:
        abort(404, f"Note with ID {note_id} not found!")

@notes_bp.route("/<note_id>", methods=["PUT"])
@jwt_required()
def update(note_id):
    note = request.get_json()
    existing_note = Note.query.get(note_id)
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return abort(404, f"JWT expired or outdated or user does not exist anymore")

    if existing_note:
        if existing_note.user_id != cuser.id:
            return abort(404, f"JWT not authorized to access this note")
        update_note = note_schema.load(note, session=db.session)
        existing_note.content = update_note.content
        db.session.merge(existing_note)
        db.session.commit()
        return note_schema.dump(existing_note), 201
    else:
        abort(404, f"Note with id {note_id} not found!")

@notes_bp.route("/<note_id>", methods=["DELETE"])
@jwt_required()
def delete(note_id):
    existing_note = Note.query.get(note_id)
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if not cuser:
        return abort(404, f"JWT expired or outdated or user does not exist anymore")

    if existing_note:
        if existing_note.user_id != cuser.id:
            return abort(404, f"JWT not authorized to access this note")
        db.session.delete(existing_note)
        db.session.commit()
        return jsonify(message=f"note id {note_id} successfully deleted"), 204
    else:
        abort(404, f"Note with id {note_id} not found!")

@notes_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    note = request.get_json()
    user_id = note.get("user_id")
    user = User.query.filter(User.id == user_id).one_or_none()
    current_user = get_jwt_identity()
    cuser = User.query.filter(User.username == current_user['username']).one_or_none()

    if user:
        print(cuser.id)
        print(user_id)
        if cuser.id != int(user_id):
            return abort(404, f"not authorized")
        new_note = note_schema.load(note, session=db.session)
        user.notes.append(new_note)
        db.session.commit()
        return note_schema.dump(new_note), 201
    else:
        abort(404, f"user not found for ID: {user_id}")
