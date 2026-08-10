import json
import os
import requests
from dotenv import load_dotenv


class OpenAIClient:
    """
    OpenAI API client with streaming support.
    Loads API key securely from .env file.
    """

    def __init__(self):
        # Load .env from project root
        from pathlib import Path
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)

        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate(self, model, prompt):
        """Non-streaming request to OpenAI."""
        if not self.api_key:
            return {
                "success": False,
                "response": "OpenAI API key not configured.\nAdd it to the .env file."
            }

        try:
            response = requests.post(
                self.base_url,
                headers=self._headers(),
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                },
                timeout=120
            )

            if response.status_code == 401:
                return {
                    "success": False,
                    "response": "Invalid OpenAI API key. Check your .env file."
                }

            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            return {"success": True, "response": content}

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "response": "Cannot connect to OpenAI API.\nCheck your internet connection."
            }
        except requests.exceptions.Timeout:
            return {"success": False, "response": "Request timed out."}
        except Exception as e:
            return {"success": False, "response": f"Error: {e}"}

    def generate_stream(self, model, prompt, on_token, on_done, on_error):
        """Stream response from OpenAI token-by-token."""
        if not self.api_key:
            on_error("OpenAI API key not configured.\nAdd it to the .env file.")
            return

        try:
            response = requests.post(
                self.base_url,
                headers=self._headers(),
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": True
                },
                stream=True,
                timeout=120
            )

            if response.status_code == 401:
                on_error("Invalid OpenAI API key. Check your .env file.")
                return

            if response.status_code == 429:
                on_error("OpenAI rate limit reached. Try again in a moment.")
                return

            response.raise_for_status()

            full_response = ""

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")

                    # Skip non-data lines
                    if not line_str.startswith("data: "):
                        continue

                    data_str = line_str[6:]  # Remove "data: " prefix

                    # Stream end signal
                    if data_str.strip() == "[DONE]":
                        on_done(full_response)
                        return

                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0].get("delta", {})
                        token = delta.get("content", "")

                        if token:
                            full_response += token
                            on_token(token)

                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

            on_done(full_response)

        except requests.exceptions.ConnectionError:
            on_error("Cannot connect to OpenAI API.\nCheck your internet connection.")
        except requests.exceptions.Timeout:
            on_error("Request timed out.")
        except Exception as e:
            on_error(f"Error: {e}")

    def check_connection(self):
        """Verify the API key is valid by making a small request."""
        if not self.api_key:
            return False
        try:
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=self._headers(),
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
