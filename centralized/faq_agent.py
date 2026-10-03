"""Especialista FAQ que reutiliza la búsqueda RAG existente."""
from agents import Agent, function_tool
from shared.model_config import build_model
from knowledge_tool import buscar_en_base_conocimiento


def resolver_faq(pregunta: str) -> str:
    """Busca una respuesta en la base de FAQs de Parachute S.A."""
    resultados = buscar_en_base_conocimiento(pregunta)
    if not resultados or resultados[0].get("error"):
        return "No fue posible consultar la base de conocimiento."
    mejor = resultados[0]
    if mejor.get("similarity_score", 0) < 0.60:
        return "No encontré esa información en la base de conocimiento de Parachute S.A."
    return mejor["respuesta"]


@function_tool
def consultar_faq(pregunta: str) -> str:
    """Busca una respuesta en la base de FAQs de Parachute S.A."""
    return resolver_faq(pregunta)


def create_agent() -> Agent:
    return Agent(name="FAQ Agent", instructions="Responde solo con información respaldada por la herramienta.", tools=[consultar_faq], model=build_model())
