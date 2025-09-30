from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class EmbeddingsGenerator:
    def __init__(self, model: str = "text-embedding-3-large"):
        self.client = OpenAI()
        self.model = model

    def embed(self, text: str) -> list[float]:
        resp = self.client.embeddings.create(model=self.model, input=text)
        return resp.data[0].embedding
