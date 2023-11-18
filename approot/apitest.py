from functools import wraps

from flask import Flask, render_template, request
from config import get_flask_config
from database import get_cursor
from models import Product, Filter
from utils import success_response, error_response, handle_unauthorized, handle_json_error, handle_database_error, \
    handle_validation_error, ProductManager
import mariadb

flask_config = get_flask_config()
app = Flask(__name__,
            static_url_path='',
            static_folder='../webroot/static',
            template_folder='../webroot/templates')



authorized_keys = ['1234', '5678', '9101']


def validate_key(key):
    print(key)
    if key in authorized_keys:
        return True
    else:
        return False


def validate_key_(func):
    """
    Decorator for validating the key cookie.
    Endpoints with this decorator require the key cookie to be set to a valid key.
    :param func:
    :return:
    """
    @wraps(func)  # Without this, the flask is angry because the name of the function is changed
    def wrapper(*args, **kwargs):
        if not validate_key(request.cookies.get('key')):
            return handle_unauthorized()
        return func(*args, **kwargs)

    return wrapper


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/api', methods=['GET', 'POST'])
def api_test():
    data = "Hello from a GET"
    return success_response("APIv1", {'data': data})


@app.route('/api/products', methods=['GET'], endpoint='get_products')
@validate_key_
def get_products():
    """
    Endpoint for getting products.

    GET requests are used to query products.
    The Content-Type header must be set to application/json.
    The body must be a JSON object containing the following optional parameters:
        filters - An array of filters to apply to the query. Each filter must be a JSON object containing the following:
            field - The field to filter by. Must be one of the following: name, price.
            rule - The rule to apply to the filter. Must be one of the following: contains, equals, greater, less.
            value - The value to filter by.
        limit - The maximum number of results to return.
        offset - The offset to start the query at.

    :return: A JSON object containing the status of the request and any data.
    """
    try:
        body = request.get_json()
    except Exception as e:
        return handle_json_error(e)

    return ProductManager.get_all_products(filters=[Filter.from_dict(_filter) for _filter in body.get('filters')], limit=body.get('limit', 10),
                                           offset=body.get('offset', 0))


@app.route('/api/products', methods=['POST'], endpoint='add_product')
@validate_key_
def add_product():
    """
    Endpoint for adding products.

    POST requests are used to add products.
    The Content-Type header must be set to application/json.
    The body must be a JSON object containing the following:
        name - The name of the product.
        price - The price of the product.
        description - The description of the product.
        stock - The stock of the product.
        location - The location of the product.

    :return: A JSON object containing the status of the request.
    """
    try:
        data = request.get_json()
    except Exception as e:
        return handle_json_error(e)

    return ProductManager.add_product(data)


@app.route('/api/products/<int:product_id>', methods=['GET'])
@validate_key_
def get_product(product_id: int):
    """
    Endpoint for getting a specific product
    Get requests are used to get a specific product.

    This endpoint requires the product_id to be specified in the URL and as such does not require a body.
    For standardization, the Content-Type header should be set to application/json.
    :param product_id: The ID of the product to get.
    :return:
    """
    return ProductManager.get_product_by_id(product_id)


@app.route('/api/products/<int:product_id>', methods=['PUT'])
@validate_key_
def modify_product(product_id):
    """
    Endpoint for modifying a specific product.
    PUT requests are used to modify a specific product.

    The Content-Type header must be set to application/json.
    The body must be a JSON object containing the following optional parameters:
        name - The name of the product.
        price - The price of the product.
        description - The description of the product.
        stock - The stock of the product.
        location - The location of the product.
    :param product_id: The ID of the product to modify.
    :return:
    """
    try:
        data = request.get_json()
    except Exception as e:
        return handle_json_error(e)

    return ProductManager.update_product(product_id, data)


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@validate_key_
def remove_product(product_id):
    """
    Endpoint for removing a specific product.
    DELETE requests are used to remove a specific product.

    This endpoint requires the key Cookie to be set to a valid key.
    For standardization, the Content-Type header should be set to application/json.
    :param product_id: The ID of the product to remove.
    :return:
    """
    return ProductManager.delete_product(product_id)


@app.route('/api/products/<int:product_id>/update-stock', methods=['POST'])
@validate_key_
def update_product_stock(product_id):
    """
    Endpoint for updating the stock of a specific product. This is preferred over the /api/products/id PUT endpoint for stock completed by the owner.
    POST requests are used to update the stock of a specific product.

    The Content-Type header must be set to application/json.
    The body must be a JSON object containing the following:
        quantity - The quantity to add or subtract from the current stock.
        action - Either "add" or "subtract" to indicate whether to add or subtract from the stock.
    :return: A JSON object indicating the status of the stock update.
    """
    try:
        data = request.get_json()
    except Exception as e:
        return handle_json_error(e)

    return ProductManager.update_product_stock(product_id, data)


@app.route('/api/products/buy/<int:product_id>', methods=['POST'])
@validate_key_
def api_product_buy(product_id):
    """
    Endpoint for buying a product. Automatically subtracts the quantity from the stock.
    POST requests are used to buy a product.
    The cookie key must be set to a valid key.
    The connection must be https (for security).

    The Content-Type header must be set to application/json.
    The body must be a JSON object containing the following:
        quantity - The quantity of the product to buy.
    :return: A JSON object indicating the status of the purchase.
    """
    # Check if https
    if request.headers.get('X-Forwarded-Proto') != 'https':
        return error_response("HTTPS Required", 400)

    try:
        data = request.get_json()
    except Exception as e:
        return handle_json_error(e)

    return ProductManager.buy_product(product_id, data)


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data['key'] in authorized_keys:
        return success_response("Logged in successfully", {'key': data['key']})
    else:
        return error_response("Invalid key", 401)


if __name__ == '__main__':
    app.run(debug=flask_config['debug'] == "ENABLED", host=flask_config['host'], port=flask_config['port'])
