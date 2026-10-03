"""Especialista FAQ que reutiliza la búsqueda RAG existente."""
from agents import Agent, function_tool
from shared.model_config import build_model
from knowledge_tool import buscar_en_base_conocimiento


def resolver_faq(pregunta: str) -> str:
    """Busca una respuesta en la base de FAQs de Parachute S.A."""
    resultados = buscar_en_base_conocimiento(pregunta)
    if not resultados or resultados[0].get("error"):
        return "No fue posible consultar la base de conocimiento."
    for resultado in resultados:
        respuesta = resultado.get("respuesta", "")
        if (resultado.get("similarity_score", 0) >= 0.60
                and respuesta
                and not respuesta.startswith("Respuesta detallada para la consulta sobre")):
            return respuesta
    return "No encontré esa información en la base de conocimiento de Parachute S.A."


@function_tool
def consultar_faq(pregunta: str) -> str:
    """Busca una respuesta en la base de FAQs de Parachute S.A."""
    return resolver_faq(pregunta)


def create_agent() -> Agent:
    return Agent(
        name="FAQ Agent",
        instructions=(
            "Consulta siempre consultar_faq con la pregunta del usuario. "
            "Devuelve la respuesta de la herramienta sin agregar datos, cifras ni "
            "servicios de conocimiento externo. Si la herramienta indica que no hay "
            "información o que hubo un error, devuelve únicamente ese mensaje y termina."
        ),
        tools=[consultar_faq],
        model=build_model(),
    )
