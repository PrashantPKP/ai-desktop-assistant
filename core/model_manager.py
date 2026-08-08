import json
from pathlib import Path


class ModelManager:
    def __init__(self):
        self.models = self._load_models()

    def _load_models(self):
        file_path = Path(__file__).parent.parent / "data" / "models.json"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def get_all_models(self):
        return self.models

    def get_model_names(self):
        return [model["name"] for model in self.models]

    def get_model(self, model_name):
        for model in self.models:
            if model["name"] == model_name:
                return model

        return None

    def get_default_model(self):
        if self.models:
            return self.models[0]["name"]
        return None