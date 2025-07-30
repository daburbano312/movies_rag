# src/infrastructure/openai_client.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Cliente de Chat completions
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_chat_completion(prompt: str, model: str = "gpt-4") -> str:
    """
    Envía el prompt a OpenAI ChatCompletion y devuelve el contenido de la respuesta.
    """
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",  "content": "Eres un asistente experto en cine de los 80."},
            {"role": "user",    "content": prompt}
        ],
        temperature=0.2,
        max_tokens=512
    )
    return resp.choices[0].message.content.strip()
