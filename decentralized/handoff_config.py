"""Handoffs con schema explícito compatible con Chat Completions."""
from agents import Agent, handoff
from pydantic import BaseModel, Field


class HandoffSummary(BaseModel):
    """Metadato mínimo para que el tool de handoff tenga properties válidas."""

    resumen: str = Field(description="Resumen breve del motivo y contexto de la transferencia.")


def _on_handoff(_context: object, _input: HandoffSummary) -> None:
    """La conversación existente se conserva; no se requiere efecto adicional."""


def create_handoff(target_agent: Agent, description: str):
    """Crea un handoff real con un contrato JSON explícito para Groq."""
    return handoff(
        target_agent,
        tool_description_override=f"{description} Incluye un resumen breve en el campo resumen.",
        input_type=HandoffSummary,
        on_handoff=_on_handoff,
    )
