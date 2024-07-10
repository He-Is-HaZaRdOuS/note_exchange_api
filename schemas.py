from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import fields
from models import User, Note
from config import db, ma

ma = Marshmallow()


class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Note
        load_instance = True
        sqla_session = db.session
        include_fk = True

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True
    notes = fields.Nested(NoteSchema, many=True)


note_schema = NoteSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)