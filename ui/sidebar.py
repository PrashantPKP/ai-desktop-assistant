import customtkinter as ctk


class Sidebar:
    """
    Collapsible sidebar with chat history.
    Shows list of past chats with rename/delete options.
    """

    def __init__(self, parent, chat_history, on_chat_select, on_new_chat):
        self.parent = parent
        self.history = chat_history
        self.on_chat_select = on_chat_select
        self.on_new_chat = on_new_chat
        self._visible = True
        self._chat_widgets = []

        # Sidebar frame
        self.frame = ctk.CTkFrame(
            parent, width=260,
            corner_radius=0,
            fg_color=("#e2e8f0", "#141425")
        )
        self.frame.pack_propagate(False)

        # Header
        hdr = ctk.CTkFrame(self.frame, fg_color="transparent", height=44)
        hdr.pack(fill="x", padx=8, pady=(10, 4))
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr, text="💬 Chats",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1e293b", "#e2e8f0"), anchor="w"
        ).pack(side="left", padx=4)

        # New Chat button
        ctk.CTkButton(
            hdr, text="＋ New", width=70, height=30,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#2563eb", "#2563eb"),
            hover_color=("#1d4ed8", "#1d4ed8"),
            text_color="#ffffff",
            command=self._on_new
        ).pack(side="right")

        # Scrollable chat list
        self.chat_list = ctk.CTkScrollableFrame(
            self.frame, fg_color="transparent",
            scrollbar_button_color=("gray78", "gray30"),
            scrollbar_button_hover_color=("gray68", "gray40")
        )
        self.chat_list.pack(fill="both", expand=True, padx=4, pady=(4, 8))

        self.refresh()

    def refresh(self):
        """Reload the chat list from history."""
        for w in self._chat_widgets:
            if w.winfo_exists():
                w.destroy()
        self._chat_widgets.clear()

        chats = self.history.get_all_chats()

        if not chats:
            empty = ctk.CTkLabel(
                self.chat_list, text="No chats yet.\nStart a conversation!",
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray50"),
                justify="center"
            )
            empty.pack(pady=40)
            self._chat_widgets.append(empty)
            return

        for chat in chats:
            self._add_chat_row(chat)

    def _add_chat_row(self, chat):
        """Add a single chat entry to the list."""
        row = ctk.CTkFrame(
            self.chat_list,
            fg_color=("gray88", "#1e1e30"),
            corner_radius=8, height=52
        )
        row.pack(fill="x", pady=2, padx=2)
        row.pack_propagate(False)

        # Title (clickable)
        title_btn = ctk.CTkButton(
            row, text=chat["title"],
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=("#d0d9e4", "#2a2a40"),
            text_color=("#1e293b", "#e2e8f0"),
            anchor="w", height=36,
            command=lambda cid=chat["id"]: self._select(cid)
        )
        title_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Action buttons (rename + delete)
        btn_frame = ctk.CTkFrame(row, fg_color="transparent", width=56)
        btn_frame.pack(side="right", padx=2)
        btn_frame.pack_propagate(False)

        ctk.CTkButton(
            btn_frame, text="✏️", width=24, height=24,
            corner_radius=4, fg_color="transparent",
            hover_color=("#cbd5e1", "#2a2a3e"),
            font=ctk.CTkFont(size=11),
            command=lambda cid=chat["id"], btn=title_btn: self._rename(cid, btn)
        ).pack(side="left", padx=1)

        ctk.CTkButton(
            btn_frame, text="🗑", width=24, height=24,
            corner_radius=4, fg_color="transparent",
            hover_color=("#fecaca", "#3b1111"),
            font=ctk.CTkFont(size=11),
            command=lambda cid=chat["id"]: self._delete(cid)
        ).pack(side="left", padx=1)

        self._chat_widgets.append(row)

    def _select(self, chat_id):
        if self.on_chat_select:
            self.on_chat_select(chat_id)

    def _on_new(self):
        if self.on_new_chat:
            self.on_new_chat()

    def _rename(self, chat_id, title_btn):
        """Show inline rename dialog."""
        dialog = ctk.CTkInputDialog(
            text="Enter new title:",
            title="Rename Chat"
        )
        new_title = dialog.get_input()
        if new_title and new_title.strip():
            self.history.rename_chat(chat_id, new_title.strip())
            title_btn.configure(text=new_title.strip())

    def _delete(self, chat_id):
        self.history.delete_chat(chat_id)
        self.refresh()

    def toggle(self):
        """Show/hide the sidebar."""
        if self._visible:
            self.frame.pack_forget()
            self._visible = False
        else:
            self.frame.pack(side="left", fill="y", before=self._get_main())
            self._visible = True

    def show(self):
        if not self._visible:
            self.frame.pack(side="left", fill="y", before=self._get_main())
            self._visible = True

    def _get_main(self):
        """Find the main content frame (first non-sidebar child)."""
        for child in self.parent.winfo_children():
            if child != self.frame:
                return child
        return None

    def get_frame(self):
        return self.frame
