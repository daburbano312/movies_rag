import pytest
from src.infrastructure.embeddings import embed_text, client

class DummyData:
    def __init__(self, embedding):
        self.embedding = embedding

class DummyResp:
    def __init__(self, vector):
        self.data = [DummyData(vector)]

def test_embed_text(monkeypatch):
    dummy_vector = [0.5, 0.6, 0.7]
    # Stub create de embeddings
    monkeypatch.setattr(client.embeddings, "create", lambda model, input: DummyResp(dummy_vector))
    result = embed_text("texto de prueba")
    assert result == dummy_vector
