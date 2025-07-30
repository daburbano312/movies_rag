# src/interfaces/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ..core.use_cases import retrieve_similar, generate_answer
from ..core.models import Movie, Answer

class AskRequest(BaseModel):
    question: str

app = FastAPI(title="Movies RAG Service")

@app.post("/ask", response_model=Answer)
async def ask(req: AskRequest):
    try:
        movies = retrieve_similar(req.question)
        resp   = generate_answer(req.question, movies)
        return Answer(answer=resp, retrieved=movies)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
