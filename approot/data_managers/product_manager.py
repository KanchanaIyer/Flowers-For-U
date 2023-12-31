import mariadb
import logging

from approot.database.database_manager import database_transaction_helper
from approot.data_managers.errors import NotFoundError, InvalidActionError
from approot.database.models import Product, Filter
from approot.utils.utils import create_filter_query


class ProductManager:
    """
    This class contains static methods for managing products. CRUD (just learned it)
    This moves the logic out of the API endpoints and into a separate class. The api module is now so much smaller.
    """

    @staticmethod
    @database_transaction_helper
    def get_all_products(filters: list[Filter] = None, limit: int = 10, offset: int = 0, cursor=None, database=None) -> list[Product]:
        """
        Gets all products from the database based on the provided filters, limit and offset
        :param list[Filter] filters:
        :param int limit: Maximum number of results to return
        :param int offset: Offset to start the query at
        :param cursor:
        :param database:
        :return: List of Product objects
        :raises NotFoundError: If no products are found which match the provided filters or limit/offset
        :raises InvalidActionError: If the provided filters are invalid
        :raises mariadb.Error: If there is an error with the database
        """
        try:
            n_offset = limit * offset  # Calculate the offset based on the limit and offset provided

            query = "SELECT * FROM products WHERE 1=1 {} LIMIT {} OFFSET {}".format(
                create_filter_query(filters) if filters else '', limit, n_offset)
            cursor.execute(query)
            data = cursor.fetchall()

            if not data or all(all(not x for x in obj.values()) for obj in data):
                raise NotFoundError("No products found which match the provided filters or limit/offset")

            return [Product.from_dict(product) for product in data]

        except InvalidActionError as e:
            raise e
        except NotFoundError as e:
            raise e

    @staticmethod
    @database_transaction_helper
    def add_product(product_data: dict, cursor=None, database=None) -> dict:
        """
        Adds a product to the database
        :param dict product_data: dict containing the product data
        :param cursor:
        :param database:
        :return: Empty dict
        :raises KeyError: If the provided product_data is missing any required fields
        :raises mariadb.Error: If there is an error with the database
        """
        try:
            logging.debug(product_data)
            cursor.execute("INSERT INTO products (NAME, PRICE, DESCRIPTION, STOCK, LOCATION) VALUES (?, ?, ?, ?, ?)",
                           (product_data['name'], product_data['price'], product_data['description'],
                            product_data['stock'], product_data['location']))
            database.commit()
            return dict()

        except KeyError as e:
            raise e

    @staticmethod
    @database_transaction_helper
    def get_product_by_id(product_id: int, cursor=None, database=None) -> Product:
        """
        Gets a product from the database by its ID
        :param int product_id: ID of the product to get
        :param cursor:
        :param database:
        :return: Product object
        :raises NotFoundError: If no product is found with the provided ID
        :raises mariadb.Error: If there is an error with the database
        """
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            data = cursor.fetchone()

            if data is None:
                raise NotFoundError("No product found with the provided ID. Cannot show")

            return Product.from_dict(data)

        except NotFoundError as e:
            raise e

    @staticmethod
    @database_transaction_helper
    def update_product(product_id: int, product_data: dict, cursor=None, database=None) -> dict:
        """
        Updates a product in the database
        :param int product_id: ID of the product to update
        :param dict product_data: Data to update the product with
        :param cursor:
        :param database:
        :return: Empty dict
        :raises NotFoundError: If no product is found with the provided ID
        :raises mariadb.Error: If there is an error with the database
        """
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ? FOR UPDATE", (product_id,))

            if cursor.fetchone() is None:
                raise NotFoundError("No product found with the provided ID. Cannot update")

            cursor.execute("UPDATE products SET NAME = COALESCE(?, NAME), PRICE = COALESCE(?, PRICE),"
                           " DESCRIPTION = COALESCE(?, DESCRIPTION), STOCK = COALESCE(?, STOCK), LOCATION = COALESCE(?, LOCATION)"
                           " WHERE product_id = ?",
                           (product_data.get('name'), product_data.get('price'), product_data.get('description'),
                            product_data.get('stock'), product_data.get('location'), product_id))
            database.commit()
            return dict()

        except NotFoundError as e:
            raise e

    @staticmethod
    @database_transaction_helper
    def delete_product(product_id: int, cursor=None, database=None) -> dict:
        """
        Deletes a product from the database
        :param int product_id: ID of the product to delete
        :param cursor:
        :param database:
        :return: Empty dict
        :raises NotFoundError: If no product is found with the provided ID
        :raises mariadb.Error: If there is an error with the database
        """
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ? FOR UPDATE", (product_id,))

            if cursor.fetchone() is None:
                raise NotFoundError("No product found with the provided ID. Cannot delete")

            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))

            database.commit()
            return dict()

        except NotFoundError as e:
            raise e

    @staticmethod
    @database_transaction_helper
    def update_product_stock(product_id: int, data: dict, cursor=None, database=None) -> dict:
        """
        Updates the stock of a product in the database
        :param product_id: ID of the product to update
        :param data: Dict containing the action to perform and the quantity to perform it with
        :param cursor:
        :param database:
        :return: Empty dict
        :raises NotFoundError: If no product is found with the provided ID
        :raises InvalidActionError: If the provided action is invalid
        :raises mariadb.Error: If there is an error with the database
        """
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            product = cursor.fetchone()

            if not product:
                raise NotFoundError("No product found with the provided ID. Cannot update stock")

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
            return dict()

        except InvalidActionError as e:
            raise e
        except NotFoundError as e:
            raise e

    @staticmethod
    @database_transaction_helper
    def buy_product(product_id: int, data: dict, cursor=None, database=None) -> dict:
        """
        'Buys' a product from the database by updating the stock
        :param product_id: ID of the product to buy
        :param data: Dict containing the quantity to buy
        :param cursor:
        :param database:
        :return: Empty dict
        :raises NotFoundError: If no product is found with the provided ID
        :raises mariadb.Error: If there is an error with the database
        """
        try:
            cursor.execute("SELECT stock FROM products WHERE product_id = ? FOR UPDATE", (product_id,))

            product = cursor.fetchone()
            if product is None:
                raise NotFoundError("No product found with the provided ID. Cannot buy")

            current_stock = product['stock']

            quantity = data.get('quantity', 1)
            if current_stock < quantity:
                raise mariadb.Error("Not enough stock available")

            cursor.execute("UPDATE products SET stock = stock - ? WHERE product_id = ?", (quantity, product_id))
            database.commit()

            return dict()
        except NotFoundError as e:
            raise e
