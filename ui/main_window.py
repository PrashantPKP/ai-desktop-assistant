import tkinter as tk

from ui.model_selector import ModelSelector
from ui.selected_text import SelectedTextPanel
from ui.prompt_panel import PromptPanel
from ui.response_panel import ResponsePanel

from core.model_manager import ModelManager
from core.assistant_controller import AssistantController


class MainWindow:

    def __init__(self):
        self.root = tk.Tk()

        self.root.title("🤖 AI Desktop Assistant")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.hide_window
        )

        self.model_manager = ModelManager()
        self.controller = AssistantController()

        self.main_frame = tk.Frame(
            self.root,
            padx=15,
            pady=15
        )
        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # Model Selector
        self.model_selector = ModelSelector(
            self.main_frame,
            self.model_manager.get_all_models()
        )

        self.model_selector.get_frame().pack(
            fill="x",
            pady=(0, 10)
        )

        # Selected Text
        self.selected_text = SelectedTextPanel(
            self.main_frame
        )

        # Prompt
        self.prompt_panel = PromptPanel(
            self.main_frame
        )

        self.prompt_panel.get_frame().pack(
            fill="x",
            pady=(0, 10)
        )

        self.prompt_panel.set_ask_command(
            self.ask_ai
        )

        # Response
        self.response_panel = ResponsePanel(
            self.main_frame
        )

        self.response_panel.get_frame().pack(
            fill="both",
            expand=True
        )

    # -----------------------
    # Window
    # -----------------------

    def run(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()

    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()

        self.root.after(
            100,
            lambda: self.root.attributes("-topmost", False)
        )

    # -----------------------
    # Shortcut
    # -----------------------

    def shortcut_pressed(self):
        self.root.after(
            0,
            self.open_assistant
        )

    def open_assistant(self):
        self.show_window()

        selected = self.controller.get_selected_text()

        if selected:
            self.selected_text.set_text(selected)
            self.selected_text.show()
        else:
            self.selected_text.clear()

    # -----------------------
    # AI
    # -----------------------

    def ask_ai(self):

        model = self.model_selector.get_selected_model()

        prompt = self.prompt_panel.get_prompt().strip()

        if not prompt:
            self.response_panel.set_response(
                "Please enter a prompt."
            )
            return

        selected = ""

        if self.selected_text.visible:
            selected = self.selected_text.text.get(
                "1.0",
                tk.END
            ).strip()

        self.response_panel.set_response(
            "🤖 Thinking..."
        )

        self.controller.ask_ai(
            model=model,
            selected_text=selected,
            user_prompt=prompt,
            on_success=self.on_ai_success,
            on_error=self.on_ai_error
        )

    def on_ai_success(self, result):
        self.root.after(
            0,
            lambda: self.response_panel.set_response(
                result["response"]
            )
        )

    def on_ai_error(self, error):
        self.root.after(
            0,
            lambda: self.response_panel.set_response(
                f"❌ {error}"
            )
        )