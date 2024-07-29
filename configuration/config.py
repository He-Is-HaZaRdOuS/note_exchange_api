import os
import toml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager


# Set the configuration type based on the CONFIG environment variable
config_type = os.getenv('CONFIG')

class Config:
    def __init__(self):
        # Load config from config file
        self._config = toml.load("configuration/database_config.toml")

    # Set relevant properties

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if config_type == 'TESTING':
            return "sqlite:///:memory:"
        elif config_type == 'DEVELOPMENT':
            return f"mariadb+pymysql://{self._config['database']['user']}:{self._config['database']['password']}@{self._config['database']['host']}:{self._config['database']['port']}/{self._config['database']['name']}"
        else:
            raise ValueError("Invalid CONFIG environment variable value")
    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self):
        return False

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
app = Flask(__name__,
            static_url_path='',
            static_folder='../static',
            template_folder='../templates')
app.config.from_object(config)

# Initialize JWT, SQLAlchemy, and Marshmallow with the Flask app
jwt = JWTManager(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
