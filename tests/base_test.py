import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.security import generate_password_hash
from app import app, config
from config import db
from models import User, Note, Friend

class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            with app.app_context():
                cls.engine = db.engine
            cls.Session = sessionmaker(bind=cls.engine)
        except OperationalError as e:
            print(f"Error connecting to the database: {e}")
            cls.engine = None

    @classmethod
    def tearDownClass(cls):
        if cls.engine:
            cls.engine.dispose()

    def setUp(self):
        if not self.engine:
            self.skipTest("Skipping test due to database connection issues.")

        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        try:
            self.session = self.Session()  # Create a new session for each test
            db.metadata.create_all(self.engine)  # Create all tables before each test
        except SQLAlchemyError as e:
            print(f"Error during setup: {e}")
            self.skipTest(f"Skipping test due to setup issues: {e}")

    def tearDown(self):
        if not self.engine:
            return

        self.session.rollback()
        self.session.close()
        self.app_context.pop()

        try:
            db.metadata.drop_all(self.engine)  # Drop all tables after each test
        except SQLAlchemyError as e:
            print(f"Error during teardown: {e}")

    def _create_test_user(self, username="testuser", password="testpassword"):
        try:
            user = User(username=username, password=generate_password_hash(password))
            self.session.add(user)
            self.session.commit()
        except SQLAlchemyError as e:
            print(f"Error creating test user: {e}")
            self.fail(f"Failed to create test user: {e}")

    def _create_test_note(self, user_id, content):
        try:
            note = Note(content=content, user_id=user_id)
            self.session.add(note)
            self.session.commit()
        except SQLAlchemyError as e:
            print(f"Error creating test note: {e}")
            self.fail(f"Failed to create test note: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
