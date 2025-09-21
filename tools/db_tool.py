from langchain.tools import tool

@tool
def procura_db(query: str) -> str:
    """
    Procura o banco de dados para responder à pergunta do usuário.
    útil para recuperar informações armazenadas no banco de dados.
    """
    # Lógica para procurar no banco de dados
    return f"Resultado da busca no banco de dados para: {query}"
