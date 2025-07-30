# src/core/use_cases.py

from typing import List
from .models import Movie
from ..infrastructure.db import get_connection
from ..infrastructure.embeddings import embed_text
from ..infrastructure.openai_client import call_chat_completion

def retrieve_similar(question: str, k: int = 5) -> List[Movie]:
    """
    1. Calcula embedding de la pregunta (lista de floats).
    2. Abre conexión (con vector adapter registrado).
    3. Ejecuta SQL con CAST explícito: ARRAY[...]::vector
    """
    q_vec = embed_text(question)      # → Python list[float]
    conn  = get_connection()
    cur   = conn.cursor()

    cur.execute(
        """
        SELECT id, title, description
          FROM movies
         ORDER BY embedding <#> %s::vector
         LIMIT %s
        """,
        (q_vec, k)
    )
    rows = cur.fetchall()
    conn.close()
    return [Movie(**row) for row in rows]

def generate_answer(question: str, context: List[Movie]) -> str:
    """
    Monta prompt con los contextos y llama a OpenAI.
    """
    snippet = "\n\n".join(
        f"Title: {m.title}\nDescription: {m.description}"
        for m in context
    )
    prompt = (
        "A continuación tienes descripciones de películas de los 80:\n"
        f"{snippet}\n\n"
        f"Pregunta: {question}\n"
        "Responde de forma clara y concisa, usando SOLO la información proporcionada."
    )
    return call_chat_completion(prompt)
