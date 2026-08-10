from core.clipboard import ClipboardManager
from core.prompt_engine import PromptEngine
from core.ollama_client import OllamaClient
from core.openai_client import OpenAIClient
from core.gemini_client import GeminiClient
from core.model_manager import ModelManager
from core.task_runner import TaskRunner


class AssistantController:
    def __init__(self):
        self.clipboard = ClipboardManager()
        self.prompt_engine = PromptEngine()
        self.model_manager = ModelManager()
        self.ollama = OllamaClient()
        self.openai = OpenAIClient()
        self.gemini = GeminiClient()

    def _get_client(self, model_name):
        """Return the correct client based on the model's provider."""
        model = self.model_manager.get_model(model_name)
        provider = model.get("provider", "ollama") if model else "ollama"

        if provider == "openai":
            return self.openai
        if provider == "gemini":
            return self.gemini
        return self.ollama

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

            client = self._get_client(model)
            return client.generate(
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
        on_error,
        images=None
    ):
        """Streaming AI request — routes to correct provider."""

        def task():
            prompt = self.prompt_engine.build_prompt(
                selected_text,
                user_prompt
            )

            client = self._get_client(model)
            kwargs = {
                "model": model,
                "prompt": prompt,
                "on_token": on_token,
                "on_done": on_done,
                "on_error": on_error
            }
            if images:
                kwargs["images"] = images
            client.generate_stream(**kwargs)

        TaskRunner.run_simple(task)

    def copy_to_clipboard(self, text):
        self.clipboard.copy_to_clipboard(text)

    def check_ollama(self):
        return self.ollama.check_connection()

    def start_ollama(self):
        return self.ollama.start_ollama()