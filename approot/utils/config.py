import logging
import os
from pathlib import Path
import configparser

def _get_config(file: Path):
    """
    Gets the configuration from the provided file
    :param file:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(file)
    return config


def get_config():
    return Config()


class Config:

    def __init__(self):
        self.config = _get_config(Path(os.getenv('FLOWERS_CONFIG_PATH', "/var/www/Flowers4U/config/config.ini")))



    def _init_config(self):
        config_path = Path(os.getenv('FLOWERS_CONFIG_PATH'))
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
        self.config = _get_config(config_path)

    def get_database_config(self):
        """
        Gets the database configuration from the config.ini file
        :return:
        """
        if self is None:
            raise Exception("WE DO NOT HAVE AN INSTANCE OF CONFIG somehow")
        logging.critical(dir(self))
        if not self.config:
            self._init_config()
        return self.config['Database']

    def get_flask_config(self):
        """
        Gets the Flask configuration from the config.ini file
        :return:
        """
        if not self.config:
            self._init_config()
        return self.config['Server']

    def get_log_config(self):
        """
        Gets the logging configuration from the config.ini file
        :return:
        """
        if self is None:
            raise Exception("WE DO NOT HAVE AN INSTANCE OF CONFIG somehow")
        if not self.config:
            self._init_config()
        return self.config['Logging']

    def get_config(self):
        """
        Gets the logging configuration from the config.ini file
        :return:
        """
        if not self.config:
            self._init_config()
        return self.config


if __name__ == '__main__':
    _config = get_config()
    print(_config.get_config().sections())
    print(_config.get_database_config())
    print(_config.get_flask_config())
    print(_config.get_log_config())
