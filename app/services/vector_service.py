# services/vector_service.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import faiss, pickle, os

def process_file(content: bytes, tenant_id: int):
    text = content.decode("utf-8", errors="ignore")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(text)

    embeddings = OpenAIEmbeddings()
    vectors = embeddings.embed_documents(chunks)

    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(vectors)
    os.makedirs("storage", exist_ok=True)
    with open(f"storage/{tenant_id}_faiss.pkl", "wb") as f:
        pickle.dump(index, f)
