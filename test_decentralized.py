"""Pruebas de reglas y estructura de la arquitectura descentralizada."""
from test_centralized import test_casos_minimos


def test_casos_minimos_descentralizada(monkeypatch):
    test_casos_minimos(monkeypatch)


def test_flujo_con_handoffs():
    for filename in ("decentralized/entry_agent.py", "decentralized/weather_agent.py", "decentralized/safety_agent.py"):
        assert "handoffs" in open(filename, encoding="utf-8").read()
