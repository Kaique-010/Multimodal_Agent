import os
import operator
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List

# LangChain e LangGraph
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory
from langgraph.graph import END, StateGraph


from AgenteLang.categorias_intencao import categorias_intencao

load_dotenv()

# Modelo de linguagem
llm = ChatOpenAI(model='gpt-4o', temperature=0)

# --- ESTADO CORRIGIDO ---
class AgentState(TypedDict):
    """
    Define os estados do agente.
    'history' agora usa a sintaxe correta para acumular mensagens.
    """
    input: str
    intencao: str
    resposta_final: str
    # A forma correta de definir um histórico que se acumula no LangGraph
    history: Annotated[List[BaseMessage], operator.add]

# --- NÓS CORRIGIDOS PARA USAR A MEMÓRIA ---

def classificar_intencao(state: AgentState) -> dict:
    """
    Classifica a intenção do usuário usando o histórico para contexto.
    """
    print("--- 🧠 Classificando intenção ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é um classificador de intenção. Sua tarefa é analisar a última mensagem do usuário, usando o histórico da conversa para contexto, e classificá-la em uma das seguintes categorias:
        {categorias}
        Responda APENAS com o nome da categoria."""),
        MessagesPlaceholder(variable_name="history"), # Onde o histórico é inserido
    ])
    chain = prompt | llm | StrOutputParser()
    intencao_classificada = chain.invoke({
        "history": state['history'],
        "categorias": ", ".join(categorias_intencao)
    })
    return {"intencao": intencao_classificada}

def responder_busca_info(state: AgentState) -> dict:
    """
    Nó especialista que usa o histórico para responder perguntas.
    """
    print("--- 🔍 Respondendo busca de informação (com memória) ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente de pesquisa prestativo. Use o histórico da conversa para responder a pergunta do usuário de forma completa e contextual."),
        MessagesPlaceholder(variable_name="history"),
    ])
    chain = prompt | llm | StrOutputParser()
    resposta = chain.invoke({"history": state['history']})
    return {"resposta_final": resposta}

def responder_saudacao(state: AgentState) -> dict:
    """
    Nó especialista que usa o histórico para responder cumprimentos.
    """
    print("--- 👋 Respondendo saudação (com memória) ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente amigável e educado. Use o histórico para responder ao cumprimento do usuário de forma simpática e contextual."),
        MessagesPlaceholder(variable_name="history"),
    ])
    chain = prompt | llm | StrOutputParser()
    resposta = chain.invoke({"history": state['history']})
    return {"resposta_final": resposta}

# --- LÓGICA DE ROTEAMENTO (sem alterações) ---
def decidir_proximo_passo(state: AgentState) -> str:
    print(f"--- 🛤️ Decidindo rota com base na intenção: {state['intencao']} ---")
    if "BUSCA_INFO" in state['intencao']:
        return "node_busca_info"
    else:
        return "node_saudacao"

# --- MONTAGEM DO GRAFO (sem alterações) ---
graph = StateGraph(AgentState)
graph.add_node('classificador', classificar_intencao)
graph.add_node('node_busca_info', responder_busca_info)
graph.add_node('node_saudacao', responder_saudacao)
graph.set_entry_point('classificador')
graph.add_conditional_edges(
    'classificador',
    decidir_proximo_passo,
    {"node_busca_info": "node_busca_info", "node_saudacao": "node_saudacao"}
)
graph.add_edge('node_busca_info', END)
graph.add_edge('node_saudacao', END)
app = graph.compile()

# --- LOOP DE CONVERSA CORRIGIDO ---

# 1. A memória é inicializada FORA do loop
history = ChatMessageHistory()

while True:
    input_usuario = input("Você: ")
    if input_usuario.lower() in ['sair', 'exit']:
        break

    # 2. Adiciona a nova mensagem do usuário ao histórico
    history.add_user_message(input_usuario)

    # 3. Invoca o grafo com o histórico completo
    # O grafo internamente adicionará a resposta da IA ao estado
    resultado = app.invoke({"history": history.messages, "input": input_usuario})
    
    resposta_agente = resultado['resposta_final']

    # 4. Adiciona a resposta do agente ao histórico para a próxima rodada
    history.add_ai_message(resposta_agente)
    
    print(f"Agente: {resposta_agente}")