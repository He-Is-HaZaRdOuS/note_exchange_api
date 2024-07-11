from flask import abort, jsonify, request, url_for, redirect, render_template
import config
import datetime
from config import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from schemas import user_schema
from users.routes import users_bp
from notes.routes import notes_bp
from friends.routes import friends_bp

app = config.app

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(notes_bp, url_prefix='/api/notes')
app.register_blueprint(friends_bp, url_prefix='/api/friends')


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

@app.route('/api/docs')
def redoc():
    return render_template("redoc.html")


@app.route("/api/register", methods=["POST"])
def register():
    user = request.get_json()
    username = user.get("username")
    password = user.get("password")
    existing_user = User.query.filter(User.username == username).one_or_none()

    if existing_user is None:
        new_user = user_schema.load(user, session=db.session)
        new_user.password = generate_password_hash(password)
        db.session.add(new_user)
        db.session.commit()
        return user_schema.dump(new_user), 201
    else:
        abort(406, f"user with username {username} already exists")


@app.route("/api/login", methods=["POST"])
def login():
    user = request.get_json()
    username = user.get("username")
    password = user.get("password")
    existing_user = User.query.filter(User.username == username).one_or_none()

    if existing_user is not None and check_password_hash(existing_user.password, password):
        access_token = create_access_token(identity={'username': username}, expires_delta=datetime.timedelta(hours=24))
        return jsonify(access_token=access_token), 200
    return jsonify(message='Invalid credentials'), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)