from flask import Blueprint, request

from approot.data_managers.user_manager import UserManager
from approot.sessions import create_session, delete_session, get_session
from approot.utils.utils import error_response, success_response, handle_error_flask

user_api = Blueprint('user_api', __name__, url_prefix='/api/user')


@user_api.route('login/', methods=['POST'])
@handle_error_flask
def login():
    """
    Endpoint for logging in.
    :return:
    """
    data = request.get_json()

    user = UserManager.login(**data)

    # Log The User In
    create_session(user) # Create a session for the user
    session_key = get_session()['key']

    response, status_code = success_response("Successfully logged in", {'key': session_key})
    response.set_cookie('key', session_key, max_age=3600)

    return response, status_code


@user_api.route('logout/', methods=['POST'])
def logout():
    """
    Endpoint for logging out.
    :return:
    """
    delete_session()
    return success_response("Successfully logged out", {})


@user_api.route('register/', methods=['POST'])
def register():
    """
    Endpoint for registering.
    :return:
    """
    data = request.get_json()
    user = UserManager.register(**data)

    create_session(user)
    resp, status_code = success_response("Successfully registered", {"key": get_session()['key']})
    resp.set_cookie('key', get_session()['key'], max_age=3600)
    return resp, status_code


@user_api.route('status/', methods=['GET'])
def status():
    """
    Endpoint for getting the status of the current user. By checking for username in the session.
    :return: 200 if logged in, 401 if not logged in
    """

    if get_session().get('user'):
        return success_response("Logged in", {})
    else:
        return error_response("Not logged in", 401)


@user_api.route('info/', methods=['GET'])
def info():
    """
    Endpoint for getting the info of the current user.
    :return: 200 with user info if logged in, 401 if not logged in
    """
    if get_session().get('user_id'):
        user = UserManager.get_user_by_id(get_session()['user_id'])
        print(user)
        return success_response("Logged in", user.to_dict())
    else:
        return error_response("Not logged in", 401)
