import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "sources.db")

def _get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            source_path TEXT NOT NULL,
            status TEXT NOT NULL,
            chunks_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Safely migrate existing tables
    try:
        cursor.execute("ALTER TABLE sources ADD COLUMN name TEXT DEFAULT 'Unknown'")
        cursor.execute("ALTER TABLE sources ADD COLUMN site TEXT DEFAULT 'tcet_main'")
    except sqlite3.OperationalError:
        pass # Columns already exist
        
    conn.commit()
    conn.close()

def add_source(source_type: str, source_path: str, name: str = "Unknown", site: str = "tcet_main") -> str:
    conn = _get_connection()
    cursor = conn.cursor()
    source_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO sources (id, type, source_path, name, site, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (source_id, source_type, source_path, name, site, 'processing', datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return source_id

def update_source_status(source_id: str, status: str, chunks_count: int = 0):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sources SET status = ?, chunks_count = ? WHERE id = ?",
        (status, chunks_count, source_id)
    )
    conn.commit()
    conn.close()

def get_sources():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, source_path, name, site, status, chunks_count, created_at FROM sources ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_source(source_id: str):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_source(source_id: str):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
