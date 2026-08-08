import tkinter as tk


class SelectedTextPanel:
    def __init__(self, parent):
        self.frame = tk.LabelFrame(
            parent,
            text="📋 Selected Text",
            padx=10,
            pady=10
        )

        self.text = tk.Text(
            self.frame,
            height=7,
            wrap="word",
            state="disabled",
            font=("Segoe UI", 10)
        )

        self.text.pack(fill="both", expand=True)

        # Hidden initially
        self.visible = False

    def set_text(self, content):
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)

        lines = content.splitlines()

        # Show only first 7 lines
        if len(lines) > 7:
            display = "\n".join(lines[:7]) + "\n..."
        else:
            display = content

        self.text.insert("1.0", display)
        self.text.config(state="disabled")

    def show(self):
        if not self.visible:
            self.frame.pack(fill="x", pady=(0, 15))
            self.visible = True

    def hide(self):
        if self.visible:
            self.frame.pack_forget()
            self.visible = False

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.config(state="disabled")
        self.hide()

    def get_frame(self):
        return self.frame