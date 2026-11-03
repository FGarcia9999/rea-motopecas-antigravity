import pytest
from fastapi.testclient import TestClient
from app.main import make_app

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MOTO_DB_PATH", str(tmp_path / "shop.db"))
    with TestClient(make_app()) as c:
        yield c
