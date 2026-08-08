import customtkinter as ctk


class ResponsePanel:
    """
    AI response display panel with copy button and
    streaming support.
    """

    def __init__(self, parent):
        # Container
        self.frame = ctk.CTkFrame(parent, corner_radius=12)
        self.visible = False

        # Header row
        header_row = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        header_row.pack(
            fill="x",
            padx=16,
            pady=(12, 6)
        )

        header = ctk.CTkLabel(
            header_row,
            text="🤖  AI Response",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        header.pack(side="left")

        # Copy button
        self.copy_button = ctk.CTkButton(
            header_row,
            text="📋 Copy",
            width=80,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray20", "gray90"),
            command=self.copy_response
        )
        self.copy_button.pack(side="right")

        # Response Textbox with scrollbar
        self.response_text = ctk.CTkTextbox(
            self.frame,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            state="disabled",
            wrap="word"
        )
        self.response_text.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 12)
        )

    def set_response(self, text):
        """Set the full response text (replaces existing)."""
        self.response_text.configure(state="normal")
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", text)
        self.response_text.configure(state="disabled")

    def append_token(self, token):
        """Append a streaming token to the response."""
        self.response_text.configure(state="normal")
        self.response_text.insert("end", token)
        self.response_text.see("end")
        self.response_text.configure(state="disabled")

    def clear(self):
        """Clear all response text."""
        self.response_text.configure(state="normal")
        self.response_text.delete("1.0", "end")
        self.response_text.configure(state="disabled")

    def show(self):
        """Show the response panel."""
        if not self.visible:
            self.frame.pack(
                fill="both",
                expand=True,
                pady=(0, 10)
            )
            self.visible = True

    def hide(self):
        """Hide the response panel."""
        if self.visible:
            self.frame.pack_forget()
            self.visible = False

    def get_text(self):
        """Get the current response text."""
        return self.response_text.get("1.0", "end").strip()

    def copy_response(self):
        """Copy response to clipboard with visual feedback."""
        text = self.get_text()

        if text:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(text)

            # Visual feedback
            original_text = self.copy_button.cget("text")
            self.copy_button.configure(
                text="✅ Copied!",
                fg_color=("#22c55e", "#16a34a")
            )

            self.frame.after(
                1500,
                lambda: self.copy_button.configure(
                    text=original_text,
                    fg_color=("gray85", "gray25")
                )
            )

    def get_frame(self):
        return self.frame