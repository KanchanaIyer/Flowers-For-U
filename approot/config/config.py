from pathlib import Path
import configparser


def get_config(file: Path):
    config = configparser.ConfigParser()
    config.read(file)
    return config


def get_database_config():
    config = get_config(Path(__file__).parents[0] / 'config.ini')
    return config['Database']


def get_flask_config():
    config = get_config(Path(__file__).parents[0] / 'config.ini')
    return config['Server']

def get_log_config():
    config = get_config(Path(__file__).parents[0] / 'config.ini')
    return config['Logging']
