import importlib.util
import sys
import logging
from pathlib import Path

sys.path.insert(0, '/var/www/Flowers4U/')
sys.path.insert(0, '/var/www/Flowers4U/approot/Flowers/lib/python3.11/site-packages')
from dotenv import load_dotenv
load_dotenv('/var/www/Flowers4U/.env')
# Import config.py
import approot.utils.config as config

try:
    log_config = config.get_config().get_log_config()
except AttributeError as e:
    raise Exception(f"Config not found\n{dir(config.get_config())}\n\n\n") from e
log_folder = log_config['folder']


main_log_path = log_folder + 'main.log'
if not Path(main_log_path).is_file():
    Path(main_log_path).touch()
    Path(main_log_path).chmod(0o666)
logging.basicConfig(filename=main_log_path, level=log_config['level'])

main_logger = logging.getLogger('main')
main_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
main_handler = logging.FileHandler(main_log_path)
main_handler.setFormatter(main_formatter)
main_logger.addHandler(main_handler)


error_log_path = log_folder + 'error.log'
if not Path(error_log_path).is_file():
    Path(error_log_path).touch()
    Path(error_log_path).chmod(0o666)

error_logger = logging.getLogger('error')
error_logger.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
error_handler = logging.FileHandler(error_log_path)
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)


from approot.apitest import app as application
application.logger.addHandler(main_handler)
application.logger.addHandler(error_handler)
