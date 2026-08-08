import json
import requests
from core.settings_manager import SettingsManager


class OllamaClient:
    def __init__(self):
        settings = SettingsManager()
        self.host = settings.get("ollama.host", "http://localhost:11434")
        self.generate_url = f"{self.host}/api/generate"

    def generate(self, model, prompt):
        """
        Send a prompt to Ollama and return the full response.
        Used as fallback when streaming is not needed.
        """

        try:
            response = requests.post(
                self.generate_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300
            )

            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "response": data.get("response", "")
            }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "response": (
                    "Cannot connect to Ollama.\n\n"
                    "Make sure Ollama is running on your system."
                )
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "response": "Request timed out. The model may be too slow."
            }

        except Exception as e:
            return {
                "success": False,
                "response": f"Error: {e}"
            }

    def generate_stream(self, model, prompt, on_token, on_done, on_error):
        """
        Stream response from Ollama token-by-token.

        Args:
            model: Model name string
            prompt: Full prompt string
            on_token: Callback(token_text) called for each token
            on_done: Callback(full_response) called when complete
            on_error: Callback(error_message) called on error
        """

        try:
            response = requests.post(
                self.generate_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=300
            )

            response.raise_for_status()

            full_response = ""

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        token = data.get("response", "")

                        if token:
                            full_response += token
                            on_token(token)

                        if data.get("done", False):
                            on_done(full_response)
                            return

                    except json.JSONDecodeError:
                        continue

            # If we exit the loop without done=True
            on_done(full_response)

        except requests.exceptions.ConnectionError:
            on_error(
                "Cannot connect to Ollama.\n\n"
                "Make sure Ollama is running on your system."
            )

        except requests.exceptions.Timeout:
            on_error("Request timed out. The model may be too slow.")

        except Exception as e:
            on_error(f"Error: {e}")

    def check_connection(self):
        """Check if Ollama is running and reachable."""
        try:
            response = requests.get(self.host, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self):
        """Fetch the list of locally available models from Ollama."""
        try:
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []