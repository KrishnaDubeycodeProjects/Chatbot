from groq import Groq
from backend.config import GROQ_API_KEY, MODEL_1, MODEL_2
import time

client = Groq(api_key=GROQ_API_KEY)

def generate(query, context, history, model="model1"):
    model_name = MODEL_1 if model == "model1" else MODEL_2

    messages = []

    # 🔹 Add system instruction
    messages.append({
        "role": "system",
        "content": "You are a helpful assistant for TCET college."
    })

    # 🔹 Add previous chat history
    for msg in history:
        messages.append(msg)

    # 🔹 Add context + new question
    messages.append({
        "role": "user",
        "content": f"""
Context:
{context}

Question:
{query}
"""
    })

    start = time.time()

    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )

    latency = time.time() - start

    return response.choices[0].message.content, latency