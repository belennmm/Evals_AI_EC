"""Especialista meteorológico que reutiliza Open-Meteo."""
import json
from agents import Agent, function_tool
from pydantic import BaseModel, Field
from shared.model_config import build_model
from shared.weather_tool import consultar_clima_open_meteo


class WeatherAgentInput(BaseModel):
    """Contrato estructurado para invocar Weather Agent como herramienta."""

    fecha: str = Field(description="Fecha del pronóstico en formato YYYY-MM-DD.")


def resolver_clima(fecha: str) -> str:
    """Obtiene el pronóstico agregado de Parachute S.A. para YYYY-MM-DD."""
    try:
        return json.dumps(consultar_clima_open_meteo(fecha), ensure_ascii=False)
    except (ValueError, ConnectionError) as error:
        return f"ERROR_CLIMA: {error}"


@function_tool
def consultar_clima(fecha: str) -> str:
    """Obtiene el pronóstico agregado de Parachute S.A. para YYYY-MM-DD."""
    return resolver_clima(fecha)


def create_agent() -> Agent:
    return Agent(name="Weather Agent", instructions="Extrae una fecha YYYY-MM-DD y consulta el clima. No emitas decisiones de seguridad.", tools=[consultar_clima], model=build_model())
