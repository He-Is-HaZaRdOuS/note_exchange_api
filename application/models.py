from datetime import datetime, timezone
from configuration.config import db

# Define models and relationships that translate to database tables using the ORM

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

# Mapper table (Role < - > Permission)
roles_permissions = db.Table('roles_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete="CASCADE"), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id', ondelete="CASCADE"), primary_key=True)
)

# Mapper table (User < - > Role)
users_roles = db.Table(
    'users_roles',
    db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete="CASCADE"), primary_key=True)
)

class User(db.Model):
    __tablename__ = "user"
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
    roles = db.relationship('Role', secondary=users_roles, backref=db.backref('users', lazy='dynamic', cascade="all, delete"))

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    permissions = db.relationship('Permission', secondary=roles_permissions, backref=db.backref('roles', lazy='dynamic', cascade="all, delete"))

    def has_permission(self, permission):
        if not permission:
            return False

        return db.session.query(roles_permissions).filter(
            roles_permissions.c.role_id == self.id,
            roles_permissions.c.permission_id == permission.id
        ).count() > 0

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions.append(permission)

    def remove_permission(self, permission):
        if self.has_permission(permission):
            self.permissions.remove(permission)

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
