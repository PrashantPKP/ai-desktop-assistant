import requests


class OllamaClient:
    def __init__(self, host="http://localhost:11434"):
        self.host = host
        self.url = f"{host}/api/generate"

    def generate(self, model, prompt):
        """
        Send a prompt to Ollama and return the response.
        """

        try:
            response = requests.post(
                self.url,
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
                "response": "❌ Cannot connect to Ollama.\n\nMake sure Ollama is running."
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "response": "❌ Request timed out."
            }

        except Exception as e:
            return {
                "success": False,
                "response": f"❌ Error:\n{e}"
            }