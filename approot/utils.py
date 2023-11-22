from functools import wraps

import mariadb
from flask import jsonify, Response
import json
from contextlib import contextmanager

from database import get_cursor
import models

VALID_FILTERS = ['name', 'price']
VALID_FILTER_RULES = ['contains', 'equals', 'greater', 'less']
FILTER_MAP = {
    'name': ['contains'],
    'price': ['equals', 'greater', 'less'],
    'stock': ['equals', 'greater', 'less', 'exists'],

}


class InvalidActionError(Exception):
    pass


class ProducetNotFoundError(Exception):
    pass


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
                    query += f"AND {_filter.field} LIKE '%{_filter.value}%' "
                elif _filter.rule == 'equals':
                    query += f"AND {_filter.field} = '{_filter.value}' "
                elif _filter.rule == 'greater':
                    query += f"AND {_filter.field} > '{_filter.value}' "
                elif _filter.rule == 'less':
                    query += f"AND {_filter.field} < '{_filter.value}' "
                elif _filter.rule == 'exists':
                    query += f"AND {_filter.field} > '{0}' "
            else:
                raise InvalidActionError(f"Invalid filter: {str(_filter)} {FILTER_MAP.get(_filter.field, [])}")
    return query


def success_response(message, data=None):
    if data is None:
        data = dict()
    return jsonify({"status": "success", "message": message, "data": data})


def error_response(message, status_code=500, data=None):
    if data is None:
        data = dict()
    return jsonify({"status": "error", "message": message, "data": data}), status_code


def handle_unauthorized():
    return error_response("Unauthorized Key", 401)


def handle_validation_error(message):
    return error_response(f'Validation Error: {message}', 400)


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
    if isinstance(exception, json.JSONDecodeError):
        status_code = 400
        error_message = f'JSON decoding error: {str(exception)}'
    elif isinstance(exception, (ValueError, TypeError)):
        status_code = 400
        error_message = f'JSON Error: {str(exception)}'
    else:
        status_code = 500
        error_message = f'Unexpected JSON-related error: {str(exception)}'

    return error_response(error_message, status_code)


@contextmanager
def get_database_connection():
    """
    Context manager for getting a database connection and cursor
    :return: database connection and cursor
    """
    try:
        database, cursor = get_cursor()
        yield database, cursor
    except mariadb.Error as e:
        yield None, None
        return handle_database_error(e)


def database_transaction_helper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_database_connection() as (database, cursor):
            if database is None:
                raise mariadb.Error("Failed to connect to database")
            try:
                return func(database=database, cursor=cursor, *args, **kwargs)
            except mariadb.Error as e:
                database.rollback()
                return handle_database_error(e)
    return wrapper



class ReviewManager:
    """
    This class contains static methods for managing reviews.
    """
    @staticmethod
    @database_transaction_helper
    def get_all_reviews(filters=None, limit=10, offset=0, cursor=None, database=None):
        try:
            n_offset = limit * offset  # Calculate the offset based on the limit and offset provided

            query = "SELECT * FROM reviews WHERE 1=1 {} LIMIT {} OFFSET {}".format(
                create_filter_query(filters) if filters else '', limit, n_offset)
            cursor.execute(query)
            data = cursor.fetchall()

            if not data or all(all(x for x in obj.values()) for obj in data):
                raise ProducetNotFoundError("No reviews found which match the provided filters or limit/offset")

            return success_response("Success", data)

        except InvalidActionError as e:
            return handle_validation_error(str(e))
        except ProducetNotFoundError as e:
            return handle_not_found_error(str(e))

