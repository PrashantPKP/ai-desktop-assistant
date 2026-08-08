import customtkinter as ctk


class SelectedTextPanel:
    """
    Displays captured selected text.
    Hidden when no text is selected.
    Shows only first 7 lines with ellipsis for long text.
    """

    MAX_PREVIEW_LINES = 7

    def __init__(self, parent):
        self.parent = parent

        # Container
        self.frame = ctk.CTkFrame(parent, corner_radius=12)

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
            text="📋  Selected Text",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        header.pack(side="left")

        # Close button
        close_btn = ctk.CTkButton(
            header_row,
            text="✕",
            width=28,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            text_color=("gray40", "gray60"),
            command=self.clear
        )
        close_btn.pack(side="right")

        # Text display
        self.text = ctk.CTkTextbox(
            self.frame,
            height=120,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            state="disabled",
            wrap="word"
        )
        self.text.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 12)
        )

        # Hidden initially
        self.visible = False
        self._full_text = ""

    def set_text(self, content):
        self._full_text = content
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")

        lines = content.splitlines()

        if len(lines) > self.MAX_PREVIEW_LINES:
            display = "\n".join(lines[:self.MAX_PREVIEW_LINES]) + "\n..."
        else:
            display = content

        self.text.insert("1.0", display)
        self.text.configure(state="disabled")

    def get_full_text(self):
        """Return the full untruncated text."""
        return self._full_text

    def show(self, after_widget=None):
        if not self.visible:
            pack_opts = {
                "fill": "x",
                "padx": 0,
                "pady": (0, 10)
            }
            if after_widget:
                pack_opts["after"] = after_widget
            self.frame.pack(**pack_opts)
            self.visible = True

    def hide(self):
        if self.visible:
            self.frame.pack_forget()
            self.visible = False

    def clear(self):
        self._full_text = ""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
        self.hide()

    def get_frame(self):
        return self.frame