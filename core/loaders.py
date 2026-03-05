import os
import pandas as pd
from langchain_community.document_loaders import (
    PyMuPDFLoader, 
    UnstructuredPowerPointLoader, 
    Docx2txtLoader,
    TextLoader,
    DataFrameLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_file_dynamically(file_path):
    """Detects extension and uses the correct loader."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        return PyMuPDFLoader(file_path).load()
    elif ext == ".docx":
        return Docx2txtLoader(file_path).load()
    elif ext == ".pptx":
        # Note: Unstructured is great for lecture slides
        return UnstructuredPowerPointLoader(file_path).load()
    elif ext in [".xlsx", ".xls", ".csv"]:
        df = pd.read_csv(file_path) if ext == ".csv" else pd.read_excel(file_path)
        # We turn rows into text like 'Column: Value | Column: Value' for the LLM
        df["text_content"] = df.apply(lambda x: " | ".join(f"{k}: {v}" for k, v in x.items()), axis=1)
        return DataFrameLoader(df, page_content_column="text_content").load()
    elif ext == ".txt":
        return TextLoader(file_path).load()
    return []

def get_chunks(docs):
    """Splits loaded documents into smaller pieces for the vector database."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_documents(docs)