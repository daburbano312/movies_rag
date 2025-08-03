# scripts/index_movies.py

import os
import csv
import time
import psycopg2
from dotenv import load_dotenv
from openai import OpenAI
from pgvector.psycopg2 import register_vector

# ─── Carga variables de entorno ────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
DATABASE_URL    = os.getenv("DATABASE_URL")
MOVIES_CSV_PATH = os.getenv("MOVIES_CSV_PATH", "movies-dataset.csv")

if not OPENAI_API_KEY or not DATABASE_URL:
    raise RuntimeError("Define OPENAI_API_KEY y DATABASE_URL en .env")

client = OpenAI(api_key=OPENAI_API_KEY)

def wait_for_db(url: str, timeout: int = 30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            conn = psycopg2.connect(url)
            conn.close()
            return
        except psycopg2.OperationalError:
            print("– esperando a que PostgreSQL arranque…")
            time.sleep(1)
    raise RuntimeError("PostgreSQL no respondió en tiempo")

def init_db(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id          SERIAL PRIMARY KEY,
                title       TEXT    NOT NULL,
                description TEXT    NOT NULL,
                embedding   VECTOR(1536) NOT NULL
            );
        """)
    conn.commit()

def pick_fields(fieldnames: list[str]) -> tuple[str,str]:
    """
    Devuelve (title_key, desc_key) eligiendo de entre fieldnames
    comparando con sets de nombres comunes.
    """
    title_guesses = {"title", "movie_title", "name", "titulo", "film"}
    desc_guesses  = {"plot", "description", "overview", "synopsis", "argumento"}

    # Encuentra la primera coincidencia en cada set
    title_key = next((f for f in fieldnames if f.lower() in title_guesses), None)
    desc_key  = next((f for f in fieldnames if f.lower() in desc_guesses),  None)

    # Si no hay coincidencia, toma las dos primeras columnas
    if title_key is None:
        title_key = fieldnames[0]
    if desc_key is None:
        # si la segunda columna es igual al título, busca otra, sino usa la segunda
        desc_key = fieldnames[1] if len(fieldnames) > 1 and fieldnames[1] != title_key else fieldnames[0]

    print(f"🔑 Usando campo TITLE   = '{title_key}'")
    print(f"🔑 Usando campo DESC    = '{desc_key}'")
    return title_key, desc_key

def index_movies(csv_path: str):
    # Verifica existencia del CSV
    print(f"📂 Path CSV: {csv_path}")
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"No existe el archivo CSV en '{csv_path}'")

    # Lee todo y detecta campos
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader     = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows       = list(reader)

    print(f"📝 Columnas detectadas: {fieldnames}")
    print(f"🔢 Filas totales:       {len(rows)}")

    title_key, desc_key = pick_fields(fieldnames)

    if not rows:
        print("⚠️ El CSV no contiene filas.")
        return

    # Prepara la BD
    wait_for_db(DATABASE_URL)
    conn = psycopg2.connect(DATABASE_URL)
    init_db(conn)
    register_vector(conn)

    inserted = 0
    with conn.cursor() as cur:
        for i, row in enumerate(rows, start=1):
            title       = row.get(title_key, "").strip()
            description = row.get(desc_key,  "").strip()

            if not title or not description:
                print(f"  – Fila {i}: omitida (title='{title}', desc_len={len(description)})")
                continue

            # Solo muestro un ejemplo
            if inserted == 0:
                print(f"  📌 Ejemplo Fila {i}: title='{title[:30]}...', desc_len={len(description)}")

            # 🔹 Embedding v1+
            resp = client.embeddings.create(
                model="text-embedding-3-small",
                input=description
            )
            vector = resp.data[0].embedding

            cur.execute(
                "INSERT INTO movies (title, description, embedding) VALUES (%s, %s, %s);",
                (title, description, vector)
            )
            inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ Indexación completada. Total insertadas: {inserted}")

if __name__ == "__main__":
    index_movies(MOVIES_CSV_PATH)
