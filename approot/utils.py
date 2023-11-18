import mariadb
from flask import jsonify, Response
import json

from database import get_cursor
import models
VALID_FILTERS = ['name', 'price']
VALID_FILTER_RULES = ['contains', 'equals', 'greater', 'less']


class InvalidActionError(Exception):
    pass


def create_filter_query(filters: list[models.Filter]):
    """
    Creates a query string based on the filters provided
    :param filters: List of filters to apply
    :return: A string containing the query
    """
    query = ""
    for _filter in filters:
        if _filter.field in VALID_FILTERS and _filter.rule in VALID_FILTER_RULES:
            if _filter.rule == 'contains':
                query += f"AND {_filter.field} LIKE '%{_filter.value}%' "
            elif _filter.rule == 'equals':
                query += f"AND {_filter.field} = '{_filter.value}' "
            elif _filter.rule == 'greater':
                query += f"AND {_filter.field} > '{_filter.value}' "
            elif _filter.rule == 'less':
                query += f"AND {_filter.field} < '{_filter.value}' "
        else:
            raise ValueError(f"Invalid filter: {_filter}")
    return query


def success_response(message, data=None):
    if data is None:
        data = dict()
    return jsonify({"status": "success", "message": message, "data": data})


def error_response(message, status_code=500, data=None):
    if data is None:
        data = dict()
    return Response(f'{{"status":"error","message":"{message}", "data": {data}}}', status=status_code,
                    mimetype='application/json')


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


def handle_json_error(exception):
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


class ProductManager:
    """
    This class contains static methods for managing products. CRUD (just learned it)
    This moves the logic out of the API endpoints and into a separate class. The api module is now so much smaller.
    """
    @staticmethod
    def get_all_products(filters=None, limit=10, offset=0):
        try:
            database, cursor = get_cursor()
        except mariadb.Error as e:
            return handle_database_error(e)

        try:
            n_offset = limit * offset  # Calculate the offset based on the limit and offset provided

            query = "SELECT * FROM products WHERE 1=1 {} LIMIT {} OFFSET {}".format(
                create_filter_query(filters) if filters else '', limit, n_offset)
            cursor.execute(query)
            data = cursor.fetchall()
            return success_response("Success", data)
        except mariadb.Error as e:
            return handle_database_error(e)

    @staticmethod
    def add_product(product_data):
        try:
            database, cursor = get_cursor()
        except mariadb.Error as e:
            return handle_database_error(e)

        try:
            cursor.execute("INSERT INTO products (NAME, PRICE, DESCRIPTION, STOCK, LOCATION) VALUES (?, ?, ?, ?, ?)",
                           (product_data['name'], product_data['price'], product_data['description'],
                            product_data['stock'], product_data['location']))
            database.commit()
            return success_response("Inserted product successfully")
        except mariadb.Error as e:
            return handle_database_error(e)

    @staticmethod
    def get_product_by_id(product_id):
        try:
            database, cursor = get_cursor()
        except mariadb.Error as e:
            return handle_database_error(e)

        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            data = cursor.fetchall()
            return success_response("Success", data)
        except mariadb.Error as e:
            return handle_database_error(e)

    @staticmethod
    def update_product(product_id, product_data):
        try:
            database, cursor = get_cursor()
        except mariadb.Error as e:
            return handle_database_error(e)

        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ? FOR UPDATE", (product_id,))
            cursor.execute("UPDATE products SET NAME = COALESCE(?, NAME), PRICE = COALESCE(?, PRICE),"
                           " DESCRIPTION = COALESCE(?, DESCRIPTION), STOCK = COALESCE(?, STOCK), LOCATION = COALESCE(?, LOCATION)"
                           " WHERE product_id = ?",
                           (product_data.get('name'), product_data.get('price'), product_data.get('description'),
                            product_data.get('stock'), product_data.get('location'), product_id))
            database.commit()
            return success_response("Updated product successfully")
        except mariadb.Error as e:
            return handle_database_error(e)

    @staticmethod
    def delete_product(product_id):
        try:
            database, cursor = get_cursor()
        except mariadb.Error as e:
            return handle_database_error(e)

        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ? FOR UPDATE", (product_id,))
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            cursor.execute("SELECT ROW_COUNT()")
            if cursor.fetchone()["ROW_COUNT()"] == 0:
                raise mariadb.Error("Product not found")
            database.commit()
            return success_response("Deleted product successfully")
        except mariadb.Error as e:
            return handle_database_error(e)

    @staticmethod
    def update_product_stock(product_id, data):
        try:
            database, cursor = get_cursor()
        except mariadb.Error as e:
            return handle_database_error(e)
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            product = cursor.fetchone()

            if not product:
                raise mariadb.Error("Product not found")

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
                raise InvalidActionError("Invalid action")

            database.commit()
            return success_response("Updated stock successfully")
        except mariadb.Error as e:
            database.rollback()
            return handle_database_error(e)
        except InvalidActionError as e:
            return handle_validation_error(str(e))

    @staticmethod
    def buy_product(product_id, data):
        try:
            database, cursor = get_cursor()
        except mariadb.Error as e:
            return handle_database_error(e)

        try:
            cursor.execute("SELECT stock FROM products WHERE product_id = ? FOR UPDATE", (product_id,))
            current_stock = cursor.fetchone()['stock']

            quantity = data.get('quantity', 1)
            if current_stock < quantity:
                raise mariadb.Error("Not enough stock available")

            cursor.execute("UPDATE products SET stock = stock - ? WHERE product_id = ?", (quantity, product_id))
            database.commit()

            return success_response("Bought product successfully")
        except mariadb.Error as e:
            database.rollback()
            return handle_database_error(e)
