memory_store = {}

MAX_HISTORY = 5   # keep last 5 messages

def get_history(session_id):
    return memory_store.get(session_id, [])

def add_message(session_id, role, content):
    if session_id not in memory_store:
        memory_store[session_id] = []

    memory_store[session_id].append({
        "role": role,
        "content": content
    })

    # keep only last N messages
    memory_store[session_id] = memory_store[session_id][-MAX_HISTORY:]