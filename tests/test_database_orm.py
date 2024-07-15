import unittest
import json
from tests.base_test import BaseTestCase
from models import User, Note, Friend, db


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

    def test_user_deletion_cascades_1(self):
        with self.app.app_context():
            # Create test users and notes
            self._create_test_user(username='testuser', password='testpassword')
            self._create_test_user(username='testuser2', password='testpassword2')
            self._create_test_note(1, 'testcontent1')
            self._create_test_note(2, 'testcontent2')

            # Establish friendship
            user1 = User.query.filter_by(username='testuser').one()
            user2 = User.query.filter_by(username='testuser2').one()
            friendship = Friend(user_id=user1.id, friend_id=user2.id)
            db.session.add(friendship)
            db.session.commit()

            # Check that friendship exists
            self.assertTrue(user1.is_friend(user2.id))

            # Delete user2
            db.session.delete(user2)
            db.session.commit()

            # Check that friendship is deleted
            self.assertFalse(user1.is_friend(user2.id))

            # Check that notes of user2 are deleted
            user2_notes = Note.query.filter_by(user_id=user2.id).all()
            self.assertEqual(len(user2_notes), 0)

    def test_user_deletion_cascades_2(self):
        with self.app.app_context():
            # Create test users and notes
            self._create_test_user(username='testuser', password='testpassword')
            self._create_test_user(username='testuser2', password='testpassword2')
            self._create_test_note(1, 'testcontent1')
            self._create_test_note(2, 'testcontent2')

            # Establish friendship
            user1 = User.query.filter_by(username='testuser').one()
            user2 = User.query.filter_by(username='testuser2').one()
            friendship = Friend(user_id=user1.id, friend_id=user2.id)
            db.session.add(friendship)
            db.session.commit()

            # Check that friendship exists
            self.assertTrue(user1.is_friend(user2.id))

            # Delete user1
            db.session.delete(user1)
            db.session.commit()

            # Check that friendship is deleted
            self.assertFalse(user1.is_friend(user2.id))

            # Check that notes of user1 are deleted
            user1_notes = Note.query.filter_by(user_id=user1.id).all()
            self.assertEqual(len(user1_notes), 0)
