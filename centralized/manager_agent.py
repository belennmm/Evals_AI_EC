"""Manager único: conserva el control y usa especialistas como herramientas."""
from agents import Agent, Runner
from centralized.faq_agent import create_agent as create_faq_agent
from centralized.weather_agent import WeatherAgentInput, create_agent as create_weather_agent
from centralized.safety_agent import SafetyAgentInput, create_agent as create_safety_agent
from centralized.booking_agent import create_agent as create_booking_agent
from shared.model_config import build_model


def create_manager() -> Agent:
    faq = create_faq_agent()
    weather = create_weather_agent()
    safety = create_safety_agent()
    booking = create_booking_agent()

    return Agent(
        name="Parachute Manager",
        instructions=(
            "Mantienes siempre el control. "
            "Para FAQs usa FAQ Agent y devuelve su respuesta sin añadir información "
            "ni cambiar cifras. Si indica falta de información o error, conserva "
            "únicamente ese mensaje y termina; no ofrezcas otros servicios ni inicies "
            "una reserva que el usuario no haya solicitado. "
            "Para una reserva: pide fecha si falta; "
            "usa Weather Agent, entrega su JSON a Safety Agent "
            "y solo si puede_saltar es true usa Booking Agent. "
            "Ante ERROR_CLIMA o PROHIBIDO no reserves."
        ),
        tools=[
            faq.as_tool(
                tool_name="faq_agent",
                tool_description="Resuelve FAQs con RAG."
            ),
            weather.as_tool(
                tool_name="weather_agent",
                tool_description="Consulta clima por fecha.",
                parameters=WeatherAgentInput,
                include_input_schema=True,
            ),
            safety.as_tool(
                tool_name="safety_agent",
                tool_description="Evalúa seguridad con datos climáticos estructurados.",
                parameters=SafetyAgentInput,
                include_input_schema=True,
            ),
            booking.as_tool(
                tool_name="booking_agent",
                tool_description="Registra una reserva local autorizada."
            ),
        ],
        model=build_model(),
    )


if __name__ == "__main__":
    print("=== Arquitectura Centralizada ===")
    print("Escribe 'salir' para terminar.")
    agent = create_manager()

    while True:
        try:
            user_input = input("\nTú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break

        if user_input.lower() in {"salir", "exit", "quit"}:
            print("Hasta luego.")
            break
        if not user_input:
            continue

        result = Runner.run_sync(agent, user_input)
        print(f"\nParachute: {result.final_output}")
