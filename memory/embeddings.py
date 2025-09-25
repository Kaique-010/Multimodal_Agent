import os
from langchain.embeddings import OpenAIEmbeddings


def get_embeddings():
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    print("embeddings gerados:", embeddings)
    return embeddings