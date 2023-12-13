from pathlib import Path
import configparser


def get_config(file: Path):
    """
    Gets the configuration from the provided file
    :param file:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(file)
    return config


def get_database_config():
    """
    Gets the database configuration from the config.ini file
    :return:
    """
    config = get_config(Path(__file__).parents[0] / 'config.ini')
    return config['Database']


def get_flask_config():
    """
    Gets the Flask configuration from the config.ini file
    :return:
    """
    config = get_config(Path(__file__).parents[0] / 'config.ini')
    return config['Server']


def get_log_config():
    """
    Gets the logging configuration from the config.ini file
    :return:
    """
    config = get_config(Path(__file__).parents[0] / 'config.ini')
    return config['Logging']
