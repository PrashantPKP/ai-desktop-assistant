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