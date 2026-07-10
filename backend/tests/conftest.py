"""Shared fixtures for Sprint 7 API tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


def _login(client: TestClient, email: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Access123!"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def passenger_token(client: TestClient) -> str:
    return _login(client, "passenger@access.test")


@pytest.fixture(scope="session")
def auth_headers(passenger_token: str) -> dict:
    return {"Authorization": f"Bearer {passenger_token}"}


@pytest.fixture(scope="session")
def provider_token(client: TestClient) -> str:
    return _login(client, "provider@access.test")


@pytest.fixture(scope="session")
def provider_headers(provider_token: str) -> dict:
    return {"Authorization": f"Bearer {provider_token}"}


@pytest.fixture(scope="session")
def dispatcher_token(client: TestClient) -> str:
    return _login(client, "dispatcher@access.test")


@pytest.fixture(scope="session")
def dispatcher_headers(dispatcher_token: str) -> dict:
    return {"Authorization": f"Bearer {dispatcher_token}"}
