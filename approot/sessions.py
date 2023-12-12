from flask import session
from approot.crypto.crypto import generate_session_key
from approot.database.models import User


def create_session(user: User):
    session['user_id'] = user.user_id
    session['key'] = generate_session_key()
    session['user'] = user.username
    session['admin'] = user.is_admin

    # Set session expiration
    session.permanent = True
    session.modified = True
    session.permanent_session_lifetime = 3600  # 1 hour
    return session


def get_session():
    return session


def delete_session():
    session.pop('user', None)
    session.pop('key', None)
    session.pop('admin', None)
    session.pop('user_id', None)
    return session



