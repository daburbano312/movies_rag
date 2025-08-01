# src/interfaces/api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import time

from ..core.use_cases import retrieve_similar, generate_answer
from ..core.models import Answer, Movie


# ----------------------------
# Modelos de petición y respuesta
# ----------------------------

class AskRequest(BaseModel):
    question: str


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: Optional[str]
    messages: List[Message]
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = 512
    # Si el frontend envía `stream`, lo aceptamos y lo ignoramos (no hacemos streaming)
    stream: Optional[bool] = False


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    id: str
    object_: str = Field(alias="object", default="chat.completion")
    created: int
    model: Optional[str]
    choices: List[Choice]
    usage: Usage

    class Config:
        allow_population_by_field_name = True


# ----------------------------
# Inicializar FastAPI y CORS
# ----------------------------

app = FastAPI(title="Movies RAG Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Endpoint original /ask
# ----------------------------

@app.post("/ask", response_model=Answer)
async def ask(req: AskRequest):
    """
    Devuelve la respuesta RAG y la lista de películas recuperadas.
    """
    try:
        movies = retrieve_similar(req.question)
        resp = generate_answer(req.question, movies)
        return Answer(answer=resp, retrieved=movies)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Endpoint OpenAI-compat /v1/chat/completions
# ----------------------------

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(req: ChatRequest):
    """
    Adaptador compatible con OpenAI Chat Completions API,
    para que la Chat UI de HuggingFace lo consuma directamente.
    """
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    try:
        # Extraer última entrada de usuario
        user_text = req.messages[-1].content

        # Flujo RAG
        movies: List[Movie] = retrieve_similar(user_text, k=5)
        answer_text: str = generate_answer(user_text, movies)

        # Timestamp
        ts = int(time.time())

        # Construir resultado
        choice = Choice(
            index=0,
            message=Message(role="assistant", content=answer_text),
            finish_reason="stop"
        )

        # Para permitir al UI mostrar algo de uso, devolvemos cero tokens
        usage = Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

        return ChatResponse(
            id=f"movies-rag-{ts}",
            object_="chat.completion",
            created=ts,
            model=req.model,
            choices=[choice],
            usage=usage
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
