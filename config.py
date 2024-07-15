import os
import toml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager


# Set the configuration type based on the CONFIG environment variable
config_type = os.getenv('CONFIG', 'DEVELOPMENT')

class Config:
    def __init__(self):
        self._config = toml.load("config.toml")

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if config_type == 'TESTING':
            return f"mariadb+pymysql://{self._config['test_database']['user']}:{self._config['test_database']['password']}@{self._config['test_database']['host']}:{self._config['test_database']['port']}/{self._config['test_database']['name']}"
        elif config_type == 'DEVELOPMENT':
            return f"mariadb+pymysql://{self._config['database']['user']}:{self._config['database']['password']}@{self._config['database']['host']}:{self._config['database']['port']}/{self._config['database']['name']}"
        else:
            raise ValueError("Invalid CONFIG environment variable value")
    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self):
        return False  # Optional: Disable modification tracking

    @property
    def JWT_SECRET_KEY(self):
        return 'Mobptimus Prime'

    @property
    def TESTING(self):
        return config_type == 'TESTING'

    @property
    def WTF_CSRF_ENABLED(self):
        return False if config_type == 'TESTING' else True

config = Config()

# Create the Flask app
app = Flask(__name__)
app.config.from_object(config)

# Initialize JWT, SQLAlchemy, and Marshmallow with the Flask app
jwt = JWTManager(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
