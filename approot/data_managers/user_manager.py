from approot.crypto.crypto import check_password
from approot.database.database_manager import database_transaction_helper
from approot.data_managers.errors import NotFoundError
from approot.utils.utils import success_response, handle_not_found_error


class UserManager:
    """
    This class contains static methods for managing user authentication and registration by accessing the database.
    """

    @staticmethod
    @database_transaction_helper
    def login(username, password, cursor=None, database=None):
        """
        Logs a user in by checking the provided credentials against the database
        :param str username: Username of the user to log in
        :param str password: Password of the user to log in
        :param cursor:
        :param database:
        :return: Tuple of Flask Response object containing the status of the request and a dict representing the user (this may be changed to a user object in the future), or None if login failed
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

            return success_response("Logged in successfully"), user

        except NotFoundError as e:
            return handle_not_found_error(str(e)), None
        except KeyError as e:
            return handle_validation_error(str(e)), None

    @staticmethod
    @database_transaction_helper
    def register(username, password, email, cursor=None, database=None):
        """
        Registers a user by inserting the provided credentials into the database and validating them
        :param str username: Username of the user to register
        :param str password: Password of the user to register
        :param str email: Email of the user to register
        :param cursor:
        :param database:
        :return: Flask Response object containing the status of the request and a dict representing the user (this may be changed to a user object in the future), or None if registration failed
        """
        if not all((username, password, email)):
            raise KeyError("Missing required field")
        try:
            secure_password = hash_password(password)
            cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                           (username, secure_password, email))
            user = cursor.lastrowid
            database.commit()
            return success_response("Registered successfully"), user

        except mariadb.IntegrityError as e:
            return handle_validation_error("Username already exists"), None
        except KeyError as e:
            return handle_validation_error(str(e)), None