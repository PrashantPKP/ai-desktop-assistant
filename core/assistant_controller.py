from core.clipboard import ClipboardManager
from core.prompt_engine import PromptEngine
from core.ollama_client import OllamaClient
from core.task_runner import TaskRunner


class AssistantController:
    def __init__(self):
        self.clipboard = ClipboardManager()
        self.prompt_engine = PromptEngine()
        self.ollama = OllamaClient()

    def get_selected_text(self):
        return self.clipboard.get_selected_text()

    def ask_ai(
        self,
        model,
        selected_text,
        user_prompt,
        on_success,
        on_error=None
    ):
        """Non-streaming AI request (fallback)."""

        def task():
            prompt = self.prompt_engine.build_prompt(
                selected_text,
                user_prompt
            )

            return self.ollama.generate(
                model=model,
                prompt=prompt
            )

        TaskRunner.run(
            task=task,
            on_success=on_success,
            on_error=on_error
        )

    def ask_ai_stream(
        self,
        model,
        selected_text,
        user_prompt,
        on_token,
        on_done,
        on_error
    ):
        """Streaming AI request — tokens arrive in real-time."""

        def task():
            prompt = self.prompt_engine.build_prompt(
                selected_text,
                user_prompt
            )

            self.ollama.generate_stream(
                model=model,
                prompt=prompt,
                on_token=on_token,
                on_done=on_done,
                on_error=on_error
            )

        TaskRunner.run_simple(task)

    def copy_to_clipboard(self, text):
        self.clipboard.copy_to_clipboard(text)

    def check_ollama(self):
        return self.ollama.check_connection()