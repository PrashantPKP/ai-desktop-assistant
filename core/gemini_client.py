import json
import os
import requests
from dotenv import load_dotenv


class GeminiClient:
    """
    Google Gemini API client with streaming support.
    Uses the REST API directly — no heavy SDK needed.
    """

    def __init__(self):
        from pathlib import Path
        load_dotenv(Path(__file__).parent.parent / ".env")

        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate(self, model, prompt):
        """Non-streaming Gemini request."""
        if not self.api_key:
            return {"success": False, "response": "Gemini API key not configured.\nAdd it to the .env file."}

        try:
            url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
            response = requests.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=120
            )

            if response.status_code == 400:
                return {"success": False, "response": "Invalid request. Check the model name."}
            if response.status_code in (401, 403):
                return {"success": False, "response": "Invalid Gemini API key. Check your .env file."}

            response.raise_for_status()
            data = response.json()

            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"success": True, "response": text}

        except requests.exceptions.ConnectionError:
            return {"success": False, "response": "Cannot connect to Gemini API.\nCheck your internet connection."}
        except Exception as e:
            return {"success": False, "response": f"Error: {e}"}

    def generate_stream(self, model, prompt, on_token, on_done, on_error):
        """Stream response from Gemini token-by-token via SSE."""
        if not self.api_key:
            on_error("Gemini API key not configured.\nAdd it to the .env file.")
            return

        try:
            url = f"{self.base_url}/{model}:streamGenerateContent?alt=sse&key={self.api_key}"
            response = requests.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                stream=True,
                timeout=120
            )

            if response.status_code in (401, 403):
                on_error("Invalid Gemini API key. Check your .env file.")
                return
            if response.status_code == 429:
                on_error("Gemini rate limit reached. Try again in a moment.")
                return

            response.raise_for_status()
            full_response = ""

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")

                    if not line_str.startswith("data: "):
                        continue

                    data_str = line_str[6:]

                    try:
                        data = json.loads(data_str)
                        parts = (data.get("candidates", [{}])[0]
                                 .get("content", {})
                                 .get("parts", []))

                        for part in parts:
                            token = part.get("text", "")
                            if token:
                                full_response += token
                                on_token(token)

                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

            on_done(full_response)

        except requests.exceptions.ConnectionError:
            on_error("Cannot connect to Gemini API.\nCheck your internet connection.")
        except requests.exceptions.Timeout:
            on_error("Request timed out.")
        except Exception as e:
            on_error(f"Error: {e}")

    def check_connection(self):
        """Verify API key works."""
        if not self.api_key:
            return False
        try:
            url = f"{self.base_url}?key={self.api_key}"
            r = requests.get(url, timeout=10)
            return r.status_code == 200
        except Exception:
            return False
