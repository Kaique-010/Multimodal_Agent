import tiktoken
from langchain.tools import tool
from openai import OpenAI
from utils.rag_memory import rag_memory
from configuracoes.config import API_KEY, TOKENIZER_ENCODING, DEFAULT_TOP_K, DEFAULT_SIMILARITY_THRESHOLD

client = OpenAI(api_key=API_KEY)
tokenizador = tiktoken.get_encoding(TOKENIZER_ENCODING)


@tool
def faiss_condicional_qa(pergunta: str, top_n: int = DEFAULT_TOP_K, limiar_similaridade: float = DEFAULT_SIMILARITY_THRESHOLD, mostrar_chunks: bool = False) -> str:
    """Busca chunks relevantes no índice FAISS com base em limiar de similaridade para QA"""
    query_emb = rag_memory.embed_text(pergunta).reshape(1, -1)
    D, I = rag_memory.index.search(query_emb, top_n)
    
    chunks_para_qa = []
    chunks_para_mostrar = []

    for i, dist in zip(I[0], D[0]):
        similaridade = 1 / (1 + dist)
        chunk = rag_memory.meta[i]
        info_chunk = f"Chunk {i}: {chunk[:100]}... Tokens: {len(tokenizador.encode(chunk))} Hash: {hash(chunk)} Similaridade: {similaridade:.2f}"
        
        if similaridade >= limiar_similaridade:
            chunks_para_qa.append(chunk)
        if mostrar_chunks:
            chunks_para_mostrar.append(info_chunk)
    
    resultado = ""
    if mostrar_chunks:
        resultado += "=== Chunks inspecionados ===\n"
        resultado += "\n".join(chunks_para_mostrar)
        resultado += "\n============================\n"
    
    if chunks_para_qa:
        contexto_qa = "\n\n".join(chunks_para_qa)
        resultado += f"Contexto para QA:\n{contexto_qa}"
    else:
        resultado += "Nenhum chunk passou pelo limiar de similaridade para QA."
    
    return resultado
