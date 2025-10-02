from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from configuracoes.config import CHAT_MODEL

from tools.rag_tool import rag_url_resposta_vetorial
from tools.inspector_tools import inspector_faiss, rag_url_resposta
from tools.qa_tools import faiss_condicional_qa
from tools.dataset_tools import salvar_dataset_finetuning

llm = ChatOpenAI(model=CHAT_MODEL, temperature=0)
memoria = MemorySaver()

agenteReact = create_react_agent(
    llm,
    tools=[rag_url_resposta_vetorial, rag_url_resposta, inspector_faiss, faiss_condicional_qa, salvar_dataset_finetuning],
    checkpointer=memoria
)

config = {'configurable': {"thread_id": "1"}}

print("Chatbot iniciado! Digite 'sair' para terminar.")
while True:
    user_input = input("Usuário: ")
    if user_input.lower() == "sair":
        break
    mensagem = [HumanMessage(content=user_input)]
    for evento in agenteReact.stream({"messages": mensagem}, config, stream_mode="values"):
        evento['messages'][-1].pretty_print()
