from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import fields
from models import User, Note, Friend
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

class UserSchemaPrivate(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        exclude = ("notes", "friends", "friends_of", "password", "admin")
    notes = fields.Nested(NoteSchema, many=True)

class FriendSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Friend
        load_instance = True
        sqla_session = db.session
    user = fields.Nested(UserSchemaPrivate)
    friend = fields.Nested(UserSchemaPrivate)


note_schema = NoteSchema()
user_schema = UserSchema()
user_schema_private = UserSchemaPrivate()
friend_schema = FriendSchema()
