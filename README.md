# Modular RAG Chatbot

An intelligent Chatbot solution designed to ingest unstructured data (including websites and scanned PDFs) and interact conversationally via a robust Retrieval-Augmented Generation (RAG) architecture.

## 🚀 Features

- **Automated Info Scraping**: Extract and parse available text, PDFs, and links directly from the target website.
- **OCR for Scanned Documents**: Leverage `EasyOCR` and `PyMuPDF` to read and parse scanned, image-based PDF documents, turning legacy materials into searchable text.
- **RAG & Vector Storage**: Utilizes `ChromaDB` for persistent local vector embeddings, ensuring fast and relevant semantic search limits across document chunks.
- **Contextual Memory**: A built-in session memory tracks multi-turn chats to provide intelligent, contextual, human-like answers.
- **FastAPI Endpoints**: Modular scale-ready backend with intuitive REST routes over a legacy script.
- **Premium Frontend UI**: State-of-the-art interactive chatting capability natively bridging to the backend models.

## 🧠 System Workflow

1. **Scraping and Ingestion**: The data source is traversed to download links and attached assets (PDFs, images).
2. **Segmentation**: Large data streams are chunked smartly.
3. **Embedding**: Text streams (and OCR text) are embedded and routed to ChromaDB's vector store.
4. **User Query**: Interaction begins. The user query is passed alongside rolling memory context and localized database results to the designated LLM, which formats an informed answer citing original context.

## 🔧 Installation & Setup

1. **Clone the repository.**
2. **Setup virtual environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r reuirements.txt
   ```
4. **Run Backend Service**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
5. **Open Frontend UI**: Navigate your browser to `frontend/index.html`.

## 📄 Project Documentation
A detailed compilation of the workflow implementation is present in the `project_report.tex` (available in the `backend` folder) which can be directly converted into a PDF report.

---
*Built incrementally from a basic script to a robust modular framework.*
