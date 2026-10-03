"""Pruebas de reglas y estructura de la arquitectura jerárquica."""
from test_centralized import test_casos_minimos


def test_casos_minimos_jerarquica(monkeypatch):
    test_casos_minimos(monkeypatch)


def test_supervisores_usan_as_tool():
    for filename in ("hierarchical/main_supervisor.py", "hierarchical/information_supervisor.py", "hierarchical/booking_supervisor.py"):
        assert "as_tool" in open(filename, encoding="utf-8").read()
