"""
core/vector_store.py
FAISS-based local vector store for RAG retrieval.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

DB_DIR = "./faiss_index"

def _get_embeddings():
    return OllamaEmbeddings(model="nomic-embed-text")

def get_vector_store():
    """Load existing FAISS index or return None if not found."""
    if not os.path.exists(DB_DIR):
        return None
    try:
        return FAISS.load_local(DB_DIR, _get_embeddings(), allow_dangerous_deserialization=True)
    except Exception:
        return None

def add_to_store(chunks):
    """Add document chunks to the FAISS index, creating it if needed."""
    embeddings = _get_embeddings()
    if os.path.exists(DB_DIR):
        vs = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
        vs.add_documents(chunks)
    else:
        vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(DB_DIR)
    return True

def clear_store():
    """Delete the FAISS index from disk."""
    import shutil
    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)