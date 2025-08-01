# Movies RAG Service

Sistema Retrieval-Augmented Generation (RAG) para responder preguntas sobre películas de los años 80, usando **FastAPI**, **PostgreSQL** (con extensión **pgvector**) y la API de **OpenAI** integradas bajo una Arquitectura Limpia.

---

## 📦 Requisitos Previos

- **Python 3.10+**
- **Docker** & **Docker Compose** (opcional)
- **Terraform** (para desplegar infraestructura AWS)
- Cuenta en **AWS** con permisos para ECR, ECS, RDS, IAM, VPC.
- Clave de API de OpenAI (`OPENAI_API_KEY`).

---

## 📁 Estructura del Proyecto

```
movies-rag/
├── infra/                  # Infraestructura como código
│   └── terraform/          # Archivos Terraform
│       ├── provider.tf
│       ├── variables.tf
│       ├── networking.tf
│       ├── rds.tf
│       ├── ecr_ecs.tf
│       ├── alb_service.tf
│       └── outputs.tf
├── src/                    # Código de la aplicación
│   ├── core/               # Entidades y casos de uso (lógica de negocio)
│   ├── infrastructure/     # Acceso a datos (Embeddings, BBDD, OpenAI client)
│   ├── interfaces/         # API FastAPI y esquemas Pydantic
│   └── presentation/       # (si aplica: dashboard, UI)
├── tests/                  # Pruebas unitarias y de aceptación
├── frontend/               # Integración con HuggingFace Chat UI
│   └── chat-ui/            # SvelteKit + Chat UI
├── deploy/                 # Diagramas y archivos de ayuda
│   └── aws_diagram.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md               # ← Este archivo
```

---

## 🚀 Instalación y Arranque Local

1. **Clona el repositorio**

   ```bash
   git clone <url-del-repo>
   cd movies-rag
   ```

2. **Configura el entorno virtual**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Crea el archivo**`` a partir de `.env.example`:

   ```bash
   cp .env.example .env
   ```

   Edita `.env` y rellena tus credenciales:

   ```dotenv
   OPENAI_API_KEY=<tu_api_key>
   DATABASE_URL=postgresql://user:password@localhost:5432/movies
   MOVIES_CSV_PATH=/ruta/a/movies-dataset.csv
   ```

4. **Levanta servicios con Docker Compose** (opcional):

   ```bash
   docker-compose up -d
   ```

5. **Indexa las películas**:

   ```bash
   python scripts/index_movies.py
   ```

6. **Arranca la API**:

   ```bash
   uvicorn src.interfaces.api:app --reload --port 8000
   ```

7. **Ejecuta pruebas**:

   ```bash
   pytest --cov
   ```

---

## 🌐 Integración Frontend (HuggingFace Chat UI)

1. **Clona el UI**

   ```bash
   git clone https://github.com/huggingface/chat-ui.git frontend/chat-ui
   cd frontend/chat-ui
   npm install
   ```

2. **Configura**``

   ```dotenv
   MODELS=`[
     {
       "name": "movie-rag",
       "displayName": "Movie RAG QA",
       "id": "movie-rag",
       "description": "Preguntas sobre películas de los 80",
       "parameters": { "temperature": 0, "max_tokens": 512 },
       "endpoints": [
         { "type": "openai", "baseURL": "http://localhost:8000/v1" }
       ]
     }
   ]`
   OPENAI_API_KEY=<tu_api_key>
   ```

3. **Proxy en**`` (ya incluido en este repo):

   ```ts
   server: {
     proxy: {
       "/v1": {
         target: "http://localhost:8000",
         changeOrigin: true,
         rewrite: (path) => path.replace(/^\/v1/, "/v1"),
       },
     },
   },
   ```

4. **Arranca el frontend**:

   ```bash
   npm run dev
   ```

5. **Visita** `http://localhost:5173` y selecciona **Movie RAG QA**.

---

## 🏗️ Infraestructura AWS con Terraform

Desde `infra/terraform/`:

```bash
terraform init
terraform plan -var-file=../../deploy/terraform.tfvars
terraform apply -var-file=../../deploy/terraform.tfvars
```

Archivos principales:

- **provider.tf**: Configuración del provider AWS.
- **variables.tf**: Variables (región, credenciales, API Key).
- **networking.tf**: VPC, subnets, Security Groups.
- **rds.tf**: Instancia RDS PostgreSQL.
- **ecr\_ecs.tf**: Repositorio ECR, Cluster ECS, Task Definition.
- **alb\_service.tf**: ALB, Target Group, Listener, ECS Service.
- **outputs.tf**: DNS del ALB y endpoint RDS.

Consulta `deploy/aws_diagram.md` para un diagrama detallado de despliegue.

---

## 📚 Diagramas y Documentación

- ``: Diagrama PlantUML de infraestructura AWS.
- ``: Diagrama PlantUML de Arquitectura Limpia.

---

## 🙌 Contribuciones

Para mejoras, haz **fork** y **pull request**. Sigue las buenas prácticas: tests, linting y documentación actualizada.



