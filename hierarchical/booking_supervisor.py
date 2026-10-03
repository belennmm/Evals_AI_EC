from agents import Agent
from shared.model_config import build_model
from centralized.weather_agent import WeatherAgentInput
from centralized.safety_agent import SafetyAgentInput
from hierarchical.weather_agent import create_agent as create_weather_agent
from hierarchical.safety_agent import create_agent as create_safety_agent
from hierarchical.booking_agent import create_agent as create_booking_agent


def create_booking_supervisor() -> Agent:
    weather, safety, booking = create_weather_agent(), create_safety_agent(), create_booking_agent()
    return Agent(name="Booking Supervisor", instructions="Para reservar: Weather Agent, Safety Agent y luego Booking Agent solo si puede_saltar. Si es PROHIBIDO o hay error, no reserves.", tools=[weather.as_tool(tool_name="weather_agent", tool_description="Consulta clima.", parameters=WeatherAgentInput, include_input_schema=True), safety.as_tool(tool_name="safety_agent", tool_description="Evalúa seguridad.", parameters=SafetyAgentInput, include_input_schema=True), booking.as_tool(tool_name="booking_agent", tool_description="Reserva autorizada.")], model=build_model())
