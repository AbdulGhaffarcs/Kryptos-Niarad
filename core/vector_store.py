"""
core/vector_store.py
FAISS vector store using HuggingFace sentence-transformers for embeddings.
No Ollama required.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

DB_DIR = "./faiss_index"

# Lightweight, fast embedding model — downloads once (~90MB)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


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