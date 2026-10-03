"""Calendario local en memoria; no modifica PostgreSQL."""
import json
from agents import Agent, function_tool
from shared.model_config import build_model

_reservas: list[str] = []


def reservar_local(fecha: str, seguridad_json: str) -> str:
    """Registra una reserva solo si el dict de seguridad permite saltar."""
    try:
        seguridad = json.loads(seguridad_json)
    except json.JSONDecodeError:
        return "No se reservó: la evaluación de seguridad no es válida."
    if not seguridad.get("puede_saltar"):
        return "No se reservó: las condiciones son PROHIBIDAS para saltar."
    if fecha in _reservas:
        return f"La fecha {fecha} ya tiene una reserva local."
    _reservas.append(fecha)
    nota = " (solo tándem experimentado)" if seguridad.get("estado") == "MARGINAL" else ""
    return f"Reserva local confirmada para {fecha}{nota}."


@function_tool
def crear_reserva(fecha: str, seguridad_json: str) -> str:
    """Crea una reserva local después de una evaluación de seguridad válida."""
    return reservar_local(fecha, seguridad_json)


def create_agent() -> Agent:
    return Agent(name="Booking Agent", instructions="Solo usa crear_reserva después de recibir una evaluación de seguridad; nunca reserves un estado PROHIBIDO.", tools=[crear_reserva], model=build_model())
