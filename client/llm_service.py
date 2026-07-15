import os
import json
import threading
import requests
from dotenv import load_dotenv


class OpenRouterService:
    """Singleton wrapper for calling OpenRouter models from anywhere in the project."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.session = requests.Session()

    def generate(self, prompt, model="nousresearch/hermes-3-llama-3.1-405b:free"):
        if not self.api_key:
            raise ValueError("Missing OPENROUTER_API_KEY in your .env file")

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-OpenRouter-Title": "My App",
            "Content-Type": "application/json",
        }

        response = self.session.post(self.base_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    client = OpenRouterService()
    answer = client.generate("Say hello in one short sentence")
    print(answer)
