"""test_health.py — proves /health really checks the database.

One test for the happy path, one that breaks the DB connection on purpose
and proves the endpoint answers 503 instead of lying with a 200.
"""

from fastapi.testclient import TestClient

from server.main import app


def test_health_ok_answers_with_real_db_check():
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["db"] == "connected"


def test_health_returns_503_when_db_is_down(monkeypatch):
    def boom():
        raise RuntimeError("database is gone")

    monkeypatch.setattr("server.main.get_connection", boom)
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 503
    assert r.json()["detail"] == "database unavailable"
