import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


def test_root():

    response = client.get("/")

    assert response.status_code == 200


def test_metrics():

    response = client.get("/metrics")

    assert response.status_code == 200
