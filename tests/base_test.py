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

class TestDatabaseState(BaseTestCase):

    def test_user_creation(self):
        self._create_test_user()
        user = self.session.query(User).filter_by(username="testuser").first()
        self.assertIsNotNone(user)

    def test_user_deletion(self):
        self._create_test_user()
        user = self.session.query(User).filter_by(username="testuser").first()
        self.session.delete(user)
        self.session.commit()
        user = self.session.query(User).filter_by(username="testuser").first()
        self.assertIsNone(user)

    def test_user_deletion_cascades_1(self):
        # Create test users and notes
        self._create_test_user(username='testuser', password='testpassword')
        self._create_test_user(username='testuser2', password='testpassword2')
        self._create_test_note(1, 'testcontent1')
        self._create_test_note(2, 'testcontent2')

        # Establish friendship
        user1 = self.session.query(User).filter_by(username='testuser').one()
        user2 = self.session.query(User).filter_by(username='testuser2').one()
        friendship = Friend(user_id=user1.id, friend_id=user2.id)
        self.session.add(friendship)
        self.session.commit()

        # Check that friendship exists
        self.assertTrue(user1.is_friend(user2.id))

        # Delete user2
        self.session.delete(user2)
        self.session.commit()

        # Check that friendship is deleted
        self.assertFalse(user1.is_friend(user2.id))

        # Check that notes of user2 are deleted
        user2_notes = self.session.query(Note).filter_by(user_id=user2.id).all()
        self.assertEqual(len(user2_notes), 0)

    def test_user_deletion_cascades_2(self):
        # Create test users and notes
        self._create_test_user(username='testuser', password='testpassword')
        self._create_test_user(username='testuser2', password='testpassword2')
        self._create_test_note(1, 'testcontent1')
        self._create_test_note(2, 'testcontent2')

        # Establish friendship
        user1 = self.session.query(User).filter_by(username='testuser').one()
        user2 = self.session.query(User).filter_by(username='testuser2').one()
        friendship = Friend(user_id=user1.id, friend_id=user2.id)
        self.session.add(friendship)
        self.session.commit()

        # Check that friendship exists
        self.assertTrue(user1.is_friend(user2.id))

        # Delete user1
        self.session.delete(user1)
        self.session.commit()

        # Check that friendship is deleted
        self.assertFalse(user2.is_friend(user1.id))

        # Check that notes of user1 are deleted
        user1_notes = self.session.query(Note).filter_by(user_id=user1.id).all()
        self.assertEqual(len(user1_notes), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
