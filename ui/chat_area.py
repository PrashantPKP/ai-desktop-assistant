import customtkinter as ctk
from ui.markdown_renderer import MarkdownRenderer


class ChatArea:
    """
    Scrollable chat area with message bubbles.
    User: right-aligned blue. AI: left-aligned with markdown.
    Shows loading dots until first token arrives.
    """

    def __init__(self, parent):
        self._current_ai_bubble = None
        self._current_ai_label = None
        self._loading_label = None
        self._loading_step = 0
        self._current_ai_text = ""
        self._first_token = True
        self._widgets = []
        self._renderer = MarkdownRenderer()

        self.frame = ctk.CTkScrollableFrame(
            parent, corner_radius=0, fg_color="transparent",
            scrollbar_button_color=("gray80", "gray30"),
            scrollbar_button_hover_color=("gray70", "gray40")
        )

        self._welcome_visible = True
        self._build_welcome()

    def _build_welcome(self):
        self.welcome = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.welcome.pack(fill="both", expand=True, pady=100)

        ctk.CTkLabel(self.welcome, text="🤖",
                     font=ctk.CTkFont(size=48)).pack(pady=(0, 12))
        ctk.CTkLabel(self.welcome, text="AI Desktop Assistant",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=("gray20", "gray80")).pack(pady=(0, 8))
        ctk.CTkLabel(self.welcome,
                     text="Select text anywhere and press Ctrl+Shift+A\nor type a prompt below",
                     font=ctk.CTkFont(size=13),
                     text_color=("gray50", "gray50"),
                     justify="center").pack()

    def _hide_welcome(self):
        if self._welcome_visible:
            self.welcome.pack_forget()
            self._welcome_visible = False

    def _scroll_bottom(self):
        self.frame.update_idletasks()
        try:
            self.frame._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    # --- User Message ---

    def add_user_message(self, prompt, context=None):
        self._hide_welcome()

        row = ctk.CTkFrame(self.frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(14, 4))

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(side="right", anchor="e")

        ctk.CTkLabel(inner, text="You",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=("gray50", "gray50"), anchor="e"
                     ).pack(fill="x", padx=6, pady=(0, 4))

        if context and context.strip():
            self._context_card(inner, context)

        bubble = ctk.CTkFrame(inner, fg_color=("#2563eb", "#2563eb"),
                              corner_radius=14)
        bubble.pack(anchor="e")

        ctk.CTkLabel(bubble, text=prompt,
                     font=ctk.CTkFont(size=13), text_color="#ffffff",
                     wraplength=480, justify="left", anchor="w"
                     ).pack(padx=16, pady=10)

        self._widgets.append(row)
        self.frame.after(50, self._scroll_bottom)

    def _context_card(self, parent, text):
        card = ctk.CTkFrame(parent,
                            fg_color=("#e8eef4", "#2a2a3e"),
                            corner_radius=10)
        card.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(card, text="📋 Context",
                     font=ctk.CTkFont(size=10),
                     text_color=("gray50", "gray50"),
                     anchor="w").pack(fill="x", padx=12, pady=(8, 2))

        lines = text.strip().splitlines()
        preview = "\n".join(lines[:5]) + ("\n..." if len(lines) > 5 else "")

        ctk.CTkLabel(card, text=preview,
                     font=ctk.CTkFont(family="Consolas", size=11),
                     text_color=("#475569", "#94a3b8"),
                     anchor="w", justify="left", wraplength=440
                     ).pack(fill="x", padx=12, pady=(0, 8))

    # --- AI Message ---

    def start_ai_message(self):
        self._hide_welcome()
        self._current_ai_text = ""
        self._first_token = True

        row = ctk.CTkFrame(self.frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(4, 14))

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(side="left", fill="x", expand=True, anchor="w")

        ctk.CTkLabel(inner, text="🤖 AI",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=("gray50", "gray50"), anchor="w"
                     ).pack(fill="x", padx=6, pady=(0, 4))

        self._current_ai_bubble = ctk.CTkFrame(
            inner, fg_color=("#eef2f7", "#1e1e2e"), corner_radius=14
        )
        self._current_ai_bubble.pack(fill="x", padx=(0, 50))

        # Loading animation
        self._loading_label = ctk.CTkLabel(
            self._current_ai_bubble, text="●",
            font=ctk.CTkFont(size=16),
            text_color=("#94a3b8", "#64748b")
        )
        self._loading_label.pack(padx=16, pady=14)
        self._loading_step = 0
        self._animate_loading()

        self._widgets.append(row)
        self.frame.after(50, self._scroll_bottom)

    def _animate_loading(self):
        if self._loading_label and self._loading_label.winfo_exists():
            dots = ["●  ○  ○", "○  ●  ○", "○  ○  ●"]
            self._loading_step = (self._loading_step + 1) % 3
            self._loading_label.configure(text=dots[self._loading_step])
            self.frame.after(350, self._animate_loading)

    def append_ai_token(self, token):
        # On first token: remove loading, create streaming label
        if self._first_token:
            self._first_token = False
            if self._loading_label and self._loading_label.winfo_exists():
                self._loading_label.destroy()
                self._loading_label = None

            self._current_ai_label = ctk.CTkLabel(
                self._current_ai_bubble, text="",
                font=ctk.CTkFont(size=13),
                text_color=("#334155", "#e2e8f0"),
                anchor="nw", justify="left", wraplength=600
            )
            self._current_ai_label.pack(fill="x", padx=14, pady=12)

        self._current_ai_text += token
        if self._current_ai_label and self._current_ai_label.winfo_exists():
            self._current_ai_label.configure(text=self._current_ai_text)
            self.frame.after(30, self._scroll_bottom)

    def finish_ai_message(self):
        """Replace streaming label with rendered markdown."""
        if not self._current_ai_bubble or not self._current_ai_text:
            return

        # Remove streaming label
        if self._current_ai_label and self._current_ai_label.winfo_exists():
            self._current_ai_label.destroy()
        # Remove loading if still showing
        if self._loading_label and self._loading_label.winfo_exists():
            self._loading_label.destroy()
            self._loading_label = None

        # Render markdown
        bubble_bg = "#eef2f7"
        content = ctk.CTkFrame(
            self._current_ai_bubble, fg_color="transparent"
        )
        content.pack(fill="x", padx=10, pady=(8, 4))

        self._renderer.render(content, self._current_ai_text,
                              bubble_bg=bubble_bg)

        # Copy all button
        full_text = self._current_ai_text
        btn_row = ctk.CTkFrame(self._current_ai_bubble, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(2, 8))

        copy_btn = ctk.CTkButton(
            btn_row, text="📋 Copy all", width=85, height=24,
            corner_radius=6, font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=("#dbeafe", "#2a2a3e"),
            text_color=("#64748b", "#94a3b8"),
            border_width=1,
            border_color=("#cbd5e1", "#475569"),
            command=lambda: self._copy_all(full_text, copy_btn)
        )
        copy_btn.pack(side="right")

        self._current_ai_bubble = None
        self._current_ai_label = None
        self.frame.after(100, self._scroll_bottom)

    def show_ai_error(self, msg):
        self.start_ai_message()
        self._first_token = False
        if self._loading_label and self._loading_label.winfo_exists():
            self._loading_label.destroy()
            self._loading_label = None

        err_label = ctk.CTkLabel(
            self._current_ai_bubble, text=f"❌ {msg}",
            font=ctk.CTkFont(size=13),
            text_color="#ef4444", anchor="nw",
            justify="left", wraplength=600
        )
        err_label.pack(fill="x", padx=14, pady=12)
        self._current_ai_bubble = None

    def _copy_all(self, text, btn):
        self.frame.clipboard_clear()
        self.frame.clipboard_append(text)
        btn.configure(text="✅ Copied!", fg_color=("#22c55e", "#16a34a"),
                      text_color="#fff")
        self.frame.after(1500, lambda: btn.configure(
            text="📋 Copy all", fg_color="transparent",
            text_color=("#64748b", "#94a3b8")))

    # --- Clear ---

    def clear(self):
        for w in self._widgets:
            if w.winfo_exists():
                w.destroy()
        self._widgets.clear()
        self._current_ai_bubble = None
        self._current_ai_label = None
        self._loading_label = None
        self._current_ai_text = ""
        if not self._welcome_visible:
            self._build_welcome()
            self._welcome_visible = True

    def get_frame(self):
        return self.frame
