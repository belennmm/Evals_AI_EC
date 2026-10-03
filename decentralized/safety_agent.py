from agents import Agent
from shared.model_config import build_model
from centralized.safety_agent import evaluar_condiciones
from decentralized.handoff_config import create_handoff


def create_agent(booking_agent: Agent) -> Agent:
    return Agent(name="Safety Agent", instructions="Evalúa el JSON climático. Si puede_saltar es true, transfiere a Booking Agent con el contexto; si es PROHIBIDO, responde y finaliza.", tools=[evaluar_condiciones], handoffs=[create_handoff(booking_agent, "Transfiere una reserva autorizada a Booking Agent.")], model=build_model())
