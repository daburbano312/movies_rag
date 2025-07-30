# src/infrastructure/db.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

# ─── 0️⃣ Carga .env ─────────────────────────────────────────────────────────
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Define DATABASE_URL en tu .env")

def get_connection():
    """
    Devuelve una conexión psycopg2 con:
      - RealDictCursor para filas como dicts.
      - pgvector registrado para mapear Python lists a parámetros SQL.
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    register_vector(conn)
    return conn
