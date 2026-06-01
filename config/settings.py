import yaml
from pathlib import Path


class Settings:
    def __init__(self, env: str = "dev"):
        self.env = self._normalize_env(env)
        self.config = self._load_config()

    def _normalize_env(self, env: str) -> str:
        return env.strip().lower().replace("-", "_")

    def _load_config(self):
        config_path = Path("config/environments.yaml")
        with open(config_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if self.env not in data:
            raise ValueError(f"Environment '{self.env}' not found in environments.yaml")

        return data[self.env]

    @property
    def base_url(self):
        return self.config["base_url"]

    @property
    def browser(self):
        return self.config["browser"]

    @property
    def headless(self):
        return self.config["headless"]
