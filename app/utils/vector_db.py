import os
import re
import pymupdf
from bangla_pdf_ocr import process_pdf
import hashlib
import json
import torch
import unicodedata
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from utils.utils import clean_full_text
from config import EMB_MODEL, QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, VECTOR_SIZE, KNOWLEDGE_BASE_PATH

HASH_INDEX_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmp/vector_hash_index.json")
device = "cuda" if torch.cuda.is_available() else "cpu"

class VectorDB:
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.__create_collection()
        self.embedding = HuggingFaceEmbeddings(model_name=EMB_MODEL, model_kwargs={'device': device})
        self.vector_store = QdrantVectorStore(client=self.client, collection_name=COLLECTION_NAME, embedding=self.embedding)
        self.hash_index = self.__load_hash_index()
        self.__add_contexts(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), KNOWLEDGE_BASE_PATH))
        self.__save_hash_index()

    def __load_hash_index(self):
        if os.path.exists(HASH_INDEX_FILE):
            with open(HASH_INDEX_FILE, "r") as f:
                return json.load(f)
        return {}

    def __save_hash_index(self):
        with open(HASH_INDEX_FILE, "w") as f:
            json.dump(self.hash_index, f, indent=2)

    def __hash_file(self, text):
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def __add_contexts(self, folder_path):
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if file_path.endswith(".pdf"):
                text = self.__load_broken_pdf(file_path)
                text = clean_full_text(text)
                source_name = file_path.split("/")[-1].strip()
            else:
                print(f"Only PDF files are considered for now. Skipping {file}")
                continue
            file_hash = self.__hash_file(text)
            if file_hash in self.hash_index:
                print(f"Skipping {file}: Already added.")
                continue
            chunks = self.__create_chunks(text)
            self.__create_collection()
            docs = [Document(page_content=chunk, metadata={"source": source_name}) for chunk in chunks]
            self.vector_store.add_documents(docs)
            self.hash_index[file_hash] = source_name
        return
    
    def __load_broken_pdf(self, file_path):
        full_text = process_pdf(file_path)
        return unicodedata.normalize("NFC", full_text)
    
    def __create_chunks(self, text, chunk_size=100, chunk_overlap=10):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "।", " "]
        )
        return splitter.split_text(text)

    def __create_collection(self):
        if not self.client.collection_exists("chatbot_context"):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )