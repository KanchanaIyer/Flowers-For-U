import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_key():
    return bcrypt.gensalt().decode('utf-8')

def hash_key(key):
    return bcrypt.hashpw(key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_key(key, hashed_key):
    return bcrypt.checkpw(key.encode('utf-8'), hashed_key.encode('utf-8'))

def generate_session_key():
    return bcrypt.gensalt().decode('utf-8')