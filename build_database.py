import os
from datetime import datetime

# Set the environment variable to determine the app configuration
os.environ['CONFIG'] = 'DEVELOPMENT'

from config import app, db
from models import User, Note, Friend

with app.app_context():
    db.drop_all()
    db.create_all()
