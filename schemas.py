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

class UserSchemaNoPassword(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        exclude = ("password",)
    notes = fields.Nested(NoteSchema, many=True)

class FriendSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Friend
        load_instance = True
        sqla_session = db.session
    user = fields.Nested(UserSchemaNoPassword)
    friend = fields.Nested(UserSchemaNoPassword)


note_schema = NoteSchema()
user_schema = UserSchema()
user_schema_no_password = UserSchemaNoPassword()
users_schema_no_password = UserSchemaNoPassword(many=True)
friend_schema = FriendSchema()