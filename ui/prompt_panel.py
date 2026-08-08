import tkinter as tk


class PromptPanel:
    def __init__(self, parent):
        self.frame = tk.LabelFrame(
            parent,
            text="💬 Prompt",
            padx=10,
            pady=10
        )

        # Quick Actions
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(fill="x", pady=(0, 10))

        actions = [
            ("Explain", "Explain this."),
            ("Summarize", "Summarize this."),
            ("Rewrite", "Rewrite this professionally."),
            ("Translate", "Translate this."),
            ("Custom", "")
        ]

        for text, prompt in actions:
            btn = tk.Button(
                self.button_frame,
                text=text,
                command=lambda p=prompt: self.set_prompt(p)
            )
            btn.pack(side="left", padx=3)

        # Prompt Textbox
        self.prompt_text = tk.Text(
            self.frame,
            height=4,
            wrap="word",
            font=("Segoe UI", 10)
        )

        self.prompt_text.pack(fill="x", pady=(0, 10))

        # Ask Button
        self.ask_button = tk.Button(
            self.frame,
            text="📤 Ask AI",
            height=2
        )

        self.ask_button.pack(fill="x")

    def set_prompt(self, prompt):
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert(tk.END, prompt)

    def get_prompt(self):
        return self.prompt_text.get("1.0", tk.END).strip()

    def clear_prompt(self):
        self.prompt_text.delete("1.0", tk.END)

    def set_ask_command(self, command):
        self.ask_button.config(command=command)

    def get_frame(self):
        return self.frame