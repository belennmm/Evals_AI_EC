"""Especialista de seguridad que reutiliza las reglas existentes."""
import json
from agents import Agent, function_tool
from pydantic import BaseModel, Field
from shared.model_config import build_model
from shared.safety_tool import evaluar_seguridad


class SafetyAgentInput(BaseModel):
    """Contrato estructurado para invocar Safety Agent como herramienta."""

    fecha: str = Field(description="Fecha de las condiciones evaluadas, YYYY-MM-DD.")
    temperatura_2m: float = Field(description="Temperatura promedio en grados Celsius.")
    precipitacion: float = Field(description="Precipitación acumulada en milímetros.")
    cobertura_nubes: float = Field(description="Cobertura máxima de nubes en porcentaje.")
    velocidad_viento: float = Field(description="Velocidad máxima del viento en km/h.")
    rachas_viento: float = Field(description="Ráfagas máximas de viento en km/h.")


def resolver_seguridad(
    fecha: str,
    temperatura_2m: float,
    precipitacion: float,
    cobertura_nubes: float,
    velocidad_viento: float,
    rachas_viento: float,
) -> str:
    """Reutiliza la regla de seguridad compartida con datos estructurados."""
    try:
        datos_clima = {
            "fecha": fecha,
            "temperatura_2m": temperatura_2m,
            "precipitacion": precipitacion,
            "cobertura_nubes": cobertura_nubes,
            "velocidad_viento": velocidad_viento,
            "rachas_viento": rachas_viento,
        }
        return json.dumps(evaluar_seguridad(datos_clima), ensure_ascii=False)
    except (KeyError, TypeError) as error:
        return f"ERROR_SEGURIDAD: datos climáticos inválidos ({error})"


@function_tool
def evaluar_condiciones(
    fecha: str,
    temperatura_2m: float,
    precipitacion: float,
    cobertura_nubes: float,
    velocidad_viento: float,
    rachas_viento: float,
) -> str:
    """Evalúa clima estructurado y devuelve estado IDEAL, MARGINAL o PROHIBIDO."""
    return resolver_seguridad(
        fecha,
        temperatura_2m,
        precipitacion,
        cobertura_nubes,
        velocidad_viento,
        rachas_viento,
    )


def create_agent() -> Agent:
    return Agent(name="Safety Agent", instructions="Evalúa exclusivamente datos meteorológicos mediante la herramienta y reporta su resultado completo.", tools=[evaluar_condiciones], model=build_model())
