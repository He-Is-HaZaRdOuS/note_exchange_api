import unittest
from werkzeug.security import generate_password_hash
from app import app
from config import db
from models import User

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

class TestDatabaseState(BaseTestCase):

    def test_user_creation(self):
        self._create_test_user()
        user = User.query.filter_by(username="testuser").first()
        self.assertIsNotNone(user)

    def test_user_deletion(self):
        self._create_test_user()
        user = User.query.filter_by(username="testuser").first()
        db.session.delete(user)
        db.session.commit()
        user = User.query.filter_by(username="testuser").first()
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()
