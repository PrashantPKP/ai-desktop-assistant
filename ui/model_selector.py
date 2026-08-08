import customtkinter as ctk


class ModelSelector:
    """
    Model selection panel with dropdown and model info display.
    """

    def __init__(self, parent, models):
        self.models = models

        # Container
        self.frame = ctk.CTkFrame(parent, corner_radius=12)

        # Header
        header = ctk.CTkLabel(
            self.frame,
            text="🤖  AI Model",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        header.pack(
            fill="x",
            padx=16,
            pady=(12, 8)
        )

        # Content row
        content_row = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        content_row.pack(
            fill="x",
            padx=16,
            pady=(0, 12)
        )

        # Dropdown
        model_names = [m["name"] for m in self.models] if self.models else ["No models"]

        self.model_var = ctk.StringVar(value=model_names[0])

        self.dropdown = ctk.CTkOptionMenu(
            content_row,
            variable=self.model_var,
            values=model_names,
            width=280,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12),
            command=self._on_model_change
        )
        self.dropdown.pack(side="left", padx=(0, 12))

        # Model info badge
        self.info_label = ctk.CTkLabel(
            content_row,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        self.info_label.pack(side="left", fill="x", expand=True)

        self._update_info()

    def _on_model_change(self, value):
        self._update_info()

    def _update_info(self):
        model_name = self.model_var.get()

        for item in self.models:
            if item["name"] == model_name:
                info_text = f"⚡ {item['type']}  •  📦 {item['size']}"
                self.info_label.configure(text=info_text)
                return

        self.info_label.configure(text="")

    def get_selected_model(self):
        return self.model_var.get()

    def get_frame(self):
        return self.frame