import json
from functools import wraps

import mariadb
from flask import Blueprint, request

from approot.data_managers.errors import NotFoundError, InvalidActionError
from approot.data_managers.product_manager import ProductManager
from approot.database.models import Filter
from approot.utils.utils import handle_unauthorized, error_response, handle_json_error, success_response, \
    validate_key_, save_image_to_disk_by_file, save_image_to_disk_by_url, InvalidMimetypeError, handle_not_found_error, \
    handle_database_error, handle_validation_error, handle_error_flask

product_api = Blueprint('product_api', __name__, url_prefix='/api/products')


def parse_image(data):
    if 'image' in request.files:  # Check if image is in files
        image = request.files['image']
        location = save_image_to_disk_by_file(image)
        return location
    elif 'image' in data:  # Check if image is in data
        location = save_image_to_disk_by_url(data['image'])
        return location
    else:
        return None


@product_api.errorhandler(404)
def page_not_found(e):
    return error_response("Resource not found", 404)


@product_api.errorhandler(500)
def internal_server_error(e):
    return error_response("Unhandled Internal server error", 500)


'''
@product_api.route('/', methods=['GET', 'POST'])
def api_test():
    data = "Hello from a GET"
    return success_response("APIv1", {'data': data})
'''


@product_api.route('/', methods=['GET'])
@handle_error_flask
def get_products():
    """
    Endpoint for getting products.

    GET requests are used to query products.
    The Content-Type header should be set to x-www-form-urlencoded.

    URL Parameters:
    - filters (optional): An array of filters to apply to the query. Each filter must be a JSON object containing the following:
        - field (str): The field to filter by. Must be one of the following: name, price.
        - rule (str): The rule to apply to the filter. Must be one of the following: contains, equals, greater, less.
        - value (str): The value to filter by.
    - limit (optional): The maximum number of results to return. Default is 10.
    - offset (optional): The offset to start the query at. Default is 0.

    Request:
    GET /api/products/?filters=[{"field": "name", "rule": "contains", "value": "Example"}]&limit=10&offset=0

    Response:
    {
        "status": "success",
        "data": [
            {
                "id": 1,
                "name": "Example Product 1",
                "price": 19.99,
                "description": "Lorem ipsum...",
                "stock": 50,
                "location": "/images/example1.jpg"
            },
            ...
        ]
    }
    """

    # Extracting query parameters from the URL
    """
    return success_response("Testing for errors", [
            {
                "id": 1,
                "name": "Example Product 1",
                "price": 19.99,
                "description": "Lorem ipsum...",
                "stock": 50,
                "location": "/images/example1.jpg"
            }])
    """
    filters = request.args.get('filters')
    #print(filters)
    filters = [Filter.from_dict(_filter) for _filter in json.loads(filters)]
    #print(filters)
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    #print(limit, offset)

    res = ProductManager.get_all_products(filters=filters,
                                               limit=limit,
                                               offset=offset)
    print(res)
    return success_response("Retrieved products successfully", res)


@product_api.route('/', methods=['POST'])
@validate_key_
@handle_error_flask
def add_product():
    """
    Endpoint for adding products.

    POST requests are used to add products.
    The Content-Type header must be set to multipart/form-data.
    The form-data must contain a key "product" with the value being a JSON object containing the following parameters:
        name - The name of the product.
        price - The price of the product.
        description - The description of the product.
        stock - The stock of the product.
        image (optional) - An optional URL containing the image of the product
    The request can optionally contain an image in the form-data.
    The key must be "image" and the value must be a file.
    If Neither the image URL nor the image file is specified, the product will be added without an image.

    Request:
    POST /api/products/
    Content-Type: multipart/form-data
    product={"name": "Example Product 1", "price": 19.99, "description": "Lorem ipsum...", "stock": 50}
    image=example.jpg

    Response:
    {
        "status": "success",
        "message": "Inserted product successfully",
        "data": {}
    }
    :return: A JSON object containing the status of the request.

    """
    data = json.loads(request.form.get('product'))
    location = parse_image(data)
    data['location'] = location

    res = ProductManager.add_product(data)
    return success_response("Inserted product successfully", res)


@product_api.route('<int:product_id>/', methods=['GET'])
def get_product(product_id: int):
    """
    Endpoint for getting a specific product
    Get requests are used to get a specific product.

    This endpoint requires the product_id to be specified in the URL and as such does not require a body.
    The Content-Type header should be set to x-www-form-urlencoded.
    :param product_id: The ID of the product to get.

    Request:
    GET /api/products/1/

    Response:
    {
        "status": "success",
        "data": {
            "id": 1,
            "name": "Example Product 1",
            "price": 19.99,
            "description": "Lorem ipsum...",
            "stock": 50,
            "location": "/images/example1.jpg"
        }
    }
    :return:
    """
    res = ProductManager.get_product_by_id(product_id)
    return success_response("Retrieved product successfully", res)


@product_api.route('<int:product_id>/', methods=['PUT'])
@validate_key_
def modify_product(product_id):
    """
    Endpoint for modifying a specific product.
    PUT requests are used to modify a specific product.

    The Content-Type header must be set to multipart/form-data.
    The form-data must contain a key "product" with the value being a JSON object containing the following optional parameters:
        name - The name of the product.
        price - The price of the product.
        description - The description of the product.
        stock - The stock of the product.
        image (optional) - An URL containing the image of the product
    The request can optionally contain an image in the form-data.
    The key must be "image" and the value must be a file.
    :param product_id: The ID of the product to modify.

    Request:
    PUT /api/products/1/
    Content-Type: multipart/form-data
    product={"name": "Example Product 1", "price": 19.99, "description": "Lorem ipsum...", "stock": 50}
    image=example.jpg

    Response:
    {
        "status": "success",
        "message": "Updated product successfully",
        "data": {}
    }
    :return:
    """
    print(request.form)
    print(request.mimetype)
    data = json.loads(request.form.get('product'))
    location = parse_image(data)
    data['location'] = location

    res = ProductManager.update_product(product_id, data)
    return success_response("Updated product successfully", res)


@product_api.route('<int:product_id>/', methods=['DELETE'])
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
    res = ProductManager.delete_product(product_id)
    return success_response("Deleted product successfully", res)


@product_api.route('<int:product_id>/update-stock/', methods=['POST'])
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

    data = request.get_json()
    res = ProductManager.update_product_stock(product_id, data)
    return success_response("Updated product stock successfully", res)


@product_api.route('buy/<int:product_id>/', methods=['POST'])
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
    if request.scheme != "https":
        return error_response("HTTPS Required", 400)

    data = request.get_json()

    res = ProductManager.buy_product(product_id, data)
    return success_response("Bought product successfully", res)
