import os
import pymupdf
import hashlib
import json
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from config import EMB_MODEL, QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, VECTOR_SIZE, KNOWLEDGE_BASE_PATH

HASH_INDEX_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmp/vector_hash_index.json")

class VectorDB:
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.__create_collection()
        self.embedding = HuggingFaceEmbeddings(model_name=EMB_MODEL, model_kwargs={'device': 'cpu'})
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
                text, source_name = self.__load_pdf(file_path)
            else:
                print(f"Only PDF files are supported")
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
    
    def __load_pdf(self, file_path):
        docs = pymupdf.open(file_path)
        full_text = "\n".join([doc.get_text() for doc in docs])
        print(f"PDF Text: {full_text[:50]}")
        return full_text, file_path.split("/")[-1].strip()

    def __create_chunks(self, text, chunk_size=1000, chunk_overlap=50):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " "]
        )
        return splitter.split_text(text)

    def __create_collection(self):
        if not self.client.collection_exists("chatbot_context"):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )