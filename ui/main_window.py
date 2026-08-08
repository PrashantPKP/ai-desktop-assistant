import ctypes
import customtkinter as ctk

from ui.model_selector import ModelSelector
from ui.selected_text import SelectedTextPanel
from ui.prompt_panel import PromptPanel
from ui.response_panel import ResponsePanel

from core.model_manager import ModelManager
from core.assistant_controller import AssistantController
from core.settings_manager import SettingsManager


class MainWindow:
    """
    Main application window.
    Uses customtkinter for a modern dark-themed UI.
    """

    def __init__(self):
        self.settings = SettingsManager()

        # --- App appearance ---
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Root window ---
        self.root = ctk.CTk()

        self.root.title("AI Desktop Assistant")

        width = self.settings.get("window.width", 900)
        height = self.settings.get("window.height", 700)
        min_w = self.settings.get("window.min_width", 700)
        min_h = self.settings.get("window.min_height", 500)

        self.root.geometry(f"{width}x{height}")
        self.root.minsize(min_w, min_h)

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.hide_window
        )

        # --- Backend ---
        self.model_manager = ModelManager()
        self.controller = AssistantController()
        self._is_generating = False

        # --- Layout ---
        self._build_ui()

    def _build_ui(self):
        """Build the complete UI layout."""

        # Scrollable main container
        self.main_frame = ctk.CTkScrollableFrame(
            self.root,
            corner_radius=0,
            fg_color="transparent"
        )
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(8, 0)
        )

        # Title bar
        title_row = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        title_row.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            title_row,
            text="🤖 AI Desktop Assistant",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        title.pack(side="left")

        # Ollama status indicator
        self.status_dot = ctk.CTkLabel(
            title_row,
            text="",
            width=12,
            height=12,
            corner_radius=6,
            fg_color="gray40"
        )
        self.status_dot.pack(side="right", padx=(0, 6))

        self.status_label = ctk.CTkLabel(
            title_row,
            text="Checking...",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
            anchor="e"
        )
        self.status_label.pack(side="right", padx=(0, 4))

        # 1. Model Selector
        self.model_selector = ModelSelector(
            self.main_frame,
            self.model_manager.get_all_models()
        )
        self.model_selector.get_frame().pack(
            fill="x",
            pady=(0, 10)
        )

        # 2. Selected Text (hidden initially)
        self.selected_text = SelectedTextPanel(
            self.main_frame
        )

        # 3. Prompt Panel
        self.prompt_panel = PromptPanel(
            self.main_frame
        )
        self.prompt_panel.get_frame().pack(
            fill="x",
            pady=(0, 10)
        )
        self.prompt_panel.set_ask_command(self.ask_ai)
        self.prompt_panel.set_clear_command(self.clear_all)

        # 4. Response Panel (hidden until Ask AI is clicked)
        self.response_panel = ResponsePanel(
            self.main_frame
        )

        # --- Status Bar ---
        self.status_bar = ctk.CTkLabel(
            self.root,
            text="Ready  •  Ctrl+Shift+A to capture text",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
            anchor="w",
            height=28
        )
        self.status_bar.pack(
            fill="x",
            padx=16,
            pady=(0, 6)
        )

        # Check Ollama connection on startup
        self.root.after(500, self._check_ollama_status)

    # -----------------------
    # Ollama Status
    # -----------------------

    def _check_ollama_status(self):
        """Check Ollama connection status and update indicator."""

        def check():
            return self.controller.check_ollama()

        def on_result(connected):
            self.root.after(0, lambda: self._update_status(connected))

        from core.task_runner import TaskRunner
        TaskRunner.run(task=check, on_success=on_result)

    def _update_status(self, connected):
        if connected:
            self.status_dot.configure(fg_color="#22c55e")
            self.status_label.configure(
                text="Ollama Connected",
                text_color="#22c55e"
            )
        else:
            self.status_dot.configure(fg_color="#ef4444")
            self.status_label.configure(
                text="Ollama Offline",
                text_color="#ef4444"
            )

    # -----------------------
    # Window Management
    # -----------------------

    def run(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()

    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        """
        Bring the window to the front reliably on Windows.
        Uses iconify→deiconify trick + Win32 SetForegroundWindow.
        """

        # Restore from withdrawn/minimized state
        self.root.deiconify()

        # iconify then deiconify forces Windows to bring it to front
        self.root.iconify()
        self.root.deiconify()

        # Set topmost temporarily to guarantee it's on top
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()

        # Use Win32 API for reliable foreground focus
        try:
            hwnd = ctypes.windll.user32.FindWindowW(
                None, "AI Desktop Assistant"
            )
            if hwnd:
                ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

        # Remove topmost after a short delay so it behaves normally
        self.root.after(
            200,
            lambda: self.root.attributes("-topmost", False)
        )

    # -----------------------
    # Shortcut Handler
    # -----------------------

    def shortcut_pressed(self):
        """
        Called from the keyboard hotkey thread.
        IMPORTANT: Capture selected text HERE (before showing
        our window) because the original app still has focus.
        If we show our window first, ctrl+c would go to our
        app instead of the source app.
        """

        import time
        # Small delay to let the hotkey keys fully release
        time.sleep(0.05)

        # Capture text while the source app still has focus
        captured_text = self.controller.get_selected_text()

        # Now schedule the UI update on the main thread
        self.root.after(
            0,
            lambda: self.open_assistant(captured_text)
        )

    def open_assistant(self, captured_text=""):
        """
        Open the assistant window with a fresh state.
        Any previously displayed prompt/response is cleared.
        """

        # Clear old state — fresh workspace every time
        self.prompt_panel.clear_prompt()
        self.response_panel.clear()
        self.response_panel.hide()
        self.selected_text.clear()
        self._set_status("Ready  •  Ctrl+Shift+A to capture text")

        # Show window and bring to front
        self.show_window()

        # Display captured text right below Model Selector
        if captured_text:
            self.selected_text.set_text(captured_text)
            self.selected_text.show(
                after_widget=self.model_selector.get_frame()
            )

    # -----------------------
    # AI Interaction
    # -----------------------

    def ask_ai(self):
        if self._is_generating:
            return

        model = self.model_selector.get_selected_model()
        prompt = self.prompt_panel.get_prompt()

        if not prompt:
            self.response_panel.clear()
            self.response_panel.set_response(
                "⚠️ Please enter a prompt."
            )
            self.response_panel.show()
            return

        # Get selected text if visible
        selected = ""
        if self.selected_text.visible:
            selected = self.selected_text.get_full_text()

        # Prepare UI for streaming — show response panel
        self._is_generating = True
        self.response_panel.clear()
        self.response_panel.show()
        self._set_status("Generating response...")

        # Stream the response
        self.controller.ask_ai_stream(
            model=model,
            selected_text=selected,
            user_prompt=prompt,
            on_token=self._on_token,
            on_done=self._on_done,
            on_error=self._on_error
        )

    def _on_token(self, token):
        """Called for each streamed token."""
        self.root.after(
            0,
            lambda t=token: self.response_panel.append_token(t)
        )

    def _on_done(self, full_response):
        """Called when streaming is complete."""
        self.root.after(0, self._on_generation_complete)

    def _on_error(self, error_msg):
        """Called on streaming error."""
        self.root.after(
            0,
            lambda: self._handle_error(error_msg)
        )

    def _on_generation_complete(self):
        self._is_generating = False
        self._set_status("Response complete  ✅")

        # Reset status after a delay
        self.root.after(
            3000,
            lambda: self._set_status(
                "Ready  •  Ctrl+Shift+A to capture text"
            )
        )

    def _handle_error(self, error_msg):
        self._is_generating = False
        self.response_panel.clear()
        self.response_panel.set_response(f"❌ {error_msg}")
        self.response_panel.show()
        self._set_status("Error occurred")

    # -----------------------
    # Clear
    # -----------------------

    def clear_all(self):
        """Reset the entire workspace."""
        self.selected_text.clear()
        self.prompt_panel.clear_prompt()
        self.response_panel.clear()
        self.response_panel.hide()
        self._set_status("Ready  •  Ctrl+Shift+A to capture text")

    # -----------------------
    # Status Bar
    # -----------------------

    def _set_status(self, text):
        self.status_bar.configure(text=text)