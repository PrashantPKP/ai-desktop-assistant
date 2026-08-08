import json
import os
from pathlib import Path


class SettingsManager:
    """
    Loads and provides access to application settings
    from data/settings.json.
    """

    _instance = None
    _settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _get_project_root(self):
        """Get the project root directory."""
        return Path(__file__).parent.parent

    def _load(self):
        file_path = self._get_project_root() / "data" / "settings.json"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self._settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._settings = {}

    def get(self, key, default=None):
        """
        Get a setting value by dot-notation key.
        Example: settings.get("window.width", 900)
        """
        keys = key.split(".")
        value = self._settings

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_all(self):
        return self._settings
