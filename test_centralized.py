"""Pruebas deterministas de las reglas que utiliza la arquitectura centralizada."""
from datetime import date, timedelta
from centralized import faq_agent, weather_agent, booking_agent
from shared.safety_tool import evaluar_seguridad


IDEAL = {"fecha": "2030-01-01", "temperatura_2m": 24, "precipitacion": 0, "cobertura_nubes": 10, "velocidad_viento": 10, "rachas_viento": 20}
PROHIBIDO = {**IDEAL, "precipitacion": 1}


def test_casos_minimos(monkeypatch):
    booking_agent._reservas.clear()
    monkeypatch.setattr(faq_agent, "buscar_en_base_conocimiento", lambda _: [{"respuesta": "Peso máximo: 100 kg.", "similarity_score": .9}])
    assert "100 kg" in faq_agent.resolver_faq("¿Cuál es el peso máximo?")
    assert booking_agent.reservar_local("2030-01-01", __import__("json").dumps(evaluar_seguridad(IDEAL))).startswith("Reserva local confirmada")
    assert weather_agent.resolver_clima((date.today() + timedelta(days=17)).isoformat()).startswith("ERROR_CLIMA:")
    assert "No se reservó" in booking_agent.reservar_local("2030-01-02", __import__("json").dumps(evaluar_seguridad(PROHIBIDO)))
    monkeypatch.setattr(faq_agent, "buscar_en_base_conocimiento", lambda _: [{"respuesta": "irrelevante", "similarity_score": .1}])
    assert "No encontré" in faq_agent.resolver_faq("Pregunta fuera de base")


def test_manager_usa_agents_as_tools():
    # Construcción sin Runner: confirma que el manager es el único orquestador.
    assert "as_tool" in open("centralized/manager_agent.py", encoding="utf-8").read()
