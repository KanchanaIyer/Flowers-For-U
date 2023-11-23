from flask import session
from crypto import generate_session_key, hash_key, check_key


def create_session(user):
    session['user'] = user
    session['key'] = generate_session_key()
    return session


def get_session():
    return session


def delete_session():
    session.pop('user', None)
    session.pop('key', None)
    return session



