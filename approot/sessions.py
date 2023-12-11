from flask import session
from approot.crypto.crypto import generate_session_key


def create_session(user):
    session['user_id'] = user
    session['key'] = generate_session_key()
    return session


def get_session():
    return session


def delete_session():
    session.pop('user', None)
    session.pop('key', None)
    session.pop('admin', None)
    session.pop('user_id', None)
    return session



