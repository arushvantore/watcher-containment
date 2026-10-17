"""test_activation.py — proves activation is enforced SERVER-SIDE.

Uses FastAPI's TestClient: real app, real routes, real SQLite —
but no network and no separate server process.
"""

import pytest
from fastapi.testclient import TestClient

from server.main import app


@pytest.fixture()
def client():
    """A TestClient whose lifespan runs (init_db) on enter, stops on exit."""
    with TestClient(app) as c:
        yield c


def _create(client, name="helper-bot"):
    r = client.post("/agents", json={"name": name})
    assert r.status_code == 201
    return r.json()


def test_new_agent_starts_inactive(client):
    agent = _create(client, "sleeper")
    assert agent["is_active"] is False


def test_activate_then_deactivate(client):
    agent = _create(client, "flipper")
    r = client.post(f"/agents/{agent['id']}/activate")
    assert r.status_code == 200
    assert r.json()["is_active"] is True

    r = client.post(f"/agents/{agent['id']}/deactivate")
    assert r.status_code == 200
    assert r.json()["is_active"] is False


def test_activation_persists_in_database(client):
    """Re-fetching from the DB must show the new state (not just the response)."""
    agent = _create(client, "persister")
    client.post(f"/agents/{agent['id']}/activate")
    r = client.get(f"/agents/{agent['id']}")
    assert r.json()["is_active"] is True


def test_unknown_agent_404(client):
    assert client.get("/agents/999999").status_code == 404
    assert client.post("/agents/999999/activate").status_code == 404


def test_duplicate_name_409(client):
    _create(client, "twin")
    r = client.post("/agents", json={"name": "twin"})
    assert r.status_code == 409


def test_empty_name_rejected(client):
    r = client.post("/agents", json={"name": ""})
    assert r.status_code == 422


def test_oversized_name_rejected(client):
    r = client.post("/agents", json={"name": "x" * 101})
    assert r.status_code == 422


def test_unknown_field_rejected(client):
    r = client.post("/agents", json={"name": "sneaky", "is_active": True})
    assert r.status_code == 422  # extra='forbid' — can't self-activate at create


def test_dangerous_tool_name_rejected(client):
    """Shell-looking strings like 'Rm -rf' must fail tool-name validation."""
    r = client.post("/agents", json={"name": "badder", "allowed_tools": ["Rm -rf"]})
    assert r.status_code == 422


def test_default_tools_empty(client):
    agent = _create(client, "toolless")
    assert agent["allowed_tools"] == []
