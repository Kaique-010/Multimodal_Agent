import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import faiss
import pickle
import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np

# -----------------------------
# Configurações LLM e embeddings
# -----------------------------
load_dotenv()
API_KEY = os.environ.get("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o", temperature=0)
client = OpenAI(api_key=API_KEY)
EMBED_DIM = 3072  # text-embedding-3-large
FAISS_PATH = "faiss_full_rag.index"
META_PATH = "faiss_full_rag_meta.pkl"

# -----------------------------
# Inicializa FAISS
# -----------------------------
if os.path.exists(FAISS_PATH):
    index = faiss.read_index(FAISS_PATH)
    with open(META_PATH, "rb") as f:
        meta = pickle.load(f)
else:
    index = faiss.IndexFlatL2(EMBED_DIM)
    meta = []

# -----------------------------
# Função de geração de embedding
# -----------------------------
def embed_text(text: str):
    resp = client.embeddings.create(model="text-embedding-3-large", input=text)
    return np.array(resp.data[0].embedding, dtype="float32")

# -----------------------------
# Função Full-RAG
# -----------------------------
@tool
def rag_url_resposta(url: str, pergunta: str, k: int = 3) -> str:
    """
    Recebe URL, extrai conteúdo, salva embeddings, busca similaridade e responde.
    """
    global index, meta

    # Scraping
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except Exception as e:
        return f"Erro ao acessar URL: {e}"

    soup = BeautifulSoup(r.text, "html.parser")
    artigo = soup.select_one("div.col-sm-9.kb-article-view-content article#kb-article")
    if not artigo:
        return "Não encontrei o artigo na página."

    texto = artigo.get_text(separator="\n", strip=True)
    chunks = [texto[i:i+800] for i in range(0, len(texto), 800)]

    # Gera embeddings e salva no FAISS
    embeddings = [embed_text(c) for c in chunks]
    index.add(np.array(embeddings))
    meta.extend(chunks)

    # Persiste no disco
    faiss.write_index(index, FAISS_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)

    # Busca similaridade para a pergunta
    query_emb = embed_text(pergunta).reshape(1, -1)
    D, I = index.search(query_emb, k)
    contexto = "\n\n".join([meta[i] for i in I[0] if i < len(meta)])

    # Pergunta pro LLM com contexto
    resposta = llm.predict(f"""
Você é um assistente especialista. Use o contexto abaixo para responder a pergunta:

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}
""")
    return resposta
