import tkinter as tk


class ResponsePanel:
    def __init__(self, parent):
        self.frame = tk.LabelFrame(
            parent,
            text="🤖 AI Response",
            padx=10,
            pady=10
        )

        # Top Buttons
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill="x", pady=(0, 8))

        self.copy_button = tk.Button(
            button_frame,
            text="📋 Copy",
            command=self.copy_response
        )
        self.copy_button.pack(side="right")

        # Response Box
        self.response_text = tk.Text(
            self.frame,
            height=12,
            wrap="word",
            state="disabled",
            font=("Segoe UI", 10)
        )

        self.response_text.pack(fill="both", expand=True)

    def set_response(self, text):
        self.response_text.config(state="normal")
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert("1.0", text)
        self.response_text.config(state="disabled")

    def append_response(self, text):
        self.response_text.config(state="normal")
        self.response_text.insert(tk.END, text)
        self.response_text.see(tk.END)
        self.response_text.config(state="disabled")

    def clear(self):
        self.response_text.config(state="normal")
        self.response_text.delete("1.0", tk.END)
        self.response_text.config(state="disabled")

    def copy_response(self):
        text = self.response_text.get("1.0", tk.END).strip()

        if text:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(text)

    def get_frame(self):
        return self.frame