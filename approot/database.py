import mariadb
from mariadb import connect
from mariadb import Error
import config
import logging

logging.getLogger(__name__)

connection: mariadb.Connection | None = None


def connect_to_database(debug=False):
    global connection
    database_config = config.get_database_config()
    connection = connect(
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
    connection.auto_reconnect = database_config['reconnect'] == 'ENABLED'
    if connection is None:
        logging.error("Failed to connect to database")
        raise Error("Failed to connect to database")


def get_cursor(debug=False):
    global connection

    if connection is None:
        connect_to_database(debug)
    cursor = connection.cursor(dictionary=True)
    return connection, cursor
