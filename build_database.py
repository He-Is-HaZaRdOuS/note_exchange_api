from datetime import datetime
from config import app, db
from models import User, Note, Friend

with app.app_context():
    db.drop_all()
    db.create_all()