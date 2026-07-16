import os

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
MODEL = os.getenv("MODEL")

assert API_TOKEN, "API_TOKEN .env'de tanimli olmali"
assert BASE_URL, "BASE_URL .env'de tanimli olmali"
assert MODEL, "MODEL .env'de tanimli olmali"


@pytest.fixture
def client():
    with httpx.Client(timeout=60.0) as c:
        yield c


def test_models_list(client):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    resp = client.get(f"{BASE_URL}/models", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    model_ids = [m["id"] for m in data["data"]]
    assert MODEL in model_ids, f"{MODEL} model listesinde bulunamadi: {model_ids}"


def test_chat_completion(client):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Iki kelimeyle selam ver."}],
        "temperature": 0.7,
        "stream": False,
    }
    resp = client.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    msg = data["choices"][0].get("message", {})
    assert "content" in msg
    assert len(msg["content"]) > 0


def test_invalid_model_returns_404(client):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "nonexistent-model-12345",
        "messages": [{"role": "user", "content": "test"}],
        "stream": False,
    }
    resp = client.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
    assert resp.status_code == 404


def test_invalid_token_returns_401(client):
    headers = {
        "Authorization": "Bearer invalid_token_123",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "test"}],
        "stream": False,
    }
    resp = client.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
    assert resp.status_code == 401
