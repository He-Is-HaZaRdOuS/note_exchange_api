import pathlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

# Base directory for the project
basedir = pathlib.Path(__file__).parent.resolve()

# Create the Flask app
app = Flask(__name__)

# Configure the Flask app
app.config["JWT_SECRET_KEY"] = 'Mobptimus Prime'
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{basedir / 'users.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize JWT, SQLAlchemy, and Marshmallow with the Flask app
jwt = JWTManager(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)