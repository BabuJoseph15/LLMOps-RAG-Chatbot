import os
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app

client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert (
        data["message"]
        == "Enterprise RAG Chatbot API"
    )


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

    assert data["service"] == "rag-chatbot"


def test_invalid_request():

    response = client.post(
        "/ask",
        json={}
    )

    assert response.status_code == 422
