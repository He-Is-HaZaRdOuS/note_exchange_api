from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from application.models import User, Permission
from helpers.common_responses import unauthorized, forbidden

# Decorator that only authorizes privileged admins to invoking function
def admin_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()

            if not current_user:
                return unauthorized()

            user = User.query.filter_by(username=current_user['username']).first()

            if not user:
                return unauthorized()

            permission = Permission.query.filter_by(name=permission_name).first()

            # Check if user has the required permission
            if not any(role.has_permission(permission) for role in user.roles):
                return forbidden()

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decorator that authorizes privileged admins and resource owners to invoking function
def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()

            if not current_user:
                return unauthorized()

            user = User.query.filter_by(username=current_user['username']).first()

            if not user:
                return unauthorized()

            if 'user_id' not in kwargs:
                return forbidden()

            permission = Permission.query.filter_by(name=permission_name).first()

            # Check if user has the required permission
            if not any(role.has_permission(permission) for role in user.roles) and kwargs['user_id'] != user.id:
                return forbidden()

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decorator that authorizes privileged admins and resource owners and friends of resource owners to invoking function
def access_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()

            if not current_user:
                return unauthorized()

            user = User.query.filter_by(username=current_user['username']).first()

            if not user:
                return unauthorized()

            if 'user_id' not in kwargs:
                return forbidden()

            target_user = User.query.get(kwargs['user_id'])

            if not target_user:
                return forbidden()

            permission = Permission.query.filter_by(name=permission_name).first()

            if (
                not target_user.is_friend(user.id) and
                kwargs['user_id'] != user.id and
                not any(role.has_permission(permission) for role in user.roles)
            ):
                return forbidden()

            return f(*args, **kwargs)

        return decorated_function
    return decorator
