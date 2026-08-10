import ctypes
import base64
import customtkinter as ctk

from ui.chat_area import ChatArea
from ui.chat_input import ChatInput
from ui.sidebar import Sidebar

from core.model_manager import ModelManager
from core.assistant_controller import AssistantController
from core.settings_manager import SettingsManager
from core.chat_history import ChatHistory


class MainWindow:
    """
    Chat-style main window — similar to ChatGPT / Gemini.
    Header with model selector, scrollable chat area,
    and input bar at the bottom.
    """

    def __init__(self):
        self.settings = SettingsManager()

        self._current_theme = self.settings.get("theme", "light")
        ctk.set_appearance_mode(self._current_theme)
        ctk.set_default_color_theme("blue")

        # --- Root window ---
        self.root = ctk.CTk()
        self.root.title("AI Desktop Assistant")

        w = self.settings.get("window.width", 900)
        h = self.settings.get("window.height", 700)
        self.root.geometry(f"{w}x{h}")
        self.root.minsize(
            self.settings.get("window.min_width", 700),
            self.settings.get("window.min_height", 500)
        )
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        # --- Backend ---
        self.model_manager = ModelManager()
        self.controller = AssistantController()
        self.chat_history = ChatHistory()
        self._is_generating = False

        self._build_ui()

    # ========================
    # UI Build
    # ========================

    def _build_ui(self):
        # --- Header Bar ---
        header = ctk.CTkFrame(
            self.root, height=50,
            corner_radius=0,
            fg_color=("#e8eef4", "#1a1a2e")
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        # Sidebar toggle
        ctk.CTkButton(
            header, text="☰", width=36, height=36,
            corner_radius=8, font=ctk.CTkFont(size=18),
            fg_color="transparent",
            hover_color=("#d0d9e4", "#2a2a40"),
            text_color=("#475569", "#94a3b8"),
            command=self._toggle_sidebar
        ).pack(side="left", padx=(8, 4))

        ctk.CTkLabel(
            header, text="🤖",
            font=ctk.CTkFont(size=22)
        ).pack(side="left", padx=(4, 6))

        ctk.CTkLabel(
            header, text="AI Desktop Assistant",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1e293b", "#e2e8f0"),
            anchor="w"
        ).pack(side="left")

        # Theme toggle button
        self.theme_btn = ctk.CTkButton(
            header, text="🌙" if self._current_theme == "light" else "☀️",
            width=36, height=36, corner_radius=18,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=("#d0d9e4", "#2a2a40"),
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", padx=(10, 0))

        # Status dot + label (right side)
        self.status_dot = ctk.CTkLabel(
            header, text="", width=10, height=10,
            corner_radius=5, fg_color="gray40"
        )
        self.status_dot.pack(side="right", padx=(0, 12))

        self.status_label = ctk.CTkLabel(
            header, text="...",
            font=ctk.CTkFont(size=11),
            text_color=("#64748b", "#94a3b8")
        )
        self.status_label.pack(side="right", padx=(0, 4))

        # Start Ollama button (hidden initially, shown when offline)
        self.start_ollama_btn = ctk.CTkButton(
            header, text="▶ Start Ollama",
            width=120, height=28, corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#2563eb", "#2563eb"),
            hover_color=("#1d4ed8", "#1d4ed8"),
            text_color="#ffffff",
            command=self._start_ollama
        )
        # Not packed yet — shown only when offline

        # Model dropdown — with provider badges
        models = self.model_manager.get_all_models()

        # Build display names with provider badges
        self._model_display_map = {}
        display_names = []
        badges = {"ollama": "💻", "openai": "☁️", "gemini": "✦"}
        for m in (models or []):
            provider = m.get("provider", "ollama")
            badge = badges.get(provider, "💻")
            display = f"{badge} {m['name']}"
            display_names.append(display)
            self._model_display_map[display] = m["name"]

        if not display_names:
            display_names = ["No models"]

        self.model_var = ctk.StringVar(value=display_names[0])

        ctk.CTkOptionMenu(
            header,
            variable=self.model_var,
            values=display_names,
            width=210, height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=11),
            text_color=("#1e293b", "#e2e8f0"),
            fg_color=("#ffffff", "#2a2a40"),
            button_color=("#cbd5e1", "#35354d"),
            button_hover_color=("#94a3b8", "#40405a"),
            dropdown_fg_color=("#ffffff", "#1e1e2e"),
            dropdown_text_color=("#1e293b", "#e2e8f0"),
            dropdown_hover_color=("#e2e8f0", "#2a2a40")
        ).pack(side="right", padx=(0, 16))

        ctk.CTkLabel(
            header, text="Model:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#475569", "#94a3b8")
        ).pack(side="right", padx=(0, 6))

        # --- Body (sidebar + main content) ---
        body = ctk.CTkFrame(self.root, fg_color="transparent")
        body.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = Sidebar(
            body, self.chat_history,
            on_chat_select=self._load_chat,
            on_new_chat=self._new_chat
        )
        self.sidebar.get_frame().pack(side="left", fill="y")

        # Main content frame
        main = ctk.CTkFrame(body, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True)

        # Chat Area
        self.chat_area = ChatArea(main)
        self.chat_area.get_frame().pack(
            fill="both", expand=True, padx=8, pady=0
        )

        # Chat Input
        self.chat_input = ChatInput(main)
        self.chat_input.get_frame().pack(
            fill="x", padx=12, pady=(0, 6)
        )
        self.chat_input.set_send_command(self.ask_ai)

        # --- Status Bar ---
        self.status_bar = ctk.CTkLabel(
            self.root,
            text="Ready  •  Ctrl+Shift+A to capture text",
            font=ctk.CTkFont(size=10),
            text_color="gray45", anchor="w", height=22
        )
        self.status_bar.pack(fill="x", padx=16, pady=(0, 4))

        # Check Ollama
        self.root.after(500, self._check_ollama)

    # ========================
    # Ollama Status
    # ========================

    def _check_ollama(self):
        from core.task_runner import TaskRunner

        def check():
            return self.controller.check_ollama()

        def on_result(ok):
            self.root.after(0, lambda: self._set_ollama_status(ok))

        TaskRunner.run(task=check, on_success=on_result)

    def _set_ollama_status(self, connected):
        if connected:
            self.status_dot.configure(fg_color="#22c55e")
            self.status_label.configure(
                text="Connected", text_color="#22c55e"
            )
            # Hide start button
            self.start_ollama_btn.pack_forget()
        else:
            self.status_dot.configure(fg_color="#ef4444")
            self.status_label.configure(
                text="Offline", text_color="#ef4444"
            )
            # Show start button
            self.start_ollama_btn.pack(side="right", padx=(0, 8))

    def _start_ollama(self):
        """Launch Ollama service in background and recheck connection."""
        self.start_ollama_btn.configure(
            text="⏳ Starting...", state="disabled",
            fg_color=("#94a3b8", "#475569")
        )
        self._set_status("Starting Ollama...")

        from core.task_runner import TaskRunner

        def start_task():
            return self.controller.start_ollama()

        def on_done(result):
            success, message = result
            self.root.after(0, lambda: self._on_ollama_started(success, message))

        TaskRunner.run(task=start_task, on_success=on_done)

    def _on_ollama_started(self, success, message):
        if success:
            self._set_ollama_status(True)
            self._set_status(f"✅ {message}")
        else:
            # Reset button to try again
            self.start_ollama_btn.configure(
                text="▶ Start Ollama", state="normal",
                fg_color=("#2563eb", "#2563eb")
            )
            self._set_status(f"⚠️ {message}")

        # Re-check after a delay
        self.root.after(5000, self._check_ollama)

    # ========================
    # Window Management
    # ========================

    def run(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()

    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        self.root.deiconify()
        self.root.iconify()
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()

        try:
            hwnd = ctypes.windll.user32.FindWindowW(
                None, "AI Desktop Assistant"
            )
            if hwnd:
                ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

        self.root.after(
            200,
            lambda: self.root.attributes("-topmost", False)
        )

    # ========================
    # Shortcut Handler
    # ========================

    def shortcut_pressed(self):
        import time
        time.sleep(0.05)
        captured = self.controller.get_selected_text()
        self.root.after(
            0, lambda: self.open_assistant(captured)
        )

    def open_assistant(self, captured_text=""):
        self._new_chat()
        self.show_window()
        if captured_text:
            self.chat_input.set_context(captured_text)

    # ========================
    # Chat History
    # ========================

    def _new_chat(self):
        """Start a fresh chat session."""
        chat_id = self.chat_history.new_chat()
        self.chat_area.clear()
        self.chat_input.clear_prompt()
        self.chat_input.clear_context()
        self.chat_input.clear_attachment()
        self._set_status("Ready  •  Ctrl+Shift+A to capture text")
        self.sidebar.refresh()

    def _load_chat(self, chat_id):
        """Load a previous chat from history."""
        chat = self.chat_history.load_chat(chat_id)
        if not chat:
            return

        self.chat_history.current_id = chat_id
        self.chat_area.clear()
        self.chat_input.clear_prompt()
        self.chat_input.clear_context()
        self.chat_input.clear_attachment()

        # Replay messages into chat area
        for msg in chat.get("messages", []):
            if msg["role"] == "user":
                self.chat_area.add_user_message(
                    msg["content"],
                    msg.get("context")
                )
            elif msg["role"] == "ai":
                self.chat_area.start_ai_message()
                # Render the saved response directly
                self.chat_area._current_ai_text = msg["content"]
                self.chat_area.finish_ai_message()

        self._set_status(f"Loaded: {chat['title']}")

    def _toggle_sidebar(self):
        self.sidebar.toggle()

    # ========================
    # AI Interaction
    # ========================

    def ask_ai(self):
        if self._is_generating:
            return

        prompt = self.chat_input.get_prompt()
        if not prompt:
            return

        display_name = self.model_var.get()
        model = self._model_display_map.get(display_name, display_name)
        context = self.chat_input.get_context()
        attachment = self.chat_input.get_attachment()

        # Ensure we have a chat session
        if not self.chat_history.current_id:
            self.chat_history.new_chat()

        # Add user message to chat area
        self.chat_area.add_user_message(prompt, context)

        # Save user message to history
        self.chat_history.add_message(
            self.chat_history.current_id, "user", prompt,
            context=context, model=model
        )
        self.sidebar.refresh()

        # Clear input
        self.chat_input.clear_prompt()
        self.chat_input.clear_attachment()

        # Prepare images for vision models
        images = None
        if attachment:
            from pathlib import Path
            suffix = Path(attachment).suffix.lower()
            if suffix in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
                try:
                    with open(attachment, "rb") as f:
                        images = [base64.b64encode(f.read()).decode("utf-8")]
                except Exception:
                    pass

        # Start AI response
        self._is_generating = True
        self.chat_area.start_ai_message()
        self._set_status(f"Generating with {model}...")

        # Stream
        kwargs = {
            "model": model,
            "selected_text": context,
            "user_prompt": prompt,
            "on_token": self._on_token,
            "on_done": self._on_done,
            "on_error": self._on_error,
        }
        if images:
            kwargs["images"] = images

        self.controller.ask_ai_stream(**kwargs)

    def _on_token(self, token):
        self.root.after(
            0,
            lambda t=token: self.chat_area.append_ai_token(t)
        )

    def _on_done(self, full_response):
        self.root.after(
            0, lambda r=full_response: self._finish_generation(r)
        )

    def _on_error(self, msg):
        self.root.after(
            0, lambda: self._handle_error(msg)
        )

    def _finish_generation(self, full_response=""):
        self._is_generating = False
        self.chat_area.finish_ai_message()
        self._set_status("Ready  •  Ctrl+Shift+A to capture text")

        # Save AI response to history
        if self.chat_history.current_id and full_response:
            self.chat_history.add_message(
                self.chat_history.current_id, "ai", full_response
            )
            self.sidebar.refresh()

    def _handle_error(self, msg):
        self._is_generating = False
        self.chat_area.finish_ai_message()
        self.chat_area.show_ai_error(msg)
        self._set_status("Error occurred")

    # ========================
    # Status
    # ========================

    def _set_status(self, text):
        self.status_bar.configure(text=text)

    # ========================
    # Theme Toggle
    # ========================

    def toggle_theme(self):
        if self._current_theme == "light":
            self._current_theme = "dark"
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀️")
        else:
            self._current_theme = "light"
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙")