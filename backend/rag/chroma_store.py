import chromadb
from chromadb.utils import embedding_functions
from backend.config import CHROMA_PATH
import uuid

client = chromadb.PersistentClient(path=CHROMA_PATH)

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def get_collection(name):
    return client.get_or_create_collection(
        name=name,
        embedding_function=embedding_func
    )

def add_documents(collection, docs, source_id: str = None):
    if not docs:
        return
    ids = [str(uuid.uuid4()) for _ in range(len(docs))]
    
    metadatas = None
    if source_id:
        metadatas = [{"source_id": source_id} for _ in range(len(docs))]
        
    collection.add(
        documents=docs,
        ids=ids,
        metadatas=metadatas
    )

def query(collection, query, k=3):
    return collection.query(query_texts=[query], n_results=k)["documents"][0]

def delete_documents_by_source(collection, source_id: str):
    collection.delete(where={"source_id": source_id})