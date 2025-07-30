# Movies-RAG

Un microservicio RAG (Retrieval-Augmented Generation) para responder preguntas sobre descripciones de películas de los 80, usando PostgreSQL+pgvector y la API de OpenAI.

---

## 📋 Contenido

- `scripts/index_movies.py` → indexa tu CSV en la BD
- `src/`  
  - `infrastructure/` → conexión BD, embeddings y cliente OpenAI  
  - `core/`           → modelos y casos de uso  
  - `interfaces/`     → API FastAPI  
  - `presentation/`   → arranque con Uvicorn  
- `tests/` → pruebas unitarias e integración
- `docker-compose.yml` + `Dockerfile` → orquestación y despliegue
- `.env.example` → variables de entorno de ejemplo

---

## 🚀 Requisitos

- Docker & Docker Compose (opcional para contenedor de PostgreSQL)
- Python 3.9+
- Cuenta de OpenAI con API Key

---

## ⚙️ Instalación local

1. Clona el repositorio  
   ```bash
   git clone <tu-repo-url>
   cd Movies-RAG
