from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from dotenv import load_dotenv

# Carrega variáveis de ambiente
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

# Inicialização do FastAPI
app = FastAPI(
    title="Agente Spartacus API",
    description="API para interação com agente inteligente Spartacus",
    version="1.0.0"
)

# Configuração CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização do agente
llm = ChatOpenAI(model=CHAT_MODEL, temperature=0)
memoria = MemorySaver()

agente_react = create_react_agent(
    llm,
    tools=[rag_url_resposta_vetorial, rag_url_resposta, inspector_faiss, faiss_condicional_qa, salvar_dataset_finetuning],
    checkpointer=memoria
)

# Modelos Pydantic
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    thread_id: str

class HealthResponse(BaseModel):
    status: str
    message: str

# Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Endpoint de saúde da API"""
    return HealthResponse(status="ok", message="Agente Spartacus  está funcionando!")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificação de saúde da API"""
    return HealthResponse(status="healthy", message="API está operacional")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint principal para chat com o agente
    
    - **message**: Mensagem do usuário
    - **thread_id**: ID da conversa (opcional, padrão: 'default')
    """
    try:
        config = {'configurable': {"thread_id": request.thread_id}}
        mensagem = [HumanMessage(content=request.message)]
        
        # Processa a mensagem através do agente
        response_content = ""
        async for evento in agente_react.astream({"messages": mensagem}, config, stream_mode="values"):
            if evento['messages']:
                last_message = evento['messages'][-1]
                if hasattr(last_message, 'content'):
                    response_content = last_message.content
        
        return ChatResponse(
            response=response_content,
            thread_id=request.thread_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar mensagem: {str(e)}")

@app.get("/tools")
async def list_tools():
    """Lista todas as ferramentas disponíveis no agente"""
    tools_info = [
        {
            "name": "rag_url_resposta_vetorial",
            "description": "Busca manuais relevantes no banco vetorial e extrai conteúdo de URL"
        },
        {
            "name": "rag_url_resposta", 
            "description": "Extrai conteúdo de uma URL e responde perguntas usando RAG"
        },
        {
            "name": "inspector_faiss",
            "description": "Inspeciona o índice FAISS e retorna informações sobre chunks relevantes"
        },
        {
            "name": "faiss_condicional_qa",
            "description": "Busca chunks relevantes no índice FAISS com base em limiar de similaridade"
        },
        {
            "name": "salvar_dataset_finetuning",
            "description": "Salva pares pergunta-resposta para dataset de fine-tuning"
        }
    ]
    return {"tools": tools_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)