import os
from dotenv import load_dotenv
from groq import Groq
from backend.rag.memory import get_history

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_answer(session_id: str, query: str, context_chunks: list):
    """
    Generates an answer using Groq by combining:
    - Context (from Chroma DB)
    - Memory (Chat history)
    - User Query
    """
    # 1. Prepare Context
    context_text = "\n\n".join(context_chunks) if context_chunks else "No relevant document context found."

    # 2. Prepare Memory
    history = get_history(session_id)
    history_text = ""
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"
    
    if not history_text:
        history_text = "No previous conversation."

    # 3. Construct System Prompt
    system_prompt = f"""You are a helpful, human-like AI assistant for the TCET (Thakur College of Engineering and Technology) website.
Be conversational, polite, and clear. 
Always base your factual answers upon the provided Context. If the context does not contain the answer, politely say you don't know based on the website.

--- PREVIOUS CONVERSATION (Memory) ---
{history_text}

--- RELEVANT CONTEXT (From Website) ---
{context_text}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.3
    )

    return response.choices[0].message.content
