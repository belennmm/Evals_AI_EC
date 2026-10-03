from agents import Agent, Runner
from shared.model_config import build_model
from hierarchical.information_supervisor import create_information_supervisor
from hierarchical.booking_supervisor import create_booking_supervisor


def create_main_supervisor() -> Agent:
    info, booking = create_information_supervisor(), create_booking_supervisor()
    return Agent(name="Main Supervisor", instructions="Clasifica la solicitud: FAQs van a Information Supervisor; reservas a Booking Supervisor. Conserva la respuesta final.", tools=[info.as_tool(tool_name="information_supervisor", tool_description="Atiende información y FAQs."), booking.as_tool(tool_name="booking_supervisor", tool_description="Gestiona reservas seguras.")], model=build_model())


if __name__ == "__main__":
    print("=== Arquitectura Jerárquica ===")
    print("Escribe 'salir' para terminar.")
    agent = create_main_supervisor()

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
