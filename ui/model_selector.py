import tkinter as tk
from tkinter import ttk


class ModelSelector:
    def __init__(self, parent, models):
        self.models = models

        self.frame = tk.LabelFrame(
            parent,
            text="🤖 AI Model",
            padx=10,
            pady=10
        )

        # Dropdown
        self.model_var = tk.StringVar()

        self.dropdown = ttk.Combobox(
            self.frame,
            textvariable=self.model_var,
            state="readonly",
            width=35
        )

        self.dropdown["values"] = [
            model["name"] for model in self.models
        ]

        if self.models:
            self.dropdown.current(0)

        self.dropdown.pack(fill="x")

        # Model Information
        self.info = tk.Label(
            self.frame,
            anchor="w",
            justify="left",
            padx=2,
            pady=8
        )

        self.info.pack(fill="x")

        self.dropdown.bind(
            "<<ComboboxSelected>>",
            self.update_info
        )

        self.update_info()

    def update_info(self, event=None):
        model = self.get_selected_model()

        for item in self.models:
            if item["name"] == model:
                self.info.config(
                    text=(
                        f"Type : {item['type']}\n"
                        f"Size : {item['size']}"
                    )
                )
                break

    def get_selected_model(self):
        return self.model_var.get()

    def get_frame(self):
        return self.frame