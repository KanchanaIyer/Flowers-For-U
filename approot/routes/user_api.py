from flask import Blueprint, request

from approot.data_managers.user_manager import UserManager
from approot.sessions import create_session, delete_session, get_session
from approot.utils.utils import handle_json_error, error_response, success_response

user_api = Blueprint('user_api', __name__, url_prefix='/api/user')


@user_api.route('login/', methods=['POST'])
def login():
    """
    Endpoint for logging in.
    :return:
    """
    data = request.get_json()

    (resp, status), user = UserManager.login(**data)

    if user and status == 200:  # Log in the user if login was successful
        create_session(user['user_id'])
        resp.set_cookie('key', get_session()['key'])

    return resp, status


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
    (resp, status), user = UserManager.register(**data)
    if user and status == 200:  # Log in the user if registration was successful
        create_session(user['user_id'])
        resp.set_cookie('key', get_session()['key'])
    return resp, status


@user_api.route('status/', methods=['GET'])
def status():
    """
    Endpoint for getting the status of the current user. By checking for user id in the session.
    :return:
    """
    if get_session().get('user'):
        return success_response("Logged in", {})
    else:
        return error_response("Not logged in", 401)
    