import importlib.util
from pathlib import Path

config_path = Path(__file__).parent.parent / 'config'
spec = importlib.util.spec_from_file_location('config', config_path / 'config.py')
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

# check if the required functions are present
required_functions = ['get_database_config', 'get_flask_config', 'get_log_config']
for func in required_functions:
    if not hasattr(config, func):
        raise ImportError(f"Required function {func} not found in config.py")

