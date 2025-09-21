from workflows.raciocinio import grafo_raciocinio
from langchain_core.messages import HumanMessage

class Orquestrador:
    def __init__(self):
        self.grafo = grafo_raciocinio
        
    def run(self, input_text: str) -> str:
        """
        Executa o fluxo de raciocínio do grafo com a entrada fornecida.
        """
        estado_inicial = {"input": input_text, "intermediate_steps": [], "chat_history": []}

        #Stream para ver os passos do grafo
        eventos = self.grafo.stream(estado_inicial, {"recursion_limit": 100})
        resposta_final = None
        for evento in eventos:
            if 'sintese_node' in evento:
                resposta_final = evento['sintese_node']['agent_outcome']
                print("Resposta-------------Final")
                print(resposta_final)
        return resposta_final