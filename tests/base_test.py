import unittest
from werkzeug.security import generate_password_hash
from app import app
from config import db
from models import User, Note, Friend

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

        self.app_context.pop()

    def _create_test_user(self, username="testuser", password="testpassword"):
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

    def _create_test_note(self, user_id, content):
        note = Note(content=content, user_id=user_id)
        db.session.add(note)
        db.session.commit()

if __name__ == '__main__':
    unittest.main()
