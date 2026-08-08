import json
import os


class ModelManager:
    def __init__(self):
        self.models = self.load_models()

    def load_models(self):
        file_path = os.path.join("data", "models.json")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
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