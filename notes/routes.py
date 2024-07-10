from flask import Blueprint, abort, make_response
from config import db
from models import Note, User
from schemas import note_schema

notes_bp = Blueprint('notes', __name__)


def read_one(note_id):
    note = Note.query.get(note_id)

    if note is not None:
        return note_schema.dump(note)
    else:
        abort(404, f"Note with ID {note_id} not found!")

def update(note_id, note):
    existing_note = Note.query.get(note_id)

    if existing_note:
        update_note = note_schema.load(note, session=db.session)
        existing_note.content = update_note.content
        db.session.merge(existing_note)
        db.session.commit()
        return note_schema.dump(existing_note), 201
    else:
        abort(404, f"Note with id {note_id} not found!")

def delete(note_id):
    existing_note = Note.query.get(note_id)

    if existing_note:
        db.session.delete(existing_note)
        db.session.commit()
        return make_response(f"{note_id} successfully deleted!", 204)
    else:
        abort(404, f"Note with id {note_id} not found!")

def create(note):
    user_id = note.get("user_id")
    user = user.query.get(user_id)

    if user:
        new_note = note_schema.load(note, session=db.session)
        user.notes.append(new_note)
        db.session.commit()
        return note_schema.dump(new_note), 201
    else:
        abort(404, f"user not found for ID: {user_id}")
