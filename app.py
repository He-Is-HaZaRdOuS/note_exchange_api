from flask import abort, jsonify, request, url_for, render_template, make_response
import config
import datetime
import sqlite3
from config import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import create_access_token
from common_responses import invalidJSON, noJSON
from schemas import user_schema
from users.routes import users_bp
from notes.routes import notes_bp
from friends.routes import friends_bp

app = config.app

# Register blueprints' routes with the app and set their URL prefixes
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(notes_bp, url_prefix='/api/notes')
app.register_blueprint(friends_bp, url_prefix='/api/friends')


# Define the home route
# This route will be the first thing a user sees when they visit the API
# It will provide a brief welcome message and a link to the API documentation
@app.route('/')
def home():
    docs_url = url_for('redoc')
    return f"""
        <html>
            <head><title>Welcome</title></head>
            <body>
                <h1>Welcome to the Flask API</h1>
                <p>Please visit the <a href="{docs_url}">API documentation</a> for more information.</p>
            </body>
        </html>
    """

# Define the route for the API documentation
# This route will display the API documentation using the ReDoc UI
# The ReDoc UI is a tool that generates interactive API documentation from OpenAPI Specification (formerly Swagger Specification)
# The OpenAPI Specification is a standard for documenting REST APIs
# The OpenAPI Specification is a JSON or YAML file that describes the API's endpoints, request/response formats, and other details
# The ReDoc UI reads the OpenAPI Specification and generates a user-friendly documentation page
@app.route('/api/docs')
def redoc():
    return render_template("redoc.html")

# Define the route for user registration
# This route will allow users to create an account by providing a username and password
# The username must be unique
# The password will be hashed before being stored in the database
# The route will return a 201 status code if the user is successfully registered
# The route will return a 406 status code if the username is already in use
# The route will return a 400 status code if the request body is not valid JSON
@app.route("/api/register", methods=["POST"])
def register():
    try:
        user = request.get_json()
        username = user.get("username")
        password = user.get("password")
        if username is None or password is None:
            raise KeyError
    except BadRequest:
        return noJSON()
    except KeyError:
        return invalidJSON()
    existing_user = User.query.filter(User.username == username).one_or_none()
    if existing_user is not None:
        response = jsonify({
            "error": "Username already in use",
            "message": f"User with username {username} already exists"
        })
        return make_response(response, 406)

    new_user = user_schema.load(user, session=db.session)
    new_user.password = generate_password_hash(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user_schema.dump(new_user)), 201


@app.route("/api/login", methods=["POST"])
def login():
    try:
        user = request.get_json()
        username = user.get("username")
        password = user.get("password")
        if username is None or password is None:
            raise KeyError
    except BadRequest:
        return noJSON()
    except KeyError:
        return invalidJSON()
    existing_user = User.query.filter(User.username == username).one_or_none()

    if existing_user is not None and check_password_hash(existing_user.password, password):
        access_token = create_access_token(identity={'username': username}, expires_delta=datetime.timedelta(hours=24))
        return jsonify(access_token=access_token), 200
    response = jsonify({
        "error": "Unauthorized",
        "message": "Invalid credentials"
    })
    return make_response(response, 401)

def run():
    app.run(host="0.0.0.0", port=8000, debug=True)

if __name__ == "__main__":
    run()
