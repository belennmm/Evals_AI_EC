"""Prueba de compatibilidad del OpenAI Agents SDK con Groq.

Ejecutar: python test_agents_sdk.py
"""

import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, set_tracing_disabled


MODEL_NAME = "openai/gpt-oss-120b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def build_model() -> OpenAIChatCompletionsModel:
    """Crea el adaptador de Chat Completions para Groq."""
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Falta GROQ_API_KEY en el archivo .env.")

    set_tracing_disabled(disabled=True)
    client = AsyncOpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    return OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)


async def main() -> None:
    agent = Agent(
        name="Agente de compatibilidad",
        instructions="Responde exactamente: COMPATIBLE",
        model=build_model(),
    )
    result = await Runner.run(agent, "Confirma que puedes responder.")
    output = str(result.final_output).strip()
    if "COMPATIBLE" not in output.upper():
        raise AssertionError(f"Respuesta inesperada de Groq: {output!r}")
    print(f"Agents SDK + Groq compatible: {output}")


if __name__ == "__main__":
    asyncio.run(main())
