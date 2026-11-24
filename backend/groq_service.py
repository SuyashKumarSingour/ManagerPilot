import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

env_file = Path(__file__).resolve().parent / ".env"
load_dotenv(env_file)


def analyze_requirements(text: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from the .env file.")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You help an Engineering Manager review requirements. "
                    "Identify possible gaps and separate questions into "
                    "EM-level and client-level questions. "
                    "Do not invent information."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )

    return response.choices[0].message.content or ""


if __name__ == "__main__":
    sample = "A customer can place an order through a website."
    print(analyze_requirements(sample))