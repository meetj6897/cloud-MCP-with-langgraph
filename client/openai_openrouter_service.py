import os
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError


class OpenAIOpenRouterService:
    """Singleton-style wrapper using the OpenAI SDK pointed at OpenRouter."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        load_dotenv()
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    def create_completion(self, prompt, models=None):
        if models is None:
            models = [
                "nousresearch/hermes-3-llama-3.1-405b:free",
                "nvidia/nemotron-nano-9b-v2:free",
                "nvidia/nemotron-3-ultra-550b-a55b:free",
            ]

        last_error = None
        for model in models:
            try:
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    extra_headers={
                        "HTTP-Referer": "http://localhost",
                        "X-OpenRouter-Title": "My App",
                    },
                )
                return completion.choices[0].message.content
            except RateLimitError as exc:
                last_error = exc
                print(f"Model {model} hit a rate limit. Trying next model...")
            except Exception as exc:
                last_error = exc
                print(f"Model {model} failed. Trying next model...")

        print("All models failed.")
        if last_error is not None:
            print(last_error)
        return None


if __name__ == "__main__":
    service = OpenAIOpenRouterService()
    result = service.create_completion("generate the cute description of the loard hanuman for generating the cartoon image of him")
    if result is not None:
        print(result)
