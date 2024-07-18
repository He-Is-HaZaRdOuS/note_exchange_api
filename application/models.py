from datetime import datetime, timezone
from configuration.config import db

class Friend(db.Model):
    __tablename__ = "friend"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='unique_user_friend'),
    )

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('friends', cascade="all, delete-orphan"))
    friend = db.relationship('User', foreign_keys=[friend_id], backref=db.backref('friends_of', cascade="all, delete-orphan"))

class Note(db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    content = db.Column(db.String(240), nullable=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )

class User(db.Model):
    __tablename__ = "user"
    admin = db.Column(db.Boolean, default=False)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(120))
    timestamp = db.Column(
        db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )
    notes = db.relationship(
        'Note',
        backref="user",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Note.timestamp)"
    )
    roles = db.relationship('Role', secondary='user_role')

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_name):
        return any(role.has_permission(permission_name) for role in self.roles)

    def is_friend(self, friend_user_id):
        return db.session.query(
            Friend.query.filter(
                (Friend.user_id == self.id) &
                (Friend.friend_id == friend_user_id)
            ).exists()
        ).scalar()

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    permissions = db.relationship('Permission', secondary='role_permission')

    def has_permission(self, permission_name):
        return any(permission.name == permission_name for permission in self.permissions)

class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

user_role = db.Table('user_role',
    db.Column(
        'user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

role_permission = db.Table('role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)
