from fastapi.testclient import TestClient
import pytest
from src.interfaces.api import app
from src.core.models import Movie

@pytest.fixture(autouse=True)
def stub_core(monkeypatch):
    # Stub retrieve_similar y generate_answer
    monkeypatch.setattr(
        "src.core.use_cases.retrieve_similar",
        lambda q, k=5: [Movie(id=1, title="M1", description="D1")]
    )
    monkeypatch.setattr(
        "src.core.use_cases.generate_answer",
        lambda q, c: "Respuesta de prueba"
    )

def test_ask_endpoint():
    client = TestClient(app)
    response = client.post("/ask", json={"question": "¿Hola?"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Respuesta de prueba"
    assert isinstance(data["retrieved"], list)
    assert data["retrieved"][0]["title"] == "M1"
