from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
import os

DB_DIR = "./faiss_index"

def get_vector_store():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    if os.path.exists(DB_DIR):
        # Allow dangerous deserialization because this is a local, trusted file
        return FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
    return None 

def add_to_store(chunks):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    if os.path.exists(DB_DIR):
        vectorstore = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(chunks)
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(DB_DIR)
    return True