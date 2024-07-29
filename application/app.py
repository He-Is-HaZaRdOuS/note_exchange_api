from flask import abort, jsonify, request, url_for, render_template, make_response
import configuration.config as config
import datetime
import sqlite3
from configuration.config import db
from application.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import create_access_token
from application.schemas import user_schema, user_schema_private
from api.users.routes import users_bp
from api.users.notes.routes import notes_bp
from api.users.friends.routes import friends_bp
from api.routes import auth_bp

app = config.app

# Register blueprints' routes with the app and set their URL prefixes
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(notes_bp, url_prefix='/api/users/<int:user_id>/notes')
app.register_blueprint(friends_bp, url_prefix='/api/users/<int:user_id>/friends')
app.register_blueprint(auth_bp, url_prefix='/api')


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

def run():
    app.run(host="0.0.0.0", port=8000, debug=True)
