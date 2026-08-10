import customtkinter as ctk


class ChatInput:
    """
    Bottom input area — context card + quick actions + text input + send.
    Looks like ChatGPT's input bar.
    """

    def __init__(self, parent):
        self.send_command = None
        self.clear_command = None
        self._context_text = ""

        # Outer container
        self.frame = ctk.CTkFrame(
            parent, fg_color="transparent"
        )

        # --- Context Card (hidden initially) ---
        self.context_frame = ctk.CTkFrame(
            self.frame,
            fg_color=("gray88", "#252538"),
            corner_radius=10
        )
        self._context_visible = False

        ctx_header = ctk.CTkFrame(
            self.context_frame, fg_color="transparent"
        )
        ctx_header.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            ctx_header, text="📋 Selected Text",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray50", anchor="w"
        ).pack(side="left")

        ctk.CTkButton(
            ctx_header, text="✕",
            width=24, height=24, corner_radius=6,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            text_color="gray50",
            command=self.clear_context
        ).pack(side="right")

        self.context_label = ctk.CTkLabel(
            self.context_frame, text="",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=("gray30", "gray55"),
            anchor="w", justify="left", wraplength=700
        )
        self.context_label.pack(
            fill="x", padx=12, pady=(0, 8)
        )

        # --- Quick Actions ---
        actions_row = ctk.CTkFrame(
            self.frame, fg_color="transparent"
        )
        actions_row.pack(fill="x", padx=4, pady=(4, 6))

        actions = [
            ("✨ Explain", "Explain this in detail."),
            ("📝 Summarize", "Summarize this concisely."),
            ("✍️ Rewrite", "Rewrite this professionally."),
            ("🌐 Translate", "Translate this to English."),
            ("🐛 Debug", "Find and fix bugs in this code."),
            ("💡 Improve", "Suggest improvements for this."),
        ]

        for text, prompt in actions:
            ctk.CTkButton(
                actions_row, text=text,
                width=90, height=28, corner_radius=14,
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                hover_color=("gray80", "gray30"),
                text_color=("gray30", "gray70"),
                border_width=1,
                border_color=("gray75", "gray35"),
                command=lambda p=prompt: self.set_prompt(p)
            ).pack(side="left", padx=3)

        # --- Attachment Preview (hidden initially) ---
        self._attached_file = None
        self.attach_frame = ctk.CTkFrame(
            self.frame, fg_color=("#dbeafe", "#1e2a4a"),
            corner_radius=8
        )
        self._attach_visible = False

        attach_inner = ctk.CTkFrame(self.attach_frame, fg_color="transparent")
        attach_inner.pack(fill="x", padx=10, pady=6)

        self.attach_icon = ctk.CTkLabel(
            attach_inner, text="📎",
            font=ctk.CTkFont(size=14)
        )
        self.attach_icon.pack(side="left", padx=(0, 6))

        self.attach_label = ctk.CTkLabel(
            attach_inner, text="",
            font=ctk.CTkFont(size=11),
            text_color=("#1e40af", "#93c5fd"), anchor="w"
        )
        self.attach_label.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            attach_inner, text="✕", width=22, height=22,
            corner_radius=4, fg_color="transparent",
            hover_color=("#bfdbfe", "#2a3a5e"),
            text_color=("#64748b", "#94a3b8"),
            font=ctk.CTkFont(size=10),
            command=self.clear_attachment
        ).pack(side="right")

        # --- Input Row ---
        input_row = ctk.CTkFrame(
            self.frame,
            fg_color=("gray90", "#1e1e2e"),
            corner_radius=14
        )
        input_row.pack(fill="x", pady=(0, 4))

        # Attach button (left side)
        self.attach_btn = ctk.CTkButton(
            input_row, text="📎",
            width=36, height=36, corner_radius=18,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=("gray82", "gray30"),
            text_color=("#64748b", "#94a3b8"),
            command=self._pick_file
        )
        self.attach_btn.pack(side="left", padx=(6, 0), pady=6)

        self.prompt_text = ctk.CTkTextbox(
            input_row, height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            wrap="word"
        )
        self.prompt_text.pack(
            side="left", fill="both",
            expand=True, padx=(4, 4), pady=6
        )

        self.prompt_text.bind(
            "<Control-Return>", self._on_ctrl_enter
        )

        # Button column
        btn_col = ctk.CTkFrame(
            input_row, fg_color="transparent"
        )
        btn_col.pack(side="right", padx=(0, 8), pady=6)

        self.send_btn = ctk.CTkButton(
            btn_col, text="➤",
            width=42, height=42,
            corner_radius=21,
            font=ctk.CTkFont(size=18),
            fg_color="#2563eb",
            hover_color="#1d4ed8"
        )
        self.send_btn.pack(pady=(0, 2))

    # --- Context ---

    def set_context(self, text):
        self._context_text = text
        lines = text.strip().splitlines()
        preview = "\n".join(lines[:7])
        if len(lines) > 7:
            preview += "\n..."

        self.context_label.configure(text=preview)

        if not self._context_visible:
            self.context_frame.pack(
                fill="x", padx=4, pady=(0, 4),
                before=self.frame.winfo_children()[1]
            )
            self._context_visible = True

    def get_context(self):
        return self._context_text if self._context_visible else ""

    def clear_context(self):
        self._context_text = ""
        if self._context_visible:
            self.context_frame.pack_forget()
            self._context_visible = False

    # --- Prompt ---

    def set_prompt(self, text):
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("end", text)

    def get_prompt(self):
        return self.prompt_text.get("1.0", "end").strip()

    def clear_prompt(self):
        self.prompt_text.delete("1.0", "end")

    # --- Attachment ---

    def _pick_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Attach File",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PDF", "*.pdf"),
                ("Text", "*.txt *.md *.py *.js *.html *.css *.json"),
                ("All Files", "*.*")
            ]
        )
        if path:
            self._attached_file = path
            from pathlib import Path
            name = Path(path).name
            suffix = Path(path).suffix.lower()

            if suffix in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
                icon = "🖼️"
            elif suffix == ".pdf":
                icon = "📄"
            else:
                icon = "📎"

            self.attach_icon.configure(text=icon)
            self.attach_label.configure(text=name)

            if not self._attach_visible:
                self.attach_frame.pack(
                    fill="x", padx=4, pady=(0, 4),
                    before=self.frame.winfo_children()[-2]
                )
                self._attach_visible = True

    def get_attachment(self):
        return self._attached_file if self._attach_visible else None

    def clear_attachment(self):
        self._attached_file = None
        if self._attach_visible:
            self.attach_frame.pack_forget()
            self._attach_visible = False

    # --- Commands ---

    def set_send_command(self, cmd):
        self.send_command = cmd
        self.send_btn.configure(command=cmd)

    def set_clear_command(self, cmd):
        self.clear_command = cmd

    def _on_ctrl_enter(self, event):
        if self.send_command:
            self.send_command()
        return "break"

    def get_frame(self):
        return self.frame
