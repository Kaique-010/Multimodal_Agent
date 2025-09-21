from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.tools.render import render_text_description
from configuracoes.settings import Settings
from configuracoes.prompts import Prompts 
from tools.web_tool import procura_web
from agentes.sintese_e_resposta import criar_agente_sintese


# Definição do estado do agente do grafo
class AgentState(TypedDict):
    input: str
    chat_history: Annotated[Sequence[BaseMessage], operator.add]
    agent_outcome: str | None
    intermediate_steps: Annotated[list[tuple], operator.add]  


#definir os nós do grafo
llm = ChatOpenAI(temperature=0, model="gpt-4o", api_key=Settings.OPENAI_API_KEY)

#ferramentas do agente aos nós
tools=[procura_web]
rendered_tools = render_text_description(tools)

#nós de detecção de intenções(Roteador)
def No_intent(state: AgentState) -> AgentState:
    """
    Nó de detecção de intenções(Roteador).
    """
    prompt_roteamento = PromptTemplate(
    template = Prompts.AGENTE_ROTEADOR,
    input_variables=["input", "tools"]
    
)
    chain_roteamento = prompt_roteamento | llm
    resultado = chain_roteamento.invoke({"input": state['input'], "tools": rendered_tools})

    # Atualizar o estado com o resultado do roteamento
    if "ferramenta" in resultado.content.lower():
        state['agent_outcome'] = "tools_node"
    else:
        state['agent_outcome'] = "sintese_node"
    
    return state

def tools_node(state: AgentState) -> AgentState:
    """
    Nó de execução de ferramentas.
    """
    for tool in tools:
        if tool.name in state['input'].lower():
            resultado = tool.invoke(state['input'])
            state['intermediate_steps'].append((tool.name, resultado))
            return state
    return state

#nó de execução de ferramentas
def sintese_node(state: AgentState) -> AgentState:
    """
    Nó de execução de ferramentas, gerção de resposta final para o usuário.
    """
    agente_sintese = criar_agente_sintese()
    contexto ="\n".join([f"{step[0]}: {step[1]}" for step in state.get('intermediate_steps', [])])
    
    response = agente_sintese.run(state['input'])
    
    return {"agent_outcome": response}

#COntrução do Grafo
def construir_grafo():
    workflow = StateGraph(AgentState)
    
    #Adicionar os nós
    workflow.add_node("No_intent", No_intent)
    workflow.add_node("tools_node", tools_node)
    workflow.add_node("sintese_node", sintese_node)

    
    #Adicionar as arestas 
    workflow.add_edge("__start__", "No_intent")
    
    def route_decision(state: AgentState) -> str:
        return state['agent_outcome']
    
    workflow.add_conditional_edges(
        "No_intent",
        route_decision,
        {
            "tools_node": "tools_node",
            "sintese_node": "sintese_node",
        }
    )
    workflow.add_edge("tools_node", "sintese_node")
    workflow.add_edge("sintese_node", END)
    
    #Compilar o grafo
    app = workflow.compile()
    return app

#Instanciar o grafo
grafo_raciocinio = construir_grafo()