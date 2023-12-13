import logging
from contextlib import contextmanager
from functools import wraps

import mariadb

from approot.database.database import get_cursor


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
        raise e
    except Exception as e:
        logging.error(f"Unknown error occurred: {e}")
        yield None, None
        raise e


def database_transaction_helper(func):
    """
    Decorator for handling database transactions. Sets up and tears down the database connection and cursor.
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_database_connection() as (database, cursor):
            if database is None:
                raise mariadb.Error("Failed to connect to database")
            try:
                return func(database=database, cursor=cursor, *args, **kwargs)
            except mariadb.Error as e:
                database.rollback()
                raise e

    return wrapper
