from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_productive_text():
    response = client.post(
        "/api/analyze",
        data={"text": "Qual o status do chamado 123? Não consigo acessar o sistema."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["category"] == "Produtivo"
    assert "Recebemos sua mensagem" in payload["suggested_reply"]
