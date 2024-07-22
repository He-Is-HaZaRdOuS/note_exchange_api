import unittest
import toml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.security import generate_password_hash
from application.app import config, app
from configuration.config import db
from application.models import User, Note, Friend, Role, Permission

class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            with app.app_context():
                cls.engine = db.engine
                cls.Session = sessionmaker(bind=cls.engine)

                # Drop all tables and recreate them
                db.metadata.drop_all(cls.engine)
                db.metadata.create_all(cls.engine)
        except OperationalError as e:
            print(f"Error connecting to the database: {e}")
            cls.engine = None

    @classmethod
    def _create_role_if_not_exists(cls, role_name):
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            cls.session = cls.Session()
            cls.session.add(role)
            cls.session.commit()
            cls.session.close()
        return role

    @classmethod
    def _create_permission_if_not_exists(cls, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        if not permission:
            permission = Permission(name=permission_name)
            cls.session = cls.Session()
            cls.session.add(permission)
            cls.session.commit()
            cls.session.close()
        return permission

    @classmethod
    def _assign_permission_to_role(cls, permission_name, role_name):
        role = Role.query.filter_by(name=role_name).first()
        permission = Permission.query.filter_by(name=permission_name).first()
        if role and permission:
            role.add_permission(permission)
            cls.session = cls.Session()
            cls.session.commit()
            cls.session.close()

    @classmethod
    def _assign_role_to_user(cls, username, role_name):
        user = User.query.filter_by(username=username).first()
        role = Role.query.filter_by(name=role_name).first()
        if user and role:
            if role not in user.roles:
                user.roles.append(role)
                cls.session = cls.Session()
                cls.session.commit()
                cls.session.close()

    @classmethod
    def _create_admin_users(cls):
        try:
            # Load the config from the config file
            with open('configuration/config.toml', 'r') as file:
                config = toml.load(file)

            # Initialize roles and permissions from config
            for role_name in config['users']['elevated_users']:
                cls._create_role_if_not_exists(role_name)

            for role_name, permissions in config['permissions'].items():
                for permission_name in permissions:
                    cls._create_permission_if_not_exists(permission_name)
                    cls._assign_permission_to_role(permission_name, role_name)

            elevated_users = config['users']['elevated_users']
            for i, username in enumerate(elevated_users, start=1):
                admin_user = User(
                    id=i,
                    username=username,
                    password=generate_password_hash(username),
                    admin=True
                )

                cls.session = cls.Session()
                cls.session.add(admin_user)
                cls.session.commit()
                cls.session.close()

                cls._assign_role_to_user(username=username, role_name=username)


        except SQLAlchemyError as e:
            print(f"Error creating admin users: {e}")

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
            # Create all tables before each test
            self.session = self.Session()
            db.metadata.create_all(self.engine)
            # Create admin users
            self._create_admin_users()
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
            # Drop all tables after each test
            db.metadata.drop_all(self.engine)
        except SQLAlchemyError as e:
            print(f"Error during teardown: {e}")

    def _create_test_user(self, username="testuser", password="C0mpl3x!"):
        try:
            user = User(username=username, password=generate_password_hash(password))
            self.session.add(user)
            self.session.commit()
            return user.id
        except SQLAlchemyError as e:
            print(f"Error creating test user: {e}")
            self.fail(f"Failed to create test user: {e}")

    def _create_test_note(self, user_id, content):
        try:
            note = Note(content=content, user_id=user_id)
            self.session.add(note)
            self.session.commit()
            return note.id
        except SQLAlchemyError as e:
            print(f"Error creating test note: {e}")
            self.fail(f"Failed to create test note: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
