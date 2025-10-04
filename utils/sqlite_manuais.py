import sqlite3
import numpy as np
from openai import OpenAI
from configuracoes.config import API_KEY, DB_PATH, EMBEDDING_MODEL

client = OpenAI(api_key=API_KEY)

# Cria tabela
with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS manuais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            embedding BLOB
        )
    """)
    conn.commit()

def gerar_embedding(texto: str):
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=texto)
    return np.array(resp.data[0].embedding, dtype="float32")

def inserir_manual_com_embedding(titulo: str, url: str):
    embedding = gerar_embedding(titulo)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO manuais (titulo, url, embedding) VALUES (?, ?, ?)",
                (titulo, url, embedding.tobytes())
            )
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"Manual já existe: {url}")

def buscar_manual_por_pergunta_vetorial(pergunta: str, top_n: int = 3):
    query_emb = gerar_embedding(pergunta)
    resultados = []

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, titulo, url, embedding FROM manuais")
        rows = c.fetchall()
        for id_, titulo, url, emb_blob in rows:
            emb = np.frombuffer(emb_blob, dtype="float32")
            sim = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
            resultados.append((sim, id_, titulo, url))
    
    resultados.sort(reverse=True, key=lambda x: x[0])
    return resultados[:top_n]

def buscar_manual_por_id(id_: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, titulo, url, embedding FROM manuais WHERE id = ?", (id_,))
        row = c.fetchone()
        if row:
            id_, titulo, url, emb_blob = row
            emb = np.frombuffer(emb_blob, dtype="float32")
            return id_, titulo, url, emb
        return None