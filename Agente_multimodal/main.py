from .orquestrador import Orquestrador


def main():
    """
    Função principal para interagir com o agente multimodal.
    """
    orquestrador = Orquestrador()
    while True:
        user_input = input("Você: ")
        if user_input.lower() in ["sair", "exit"]:
            break
        response = orquestrador.run(user_input)
        print("Agente:", response)
        
if __name__ == "__main__":
    main()
