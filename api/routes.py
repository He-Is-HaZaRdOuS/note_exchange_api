import datetime
from flask import Blueprint, request, jsonify, make_response
from configuration.config import db
from application.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest
from sqlalchemy import select
from application.schemas import user_schema, user_schema_private
from helpers.common_responses import badRequest, unauthorized, forbidden, notFound
from helpers.input_validator import username_is_valid, password_is_valid, username_is_reserved

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Define the route for user registration
# This route will allow users to create an account by providing a username and password
# The username must be unique
# The password will be hashed before being stored in the database
# The route will return a 201 status code if the user is successfully registered
# The route will return a 406 status code if the username is already in use
# The route will return a 400 status code if the request body is not valid JSON
@auth_bp.route("/register", methods=["POST"])
def register():
    # Check if the recieved payload is faulty
    try:
        user = request.get_json()
        username = user.get("username")
        password = user.get("password")
        if username is None or password is None:
            raise KeyError
    except BadRequest:
        return badRequest("Could not load JSON from request")
    except KeyError:
        return badRequest("Invalid JSON body")

    # Reject if username is reserved
    if username_is_reserved(username):
        response = jsonify({
            "error": "Invalid Username",
            "message": "Username is reserved"
        })
        return make_response(response, 406)

    # Reject if the user already exists
    existing_user = User.query.filter(User.username == username).one_or_none()
    if existing_user is not None:
        response = jsonify({
            "error": "Username already in use",
            "message": f"User with username {username} already exists"
        })
        return make_response(response, 406)

    # Reject if the username is invalid
    if not username_is_valid(username):
        response = jsonify({
            "error": "Invalid Username",
            "message": "Username must be at least 4 characters long and at most 12 characters long, contain only alphanumeric characters, and be all lowercase"
        })
        return make_response(response, 406)

    # Reject if the password is invalid
    if not password_is_valid(password):
        response = jsonify({
            "error": "Invalid Password",
            "message": "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character"
        })
        return make_response(response, 406)

    # Else, Accept the request and register new user
    new_user = user_schema.load(user, session=db.session)
    new_user.password = generate_password_hash(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user_schema_private.dump(new_user)), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    # Check if the recieved payload is faulty
    try:
        user = request.get_json()
        username = user.get("username")
        password = user.get("password")
        if username is None or password is None:
            raise KeyError
    except BadRequest:
        return badRequest("Could not load JSON from request")
    except KeyError:
        return badRequest("Invalid JSON body")

    # Skip validation check if a reserved user is attempting to log in
    if not username_is_reserved(username):
        if not username_is_valid(username):
            response = jsonify({
                "error": "Invalid Username",
                "message": "Username must be at least 4 characters long and at most 12 characters long, contain only alphanumeric characters, and be all lowercase"
            })
            return make_response(response, 406)

    existing_user = User.query.filter(User.username == username).one_or_none()

    # Generate JWT if user exists and has provided the correct password
    if existing_user is not None and check_password_hash(existing_user.password, password):
        access_token = create_access_token(identity={'username': username}, expires_delta=datetime.timedelta(hours=24))
        response = jsonify({
            "access_token": f"{access_token}",
            "id": f"{existing_user.id}"
        })
        return make_response(response, 200)

    # Else, Reject the request
    response = jsonify({
        "error": "Unauthorized",
        "message": "Invalid credentials"
    })
    return make_response(response, 401)
