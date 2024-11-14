from ..utils.singleton import Singleton

class Config(metaclass=Singleton):
    def __init__(self):
        self.configs = {}
    
    def _get(self, *args, **kwargs):
        return self._configs.get(*args, **kwargs)

    def get_key(self, key, *args, **kwargs):
        value = self._get(key, *args, **kwargs)
        if value is None:
            raise ValueError(f"Key '{key}' not found in the YAML file")
        return value

CONFIG = Config()