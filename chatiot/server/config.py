import yaml

from utils.singleton import Singleton
from pathlib import Path
import os

def get_config_file():
    current_path = Path.cwd()
    if os.path.exists(os.path.join(current_path, "configs", "default_config.yaml")):
        config_path = os.path.join(current_path, "configs", "default_config.yaml")
    else:
        config_path = os.path.join(current_path, "frontend", "configs", "config.yaml")
    return config_path

class Config(metaclass=Singleton):
    """
    常规使用方法：
    config = Config("config.yaml")
    secret_key = config.get_key("MY_SECRET_KEY")
    print("Secret key:", secret_key)
    """

    _instance = None
    config_yaml_file = get_config_file()

    def __init__(self, yaml_file=config_yaml_file):
        self.configs = {}
        self._init_with_config_files(self.configs, yaml_file)

    def _init_with_config_files(self, configs: dict, yaml_file: str):
        with open(yaml_file, "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        configs.update(yaml_data)
    
    def _get(self, *args, **kwargs):
        return self._configs.get(*args, **kwargs)

    def get_key(self, key, *args, **kwargs):
        value = self._get(key, *args, **kwargs)
        if value is None:
            raise ValueError(f"Key '{key}' not found in the YAML file")
        return value
    
CONFIG = Config()