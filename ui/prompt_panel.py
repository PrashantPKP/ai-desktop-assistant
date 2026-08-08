import customtkinter as ctk


class PromptPanel:
    """
    Prompt input area with quick-action buttons and Ask AI button.
    Supports Ctrl+Enter keyboard shortcut to send.
    """

    def __init__(self, parent):
        self.ask_command = None

        # Container
        self.frame = ctk.CTkFrame(parent, corner_radius=12)

        # Header
        header = ctk.CTkLabel(
            self.frame,
            text="💬  Prompt",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        header.pack(
            fill="x",
            padx=16,
            pady=(12, 8)
        )

        # Quick Action Buttons
        actions_frame = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        actions_frame.pack(
            fill="x",
            padx=16,
            pady=(0, 8)
        )

        actions = [
            ("✨ Explain", "Explain this in detail."),
            ("📝 Summarize", "Summarize this concisely."),
            ("✍️ Rewrite", "Rewrite this professionally."),
            ("🌐 Translate", "Translate this to English."),
            ("🐛 Debug", "Find and fix bugs in this code."),
            ("💡 Improve", "Suggest improvements for this."),
        ]

        for text, prompt in actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                width=100,
                height=30,
                corner_radius=8,
                font=ctk.CTkFont(size=11),
                fg_color=("gray85", "gray25"),
                hover_color=("gray75", "gray35"),
                text_color=("gray20", "gray90"),
                command=lambda p=prompt: self.set_prompt(p)
            )
            btn.pack(side="left", padx=(0, 6), pady=2)

        # Prompt Textbox
        self.prompt_text = ctk.CTkTextbox(
            self.frame,
            height=80,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.prompt_text.pack(
            fill="x",
            padx=16,
            pady=(0, 10)
        )

        # Bind Ctrl+Enter to send
        self.prompt_text.bind(
            "<Control-Return>",
            self._on_ctrl_enter
        )

        # Bottom row — Ask + Clear buttons
        button_row = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        button_row.pack(
            fill="x",
            padx=16,
            pady=(0, 12)
        )

        self.ask_button = ctk.CTkButton(
            button_row,
            text="📤  Ask AI",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#1a73e8", "#1a73e8"),
            hover_color=("#1558b0", "#1558b0")
        )
        self.ask_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8)
        )

        self.clear_button = ctk.CTkButton(
            button_row,
            text="🗑️  Clear",
            height=40,
            width=100,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            fg_color=("gray80", "gray30"),
            hover_color=("gray70", "gray40"),
            text_color=("gray20", "gray90"),
        )
        self.clear_button.pack(side="right")

        # Hint label
        hint = ctk.CTkLabel(
            self.frame,
            text="Ctrl+Enter to send",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50"),
            anchor="e"
        )
        hint.pack(
            fill="x",
            padx=16,
            pady=(0, 8)
        )

    def _on_ctrl_enter(self, event):
        if self.ask_command:
            self.ask_command()
        return "break"

    def set_prompt(self, prompt):
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("end", prompt)

    def get_prompt(self):
        return self.prompt_text.get("1.0", "end").strip()

    def clear_prompt(self):
        self.prompt_text.delete("1.0", "end")

    def set_ask_command(self, command):
        self.ask_command = command
        self.ask_button.configure(command=command)

    def set_clear_command(self, command):
        self.clear_button.configure(command=command)

    def get_frame(self):
        return self.frame