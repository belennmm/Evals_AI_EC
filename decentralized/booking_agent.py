from agents import Agent
from shared.model_config import build_model
from centralized.booking_agent import crear_reserva


def create_agent() -> Agent:
    return Agent(name="Booking Agent", instructions="Recibes la evaluación previa. Reserva solo si puede_saltar es true; rechaza PROHIBIDO.", tools=[crear_reserva], model=build_model())
