# src/infrastructure/embeddings.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Cliente de embeddings
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_text(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """
    Retorna el vector embedding para el texto dado.
    """
    resp = client.embeddings.create(
        model=model,
        input=text
    )
    return resp.data[0].embedding
