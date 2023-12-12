import logging
from functools import wraps

import mariadb
import werkzeug.exceptions
from flask import jsonify, request
import json
import requests
from werkzeug.utils import secure_filename

from approot import SERVER_ROOT
from approot.crypto.crypto import hash_key
from approot.sessions import get_session

from approot.data_managers.errors import InvalidActionError, InvalidMimetypeError, NotFoundError
from approot.database import models
from approot.database.database_manager import database_transaction_helper

UPLOAD_FOLDER = SERVER_ROOT / 'webroot/static/images/products'
SERVER_URL_ROOT = '/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif'}


def generate_unique_filename(filename):
    """
    Generates a unique filename for a file It will keep hashing the filename until it is unique
    :param filename: Name of the file to generate a unique filename for
    :return: A unique filename
    """
    filename = f"{hash_key(filename)}.{filename.rsplit('.', 1)[1].lower()}"
    if (UPLOAD_FOLDER / filename).exists():
        return generate_unique_filename(filename)
    else:
        return filename


def allowed_file(filename):
    """
    Checks if a file is allowed to be uploaded
    :param filename: Name of the file to check
    :return: True if the file is allowed, otherwise False
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image_to_disk_by_url(url):
    """
    Saves an image to disk
    :param url: URL of the image to save
    :return: Path to the saved image
    """
    if url:
        logging.debug(f"URL: {url}")
        response = requests.get(url)
        mimetype = response.headers.get('content-type')
        logging.debug(f"Mimetype: {mimetype}")
        if mimetype.strip() in ALLOWED_MIME_TYPES:
            logging.debug(f"Saving image to disk. Size: {len(response.content)} bytes")
            filename = secure_filename(generate_unique_filename(response.url.rsplit('/', 1)[1]))
            filepath = UPLOAD_FOLDER / filename
            with open(filepath, 'wb') as f:
                logging.debug(f"Writing to file: {filepath}")
                f.write(response.content)

            server_url = f"{SERVER_URL_ROOT}/{filename}"
            logging.debug(f"Server URL: {server_url}")
            return server_url
        else:
            raise InvalidMimetypeError(f"Invalid mimetype: {mimetype}")
    else:
        return None


def save_image_to_disk_by_file(image):
    """
    Saves an image to disk
    :param image: Image to save
    :return: Path to the saved image
    """
    if image:
        mimetype = image.mimetype
        if mimetype in ALLOWED_MIME_TYPES:
            filename = secure_filename(generate_unique_filename(image.filename))
            filepath = UPLOAD_FOLDER / filename
            image.save(filepath)
            server_url = f"{SERVER_URL_ROOT}/{filename}"
            return server_url
        else:
            raise InvalidMimetypeError(f"Invalid mimetype: {mimetype}")
    else:
        return None


VALID_FILTERS = ['name', 'price', 'stock']
VALID_FILTER_RULES = ['contains', 'equals', 'greater', 'less']
FILTER_MAP = {
    'name': ['contains'],
    'price': ['equals', 'greater', 'less'],
    'stock': ['equals', 'greater', 'less', 'exists'],

}


def handle_error_flask(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except json.JSONDecodeError as e:
            return handle_json_error(e)
        except mariadb.Error as e:
            return handle_database_error(e)
        except NotFoundError as e:
            return handle_not_found_error(e)
        except (InvalidActionError, InvalidMimetypeError) as e:
            return handle_validation_error(e)
        except Exception as e:
            return handle_unknown_error(e)
    return wrapper


def validate_key_(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_key = request.cookies.get('key')
        session = get_session()
        print(str(session))
        print(user_key)
        session_key = get_session().get('key')
        if not user_key or (user_key != session_key):
            return handle_unauthorized()

        return func(*args, **kwargs)

    return wrapper


def create_filter_query(filters: list[models.Filter]):
    """
    Creates a query string based on the filters provided
    :param filters: List of filters to apply
    :return: A string containing the query
    """

    query = ""
    for _filter in filters:
        if _filter:

            if _filter.field in FILTER_MAP.keys() and _filter.rule in FILTER_MAP[_filter.field]:

                if _filter.rule == 'contains':
                    query += f"{_filter.comparator} {'NOT' if _filter.negate else ''} {_filter.field} LIKE '%{_filter.value}%' "
                elif _filter.rule == 'equals':
                    query += f"{_filter.comparator} {'NOT' if _filter.negate else ''} {_filter.field} = '{_filter.value}' "
                elif _filter.rule == 'greater':
                    query += f"{_filter.comparator} {'NOT' if _filter.negate else ''} {_filter.field} > '{_filter.value}' "
                elif _filter.rule == 'less':
                    query += f"{_filter.comparator} {'NOT' if _filter.negate else ''} {_filter.field} < '{_filter.value}' "
                elif _filter.rule == 'exists':
                    query += f"{_filter.comparator} {'NOT' if _filter.negate else ''} {_filter.field} > '{0}' "
            else:
                raise InvalidActionError(f"Invalid filter: {str(_filter)} {FILTER_MAP.get(_filter.field, [])}")
    return query


def success_response(message, data=None):
    if data is None:
        data = dict()
    return jsonify({"status": "success", "message": message, "data": data}), 200


def error_response(message, status_code=500, data=None):
    if data is None:
        data = dict()
    return jsonify({"status": "error", "message": message, "data": data}), status_code


def handle_unauthorized():
    return error_response("Unauthorized Key", 401)


def handle_validation_error(message):
    return error_response(f'Validation Error: {message}', 400)


def handle_unknown_error(message):
    return error_response(f'Unknown Error: {message}', 500)


def handle_database_error(exception):
    if isinstance(exception, mariadb.IntegrityError):
        status_code = 409  # Conflict
        error_message = f'Database Integrity Error: {str(exception)}'
    elif isinstance(exception, mariadb.OperationalError):
        status_code = 500
        error_message = f'Database Operational Error: {str(exception)}'
    elif isinstance(exception, mariadb.ProgrammingError):
        status_code = 500
        error_message = f'Database Programming Error: {str(exception)}'
    else:
        status_code = 500
        error_message = f'Unexpected Database Error: {str(exception)}'

    return error_response(error_message, status_code)


def handle_not_found_error(message):
    return error_response(f'Not Found Error: {message}', 404)


def handle_json_error(exception):
    # Does not currently work as intended as request.get_json() throws a 400 error before this is called...
    if isinstance(exception, (json.JSONDecodeError, werkzeug.exceptions.BadRequest)):
        status_code = 400
        error_message = f'JSON decoding error: {str(exception)}'
    elif isinstance(exception, (ValueError, TypeError)):
        status_code = 400
        error_message = f'JSON Error: {str(exception)}'
    else:
        status_code = 500
        error_message = f'Unexpected JSON-related error: {str(exception)}'

    return error_response(error_message, status_code)


class ReviewManager:
    """
    This class contains static methods for managing reviews.
    """

    @staticmethod
    @database_transaction_helper
    def get_all_reviews(filters=None, limit=10, offset=0, cursor=None, database=None):
        """
        Gets all reviews from the database
        :param list[dict] filters: List of filters to apply
        :param int limit: Maximum number of results to return
        :param int offset: Offset to start the query at
        :param cursor: Database cursor to use
        :param database: Database connection to use
        :return: Flask Response object containing the status of the request and any data
        """
        try:
            n_offset = limit * offset  # Calculate the offset based on the limit and offset provided

            query = "SELECT * FROM reviews WHERE 1=1 {} LIMIT {} OFFSET {}".format(
                create_filter_query(filters) if filters else '', limit, n_offset)
            cursor.execute(query)
            data = cursor.fetchall()

            if not data or all(all(x for x in obj.values()) for obj in data):
                raise NotFoundError("No reviews found which match the provided filters or limit/offset")

            return data

        except InvalidActionError as e:
            raise e
        except NotFoundError as e:
            raise e
