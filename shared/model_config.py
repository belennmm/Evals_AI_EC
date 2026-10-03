import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

load_dotenv()

set_tracing_disabled(True)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-120b"


def build_model():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("No se encontró GROQ_API_KEY en el archivo .env")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
    )

    return OpenAIChatCompletionsModel(
        model=GROQ_MODEL,
        openai_client=client,
    )