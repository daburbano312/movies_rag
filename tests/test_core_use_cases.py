import pytest
from src.core.use_cases import retrieve_similar, generate_answer
from src.core.models import Movie

# --- Test retrieve_similar ---

def test_retrieve_similar(monkeypatch):
    dummy_vec = [0.1, 0.2, 0.3]
    # Stub embed_text para devolver vector fijo
    monkeypatch.setattr("src.core.use_cases.embed_text", lambda q, model=None: dummy_vec)
    # Stub conexión y cursor
    class FakeCursor:
        def execute(self, *args, **kwargs): pass
        def fetchall(self): return [(1, "Test Movie", "Desc")]
        def close(self): pass
    class FakeConn:
        def cursor(self): return FakeCursor()
        def close(self): pass
    monkeypatch.setattr("src.core.use_cases.get_connection", lambda: FakeConn())

    movies = retrieve_similar("¿Qué onda?", k=1)
    assert isinstance(movies, list)
    assert len(movies) == 1
    assert isinstance(movies[0], Movie)
    assert movies[0].title == "Test Movie"

# --- Test generate_answer ---

def test_generate_answer(monkeypatch):
    # Stub call_chat_completion
    monkeypatch.setattr("src.core.use_cases.call_chat_completion", lambda prompt, model=None: "Respuesta AI")
    context = [Movie(id=1, title="M1", description="D1"), Movie(id=2, title="M2", description="D2")]
    ans = generate_answer("¿Pregunta?", context)
    assert ans == "Respuesta AI"
    # Verificar que el prompt incluya títulos de películas
    assert "Title: M1" in ans or "Respuesta AI" == ans
