from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
import sys
import os

# Allow Python to find the 'backend' module when running from VSCode's "Run" button
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our custom modules
from backend.rag.scraper import crawl_website
from backend.rag.chunker import TextChunker, is_valid_page
from backend.rag.chroma_store import get_collection, add_documents, query as chroma_query
from backend.rag.memory import add_message
from backend.rag.llm import generate_answer
from backend.admin.routes import router as admin_router

app = FastAPI(title="TCET Chatbot API")

# Setup CORS to allow the frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admin")


# Collections are now loaded dynamically per request.

# Mutex to ensure single scraping at a time
scraping_lock = threading.Lock()

class ChatRequest(BaseModel):
    query_text: str
    session_id: str
    site: str = "tcet_main"
    model: str = "model1"

class ScrapeRequest(BaseModel):
    url: str
    max_pages: int = 5

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        collection = get_collection(req.site)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database not initialized properly: {e}")
    
    # 1. Retrieve Context from ChromaDB
    try:
        # Chroma query expects string, we return list of strings
        context_docs = chroma_query(collection, req.query_text, k=3)
        # chroma returns a list of results, we just take the nearest 3
        if isinstance(context_docs, list) and len(context_docs) > 0:
            if isinstance(context_docs[0], list): # sometimes chroma returns list of lists
                context_chunks = context_docs[0]
            else:
                context_chunks = context_docs
        else:
            context_chunks = []
    except Exception as e:
        print(f"Chroma Error: {e}")
        context_chunks = []

    # 2. Append User Query to Memory
    add_message(req.session_id, "user", req.query_text)

    # 3. Generate Answer
    try:
        answer = generate_answer(req.session_id, req.query_text, context_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 4. Append Bot Answer to Memory
    add_message(req.session_id, "assistant", answer)

    return {"answer": answer, "session_id": req.session_id}

@app.post("/scrape")
async def scrape_endpoint(req: ScrapeRequest, background_tasks: BackgroundTasks):
    if scraping_lock.locked():
        return {"status": "Scraping is already in progress. Please wait."}
    
    background_tasks.add_task(run_scraper, req.url, req.max_pages)
    return {"status": "Scraping started in the background."}

def run_scraper(url: str, max_pages: int):
    with scraping_lock:
        print(f"🚀 Starting scraper for {url} with max_pages {max_pages}")
        pages = crawl_website(url, max_pages=max_pages)
        
        chunker = TextChunker(chunk_size=500, overlap=50)
        all_chunks = []
        
        for page in pages:
            if not is_valid_page(page.text):
                continue
            chunks = [c for c in chunker.chunk(page.text) if len(c.strip()) > 50]
            all_chunks.extend(chunks)
            
        if all_chunks:
            print(f"📦 Storing {len(all_chunks)} chunks to ChromaDB (tcet_docs)...")
            col = get_collection("tcet_docs")
            add_documents(col, all_chunks)
            print("✅ Storage complete.")
        else:
            print("⚠️ No valid chunks found to store.")

if __name__ == "__main__":
    import uvicorn
    # This allows you to just type `python backend/main.py` to start the server!
    print("🚀 Starting FastAPI server on http://127.0.0.1:8000")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)