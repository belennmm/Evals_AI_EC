from agents import Agent
from shared.model_config import build_model
from centralized.weather_agent import consultar_clima
from decentralized.handoff_config import create_handoff


def create_agent(safety_agent: Agent) -> Agent:
    return Agent(name="Weather Agent", instructions="Consulta el clima. Si es válido, transfiere a Safety Agent con el JSON; si hay ERROR_CLIMA, informa y finaliza.", tools=[consultar_clima], handoffs=[create_handoff(safety_agent, "Transfiere el contexto meteorológico a Safety Agent.")], model=build_model())
