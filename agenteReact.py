# Import HumanMessage para o formato correto das mensagens
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from tools.rag_tool import rag_url_resposta

from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURAÇÃO ---
llm = ChatOpenAI(model='gpt-4o', temperature=0)

# 1. Crie a instância do checkpointer (memória)
memoria = MemorySaver()

# --- CRIAÇÃO DO AGENTE ---
# Corrigido:
# - Removido o argumento 'prompt' para que o LangGraph use o prompt padrão do ReAct, que é essencial.
# - Adicionado o argumento 'checkpointer' para conectar o agente à nossa instância de memória.
agenteReact = create_react_agent(
    llm,
    tools=[rag_url_resposta], 
    checkpointer=memoria # <-- CONECTA A MEMÓRIA AQUI
)

# --- CONFIGURAÇÃO DA CONVERSA ---
# Corrigido: A chave deve ser 'configurable' e não 'configurable0'
config = {'configurable': {
    "thread_id": "conversa_do_rodrigo_1" # Use um ID descritivo
}}

# --- LOOP DO CHAT ---
print("Chatbot iniciado! Digite 'sair' para terminar.")
while True:
    user_input = input("Usuário: ")
    if user_input.lower() == "sair":
        break
        
    # É uma boa prática usar a classe HumanMessage
    mensagem = [HumanMessage(content=user_input)]
    
    # O input do stream é um dicionário com a chave "messages"
    for evento in agenteReact.stream({"messages": mensagem}, config, stream_mode="values"):
        # O evento é um dicionário, e a última mensagem da lista de mensagens é a do assistente
        evento['messages'][-1].pretty_print()