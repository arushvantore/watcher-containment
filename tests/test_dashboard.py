"""test_dashboard.py — the dashboard is actually served at the root URL."""

from fastapi.testclient import TestClient

from server.main import app


def test_root_serves_dashboard_html():
    with TestClient(app) as client:
        r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "WATCHER" in r.text
