import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:1b")
LLM_TEMP = os.getenv("LLM_TEMP", 0.0)
EMB_MODEL = os.getenv("EMB_MODEL", "intfloat/multilingual-e5-base") #intfloat/multilingual-e5-small use this for small models
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = os.getenv("QDRANT_PORT", 6333)
COLLECTION_NAME=os.getenv("COLLECTION_NAME", "chatbot_context")
VECTOR_SIZE=os.getenv("VECTOR_SIZE", 768)
HF_TOKEN = os.getenv("HF_TOKEN")
KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_bases")
STOPWORD_PATH = os.getenv("STOPWORD_PATH", "stop_words")

print(f"="*50)
print(f"OLLAMA_BASE_URL: {OLLAMA_BASE_URL}\nLLM_MODEL: {LLM_MODEL}\nLLM_TEMP: {LLM_TEMP}\nEMB_MODEL: {EMB_MODEL}\nQDRANT_HOST: {QDRANT_HOST}\nQDRANT_PORT: {QDRANT_PORT}\nCOLLECTION_NAME: {COLLECTION_NAME}\nVECTOR_SIZE: {VECTOR_SIZE}")
print(f"="*50)