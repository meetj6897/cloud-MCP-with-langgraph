import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


def main():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENROUTER_API_KEY in your .env file")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost",
                "X-OpenRouter-Title": "My App",
            },
            data=json.dumps({
                "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
                "messages": [
                    {
                        "role": "user",
                        "content": "What is the meaning of life?"
                    }
                ]
            })
        )
        response.raise_for_status()
        print(response.json())
    except requests.exceptions.HTTPError as exc:
        if response.status_code == 429:
            print("Rate limit exceeded. Please wait a few moments and try again.")
        else:
            print(f"Request failed: {exc}")


if __name__ == "__main__":
    main()
