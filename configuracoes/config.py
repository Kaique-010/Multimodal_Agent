import os
from dotenv import load_dotenv

load_dotenv()

# Configurações da API
API_KEY = os.environ.get("OPENAI_API_KEY")
EMBED_DIM = 3072  # text-embedding-3-large

# Caminhos dos arquivos
CAMINHO_FAISS = "faiss/faiss_full_rag.index"
CAMINHO_META = "faiss/faiss_full_rag_meta.pkl"
DATASET_PATH = "dataset_finetuning.jsonl"
DB_PATH = "db/manuais.db"

# Configurações do modelo
EMBEDDING_MODEL = "text-embedding-3-large"
CHAT_MODEL = "gpt-4o"
TOKENIZER_ENCODING = "cl100k_base"

# Configurações de chunking
MAX_TOKENS_PER_CHUNK = 500
DEFAULT_TOP_K = 3
DEFAULT_SIMILARITY_THRESHOLD = 0.5  # Reduzido de 0.75 para 0.5