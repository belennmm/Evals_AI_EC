from agents import Agent
from shared.model_config import build_model
from centralized.faq_agent import consultar_faq


def create_agent() -> Agent:
    return Agent(name="FAQ Agent", instructions="Resuelve una FAQ directamente con la herramienta y finaliza; no transfieras a otros agentes.", tools=[consultar_faq], model=build_model())
