from agents import Agent
from shared.model_config import build_model
from hierarchical.faq_agent import create_agent as create_faq_agent


def create_information_supervisor() -> Agent:
    faq = create_faq_agent()
    return Agent(name="Information Supervisor", instructions="Gestiona solamente consultas informativas mediante FAQ Agent.", tools=[faq.as_tool(tool_name="faq_agent", tool_description="Resuelve FAQs.")], model=build_model())
