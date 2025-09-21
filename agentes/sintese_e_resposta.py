from agno.agent import Agent
from agno.models.openai import OpenAIChat
from configuracoes.settings import settings
from configuracoes.prompts import Prompts

def criar_agente_sintese() -> Agent:
    """
    Cria um agente de síntese de respostas.
    """
    llm = OpenAIChat(
        id="gpt-4o",
        api_key=settings.OPENAI_API_KEY,
        temperature=0
    )

    agente_sintese = Agent(
        model=llm,
        instructions=Prompts.AGENTE_SINTESE_E_RESPOSTA, 
        name="agente_sintese", 
        description="Agente especializado na síntese de respostas."
    )
    return agente_sintese
