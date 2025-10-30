# services/vector_service.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import faiss
import pickle
import os
import numpy as np

def process_file(content: bytes, tenant_id: int):
    text = content.decode("utf-8", errors="ignore")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(text)

    embeddings = OpenAIEmbeddings()
    vectors = embeddings.embed_documents(chunks)
    
    # Chuyển list thành numpy array
    vectors_array = np.array(vectors).astype('float32')

    index = faiss.IndexFlatL2(vectors_array.shape[1])
    index.add(vectors_array)
    
    os.makedirs("storage", exist_ok=True)
    with open(f"storage/{tenant_id}_faiss.pkl", "wb") as f:
        pickle.dump((index, chunks), f)
