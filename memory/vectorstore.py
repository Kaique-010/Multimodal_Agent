import faiss
import pickle
import os

class FAISSVectorStore:
    def __init__(self, dim: int = 3072, index_path: str = "faiss_index.index", meta_path: str = "faiss_meta.pkl"):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path

        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            with open(meta_path, "rb") as f:
                self.meta = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.meta = []

    def add(self, texts: list[str], embeddings: list[list[float]]):
        import numpy as np
        vecs = np.array(embeddings).astype("float32")
        self.index.add(vecs)
        self.meta.extend(texts)
        self.save()

    def search(self, query_embedding: list[float], k: int = 5):
        import numpy as np
        vec = np.array([query_embedding]).astype("float32")
        D, I = self.index.search(vec, k)
        results = [self.meta[i] for i in I[0] if i < len(self.meta)]
        return results

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.meta, f)
