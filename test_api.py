import requests
import json

# URL base da API
BASE_URL = "http://localhost:8000"

def test_health():
    """Testa o endpoint de saúde"""
    print("=== Testando Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_tools():
    """Lista as ferramentas disponíveis"""
    print("=== Listando Ferramentas ===")
    response = requests.get(f"{BASE_URL}/tools")
    print(f"Status: {response.status_code}")
    tools = response.json()
    for tool in tools["tools"]:
        print(f"- {tool['name']}: {tool['description']}")
    print()

def test_chat(message, thread_id="test-thread"):
    """Testa o endpoint de chat"""
    print(f"=== Testando Chat: '{message}' ===")
    
    payload = {
        "message": message,
        "thread_id": thread_id
    }
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Thread ID: {result['thread_id']}")
        print(f"Resposta: {result['response']}")
    else:
        print(f"Erro: {response.text}")
    print()

def main():
    """Executa todos os testes"""
    print("🚀 Testando API do Agente Multimodal\n")
    
    try:
        # Teste de saúde
        test_health()
        
        # Lista ferramentas
        test_tools()
        
        # Testes de chat
        test_chat("Olá! Como você pode me ajudar?")
        test_chat("Como emitir uma nota fiscal?")
        test_chat("Qual é o status de uma nota fiscal transmitida?")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API.")
        print("Certifique-se de que o servidor está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()