import logging

import mariadb

from approot.crypto.crypto import check_password, hash_password
from approot.database.database_manager import database_transaction_helper
from approot.data_managers.errors import NotFoundError
from approot.database.models import User
from approot.utils.utils import success_response, handle_not_found_error


class UserManager:
    """
    This class contains static methods for managing user authentication and registration by accessing the database.
    """

    @staticmethod
    @database_transaction_helper
    def get_user_by_id(user_id: int, cursor=None, database=None) -> User:
        """
        Gets a user from the database by their id
        :param int user_id: Id of the user to get
        :param cursor:
        :param database:
        :return: User object representing the user that was retrieved
        :raises NotFoundError: If no user is found with the provided id
        """
        try:
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            if user is None:
                raise NotFoundError("No user found with the provided id")
            return User.from_dict(user)
        except NotFoundError as e:
            raise e

    @staticmethod
    @database_transaction_helper
    def login(username: str, password: str, cursor=None, database=None) -> User:
        """
        Logs a user in by checking the provided credentials against the database
        :param str username: Username of the user to log in
        :param str password: Password of the user to log in
        :param cursor:
        :param database:
        :return: User object representing the user that was logged in
        :raises KeyError: If a required field is missing
        :raises NotFoundError: If no user is found with the provided credentials
        """
        try:
            # print(username, password)

            if not all((username, password)):
                raise KeyError("Missing required field")

            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            # print(f"Cursor: {cursor}")
            prospective_user = cursor.fetchone()
            # print(f"P User: {prospective_user}")

            if prospective_user is None:
                raise NotFoundError("No user found with the provided credentials. Cannot login")

            if not check_password(password, prospective_user['password']):
                raise NotFoundError("No user found with the provided credentials. Cannot login")

            user = prospective_user

            # Get user Admin status
            cursor.execute("SELECT * FROM administrators WHERE user_id = ?", (user['user_id'],))
            admin = cursor.fetchone()
            if admin is not None:
                user['is_admin'] = True
            else:
                user['is_admin'] = False

            return User.from_dict(user)

        except NotFoundError as e:
            raise e
        except KeyError as e:
            raise e

    @staticmethod
    @database_transaction_helper
    def register(username: str, password: str, email: str, cursor=None, database=None) -> User:
        """
        Registers a user by inserting the provided credentials into the database and validating them
        :param str username: Username of the user to register
        :param str password: Password of the user to register
        :param str email: Email of the user to register
        :param cursor:
        :param database:
        :return: User object representing the user that was registered
        :raises KeyError: If a required field is missing
        :raises mariadb.IntegrityError: If the username or email already exists in the database
        """
        if not all((username, password, email)):
            raise KeyError("Missing required field")

        try:
            secure_password = hash_password(password)
            cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                           (username, secure_password, email))
            last_id = cursor.lastrowid
            database.commit()

            user = {'user_id': last_id, 'username': username, 'email': email, 'is_admin': False}

            return User.from_dict(user)

        except mariadb.IntegrityError as e:
            e.args = ("Username or email already exists",)
            raise e
        except KeyError as e:
            raise e
        except Exception as e:
            logging.exception(e)
            raise e
