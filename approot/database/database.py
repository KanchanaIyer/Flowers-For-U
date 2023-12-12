import mariadb
from mariadb import connect
from mariadb import Error
import approot.config.config
import logging

from approot.config import config
from flask import g

logging.getLogger(__name__)

# Global variable for the connection pool
pool: mariadb.ConnectionPool = None  # type: ignore


def init_connection_pool(debug=False):
    global pool
    database_config = config.get_database_config()
    pool = mariadb.ConnectionPool(
        pool_name="FlowerPool",
        pool_size=int(database_config['poolSize']),
        host=database_config['host'],
        user=database_config['user'],
        password=database_config['password'],
        database=database_config['database'],
        port=int(database_config['port']),
        # unix_socket=database_config['socket'] if database_config['socket'] else None,
        connect_timeout=int(database_config['connectionTimeout']),
        read_timeout=int(database_config['readTimeout']),
        write_timeout=int(database_config['writeTimeout']),
        ssl_key=database_config['sslKey'],
        ssl_cert=database_config['sslCert'],
        ssl_ca=database_config['sslCa'],
        ssl_verify_cert=debug,
        # ssl=database_config['ssl'] == 'ENABLED',
    )
    pool.auto_reconnect = database_config['reconnect'] == 'ENABLED'


def get_db_connection(debug=False):
    if not pool:
        init_connection_pool(debug)

    if not g.get('db_connection'):
        g.db_connection = pool.get_connection()
    return g.db_connection


def get_cursor(debug=False):
    connection = get_db_connection(debug)
    cursor = connection.cursor(dictionary=True)
    return connection, cursor


def close_connection(error=None):
    logging.debug("Closing database connection")
    logging.error(error)
    db = g.pop('db_connection', None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_connection)
