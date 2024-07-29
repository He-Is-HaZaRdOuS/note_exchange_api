import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
import toml
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Set the environment variable to determine the app configuration
os.environ['CONFIG'] = 'DEVELOPMENT'

from configuration.config import app, db
from application.models import User, Note, Friend, Role, Permission

def drop_all(engine):
    inspector = inspect(engine)

    # Disable foreign key checks
    with engine.connect() as connection:
        connection.execute(text('SET foreign_key_checks = 0;'))

    try:
        # Get all tables
        tables = inspector.get_table_names()

        # Drop all tables
        for table in tables:
            with engine.connect() as connection:
                connection.execute(text(f'DROP TABLE IF EXISTS `{table}`;'))

    except Exception as e:
        print(f"Error dropping tables: {e}")

    finally:
        # Re-enable foreign key checks
        with engine.connect() as connection:
            connection.execute(text('SET foreign_key_checks = 1;'))

def create_role_if_not_exists(session, role_name):
    role = session.query(Role).filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        session.add(role)
        session.commit()
    return role

def create_permission_if_not_exists(session, permission_name):
    permission = session.query(Permission).filter_by(name=permission_name).first()
    if not permission:
        permission = Permission(name=permission_name)
        session.add(permission)
        session.commit()
    return permission

def assign_permission_to_role(session, permission_name, role_name):
    role = session.query(Role).filter_by(name=role_name).first()
    permission = session.query(Permission).filter_by(name=permission_name).first()
    if role and permission:
        if not any(p.id == permission.id for p in role.permissions):
            role.add_permission(permission)
            session.commit()

def assign_role_to_user(session, username, role_name):
    user = session.query(User).filter_by(username=username).first()
    role = session.query(Role).filter_by(name=role_name).first()
    if user and role:
        if role not in user.roles:
            user.roles.append(role)
            session.commit()

def create_admin_users(session):
    try:
        # Load config from config file
        with open('configuration/elevated_users.toml', 'r') as file:
            config = toml.load(file)

        # Initialize roles and permissions from config
        for role_name in config['users']['elevated_users']:
            create_role_if_not_exists(session, role_name)

        for role_name, permissions in config['permissions'].items():
            for permission_name in permissions:
                create_permission_if_not_exists(session, permission_name)
                assign_permission_to_role(session, permission_name, role_name)

        # Create privileged admins from config
        elevated_users = config['users']['elevated_users']
        for i, username in enumerate(elevated_users, start=1):
            admin_user = User(
                id=i,
                username=username,
                password=generate_password_hash(username)
            )
            session.add(admin_user)
            session.commit()
            assign_role_to_user(session, username=username, role_name=username)

    except SQLAlchemyError as e:
        print(f"Error creating admin users: {e}")

# Main
with app.app_context():
    engine = db.engine
    Session = sessionmaker(bind=engine)

    # Drop all tables
    drop_all(engine)

    # Create all tables
    db.metadata.create_all(engine)

    session = Session()

    # Create and add admin users dynamically
    create_admin_users(session)

    session.close()
    print("Database initialized successfully")
