import requests
from bs4 import BeautifulSoup
from langchain.tools import tool


@tool
def procura_web(query: str) -> str:
    """
    Procura a internet usando a api de DuckDuckGo para responder à pergunta do usuário.
    útil para buscas inteligentes e atualizadas sobre assuntos gerais 
    """
    url=f"https://duckduckgo.com/html/?q={query}"
    response=requests.get(url)
    if response.status_code!=200:
        return f"Erro ao fazer a requisição: {response.status_code}"
    soup=BeautifulSoup(response.text,"html.parser")
    results=soup.find_all("div",class_="result")
    if not results:
        return "Nenhum resultado encontrado."
    return results[0].text.strip()

