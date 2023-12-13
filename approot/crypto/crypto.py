import bcrypt

def hash_password(password):
    """
    Hashes a password using bcrypt
    :param password:
    :return:
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def check_password(password, hashed_password):
    """
    Checks a password against a hashed password using bcrypt
    :param password:
    :param hashed_password:
    :return:
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_key():
    """
    Generates a key using bcrypt
    :return:
    """
    return bcrypt.gensalt().decode('utf-8')

def hash_key(key):
    """
    Hashes a key using bcrypt
    :param key:
    :return:
    """
    return bcrypt.hashpw(key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_key(key, hashed_key):
    """
    Checks a key against a hashed key using bcrypt
    :param key:
    :param hashed_key:
    :return:
    """
    return bcrypt.checkpw(key.encode('utf-8'), hashed_key.encode('utf-8'))

def generate_session_key():
    """
    Generates a session key using bcrypt
    :return:
    """
    return bcrypt.gensalt().decode('utf-8')
