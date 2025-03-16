import yaml
import os

class Config:
    def __init__(self, config_filename="config.yml"):
        config_dir = os.path.dirname(__file__)
        self.config_path = os.path.join(config_dir, config_filename)
        self.data = self._load_config()

    def _load_config(self):
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл конфігурації не знайдено: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Невалідний файл конфігурації: {e}")

    def get(self, section, key, default=None):
        try:
            return self.data[section][key]
        except KeyError:
            if default is not None:
                return default
            else:
                raise KeyError(f"Ключ '{key}' не знайдено в секції '{section}'")