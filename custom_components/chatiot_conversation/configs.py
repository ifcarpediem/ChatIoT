from utils.singleton import Singleton

class Configs(metaclass=Singleton):
    def __init__(self):
        self.hass_data = {}
        self.configs_llm = {}
    
    def _get(self, *args, **kwargs):
        return self._configs.get(*args, **kwargs)

    def get_key(self, key, *args, **kwargs):
        value = self._get(key, *args, **kwargs)
        if value is None:
            raise ValueError(f"Key '{key}' not found in the YAML file")
        return value

CONFIG = Configs()