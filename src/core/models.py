# src/core/models.py
from pydantic import BaseModel
from typing import List

class Movie(BaseModel):
    id: int
    title: str
    description: str

class Answer(BaseModel):
    answer: str
    retrieved: List[Movie]