class ProductManager:
    """
    This class contains static methods for managing products. CRUD (just learned it)
    This moves the logic out of the API endpoints and into a separate class. The api module is now so much smaller.
    """

    @staticmethod
    @database_transaction_helper
    def get_all_products(filters=None, limit=10, offset=0, cursor=None, database=None):
        try:
            n_offset = limit * offset  # Calculate the offset based on the limit and offset provided

            query = "SELECT * FROM products WHERE 1=1 {} LIMIT {} OFFSET {}".format(
                create_filter_query(filters) if filters else '', limit, n_offset)
            cursor.execute(query)
            data = cursor.fetchall()
            print(data)

            if not data or all(all(not x for x in obj.values()) for obj in data):
                raise ProducetNotFoundError("No products found which match the provided filters or limit/offset")

            return success_response("Success", data)

        except InvalidActionError as e:
            return handle_validation_error(str(e))
        except ProducetNotFoundError as e:
            return handle_not_found_error(str(e))

    @staticmethod
    @database_transaction_helper
    def add_product(product_data, cursor=None, database=None):
        try:
            cursor.execute("INSERT INTO products (NAME, PRICE, DESCRIPTION, STOCK, LOCATION) VALUES (?, ?, ?, ?, ?)",
                           (product_data['name'], product_data['price'], product_data['description'],
                            product_data['stock'], product_data['location']))
            database.commit()
            return success_response("Inserted product successfully")

        except KeyError as e:
            return handle_validation_error(f"Missing required field: {str(e)}")

    @staticmethod
    @database_transaction_helper
    def get_product_by_id(product_id, cursor=None, database=None):
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            data = cursor.fetchall()

            if data is None:
                raise ProducetNotFoundError("No product found with the provided ID. Cannot show")

            return success_response("Success", data)

        except ProducetNotFoundError as e:
            return handle_not_found_error(str(e))

    @staticmethod
    @database_transaction_helper
    def update_product(product_id, product_data, cursor=None, database=None):
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ? FOR UPDATE", (product_id,))

            if cursor.fetchone() is None:
                raise ProducetNotFoundError("No product found with the provided ID. Cannot update")

            cursor.execute("UPDATE products SET NAME = COALESCE(?, NAME), PRICE = COALESCE(?, PRICE),"
                           " DESCRIPTION = COALESCE(?, DESCRIPTION), STOCK = COALESCE(?, STOCK), LOCATION = COALESCE(?, LOCATION)"
                           " WHERE product_id = ?",
                           (product_data.get('name'), product_data.get('price'), product_data.get('description'),
                            product_data.get('stock'), product_data.get('location'), product_id))
            database.commit()
            return success_response("Updated product successfully")

        except ProducetNotFoundError as e:
            return handle_not_found_error(str(e))

    @staticmethod
    @database_transaction_helper
    def delete_product(product_id, cursor=None, database=None):
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ? FOR UPDATE", (product_id,))

            if cursor.fetchone() is None:
                raise ProducetNotFoundError("No product found with the provided ID. Cannot delete")

            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))

            database.commit()
            return success_response("Deleted product successfully")

        except ProducetNotFoundError as e:
            return handle_not_found_error(str(e))

    @staticmethod
    @database_transaction_helper
    def update_product_stock(product_id, data, cursor=None, database=None):
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            product = cursor.fetchone()

            if not product:
                raise ProducetNotFoundError("No product found with the provided ID. Cannot update stock")

            quantity = data.get('quantity', 0)

            if data['action'] == 'add':
                cursor.execute("UPDATE products SET stock = stock + ? WHERE product_id = ?",
                               (quantity, product_id))
            elif data['action'] == 'subtract':
                if product['stock'] < data['quantity']:
                    raise mariadb.Error("Not enough stock available")
                cursor.execute("UPDATE products SET stock = stock - ? WHERE product_id = ?",
                               (quantity, product_id))
            else:
                raise InvalidActionError(f"Invalid action: '{data['action']}'")

            database.commit()
            return success_response("Updated stock successfully")

        except InvalidActionError as e:
            return handle_validation_error(str(e))
        except ProducetNotFoundError as e:
            return handle_not_found_error(str(e))

    @staticmethod
    @database_transaction_helper
    def buy_product(product_id, data, cursor=None, database=None):
        try:
            cursor.execute("SELECT stock FROM products WHERE product_id = ? FOR UPDATE", (product_id,))

            product = cursor.fetchone()
            if product is None:
                raise ProducetNotFoundError("No product found with the provided ID. Cannot buy")

            current_stock = product['stock']

            quantity = data.get('quantity', 1)
            if current_stock < quantity:
                raise mariadb.Error("Not enough stock available")

            cursor.execute("UPDATE products SET stock = stock - ? WHERE product_id = ?", (quantity, product_id))
            database.commit()

            return success_response("Bought product successfully")

        except ProducetNotFoundError as e:
            return handle_not_found_error(str(e))
