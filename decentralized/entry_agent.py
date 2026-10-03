from agents import Agent, Runner
from shared.model_config import build_model
from decentralized.faq_agent import create_agent as create_faq_agent
from decentralized.booking_agent import create_agent as create_booking_agent
from decentralized.safety_agent import create_agent as create_safety_agent
from decentralized.weather_agent import create_agent as create_weather_agent
from decentralized.handoff_config import create_handoff


def create_entry_agent() -> Agent:
    booking = create_booking_agent()
    safety = create_safety_agent(booking)
    weather = create_weather_agent(safety)
    faq = create_faq_agent()
    return Agent(name="Parachute Router", instructions="Sin gestionar centralmente: transfiere FAQs directamente a FAQ Agent y solicitudes de reserva a Weather Agent.", handoffs=[create_handoff(faq, "Transfiere una consulta informativa a FAQ Agent."), create_handoff(weather, "Transfiere una solicitud de reserva a Weather Agent.")], model=build_model())


if __name__ == "__main__":
    print("=== Arquitectura Descentralizada ===")
    print("Escribe 'salir' para terminar.")
    agent = create_entry_agent()

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
