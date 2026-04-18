from fastapi import APIRouter, File, UploadFile, BackgroundTasks, Form, HTTPException
from pydantic import BaseModel
import os
import threading

from backend.database import add_source, get_sources, delete_source, update_source_status, get_source
from backend.rag.scraper import crawl_website
from backend.rag.chunker import TextChunker, is_valid_page
from backend.rag.chroma_store import get_collection, add_documents, delete_documents_by_source
from backend.rag.pdf_parser import parse_pdf_bytes

router = APIRouter()
processing_lock = threading.Lock()

class AddUrlRequest(BaseModel):
    url: str
    name: str = "Unknown"
    site: str = "tcet_main"

@router.get("/sources")
def list_sources():
    sources = get_sources()
    return {"sources": sources}

def process_url_background(source_id: str, url: str, site: str):
    with processing_lock:
        try:
            print(f"🚀 Started background processing for URL source {source_id}: {url}")
            pages = crawl_website(url, max_pages=1) # only scrape the given URL
            text_content = ""
            for p in pages:
                text_content += p.text + "\n"
                
            chunker = TextChunker(chunk_size=500, overlap=50)
            chunks = [c for c in chunker.chunk(text_content) if len(c.strip()) > 50]
            
            if chunks:
                collection = get_collection(site)
                add_documents(collection, chunks, source_id=source_id)
                update_source_status(source_id, "completed", len(chunks))
                print(f"✅ Source {source_id} processed successfully. {len(chunks)} chunks added.")
            else:
                update_source_status(source_id, "failed", 0)
                print(f"⚠️ No valid text found for {url}")
        except Exception as e:
            update_source_status(source_id, "failed", 0)
            print(f"❌ Error processing URL {url}: {str(e)}")

@router.post("/url")
def add_url_source(req: AddUrlRequest, background_tasks: BackgroundTasks):
    # Add to DB first
    source_id = add_source("url", req.url, req.name, req.site)
    
    # Process in background
    background_tasks.add_task(process_url_background, source_id, req.url, req.site)
    
    return {"message": "URL added successfully", "source_id": source_id, "status": "processing"}

def process_pdf_background(source_id: str, pdf_bytes: bytes, filename: str, site: str):
    with processing_lock:
        try:
            print(f"🚀 Started background processing for PDF source {source_id}: {filename}")
            text_content = parse_pdf_bytes(pdf_bytes)
            
            chunker = TextChunker(chunk_size=500, overlap=50)
            chunks = [c for c in chunker.chunk(text_content) if len(c.strip()) > 50]
            
            if chunks:
                collection = get_collection(site)
                add_documents(collection, chunks, source_id=source_id)
                update_source_status(source_id, "completed", len(chunks))
                print(f"✅ Source {source_id} processed successfully. {len(chunks)} chunks added.")
            else:
                if not text_content.strip():
                    update_source_status(source_id, "failed (No extractable text)", 0)
                    print(f"⚠️ No extractable text found in {filename}")
                else:
                    update_source_status(source_id, "failed (Text too short)", 0)
                    print(f"⚠️ Text found in {filename} but it was too short to chunk.")
        except Exception as e:
            update_source_status(source_id, f"error: {str(e)[:20]}", 0)
            print(f"❌ Error processing PDF {filename}: {str(e)}")

@router.post("/pdf")
async def add_pdf_source(background_tasks: BackgroundTasks, file: UploadFile = File(...), name: str = Form(...), site: str = Form(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    pdf_bytes = await file.read()
    
    # Add to DB
    source_id = add_source("pdf", file.filename, name, site)
    
    # Process in background
    background_tasks.add_task(process_pdf_background, source_id, pdf_bytes, file.filename, site)
    
    return {"message": "PDF added successfully", "source_id": source_id, "status": "processing"}

@router.delete("/{source_id}")
def delete_source_endpoint(source_id: str):
    try:
        source = get_source(source_id)
        if source:
            collection = get_collection(source["site"])
            delete_documents_by_source(collection, source_id)
        
        # Delete from DB
        delete_source(source_id)
        
        return {"message": "Source deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))