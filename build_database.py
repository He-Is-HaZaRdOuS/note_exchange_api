import os
from datetime import datetime
from werkzeug.security import generate_password_hash
import toml

# Set the environment variable to determine the app configuration
os.environ['CONFIG'] = 'DEVELOPMENT'

from configuration.config import app, db
from application.models import User, Note, Friend

# Load the elevated usernames from the config file
with open('configuration/config.toml', 'r') as file:
    config = toml.load(file)
elevated_usernames = config['users']['elevated_usernames']

with app.app_context():
    db.drop_all()
    db.create_all()

    for i, username in enumerate(elevated_usernames, start=1):
        admin_user = User(
            id=i,  # Generate a unique ID for each admin user
            username=username,
            password=generate_password_hash(username),
            admin=True
        )
        db.session.add(admin_user)

    db.session.commit()
