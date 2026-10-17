"""test_task_flow.py — proves the task path end-to-end:
activation gate (403 + logged refusal), tool allowlist (denied
without 'echo'), successful echo, and the logs endpoint."""

import pytest
from fastapi.testclient import TestClient

from server.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _agent(client, name, tools=None, activate=True):
    r = client.post("/agents", json={"name": name,
                                     "allowed_tools": tools or []})
    assert r.status_code == 201
    agent = r.json()
    if activate:
        client.post(f"/agents/{agent['id']}/activate")
    return agent


def test_inactive_agent_refused_403_and_logged(client):
    """THE core security test: deactivated agent gets 403,
    and the refusal itself appears in task_logs."""
    agent = _agent(client, "off-agent", activate=False)
    r = client.post(f"/agents/{agent['id']}/tasks", json={"task_text": "hi"})
    assert r.status_code == 403
    task_id = r.json()["detail"]["task_id"]

    logs = client.get(f"/agents/{agent['id']}/logs").json()
    refusal = [l for l in logs if l["task_id"] == task_id]
    assert len(refusal) == 1
    assert refusal[0]["step"] == "activation_check"
    assert refusal[0]["status"] == "rejected"
    # nothing ran after the gate
    assert all(l["step"] == "activation_check" for l in refusal)


def test_active_agent_with_echo_tool_completes(client):
    agent = _agent(client, "echoer", tools=["echo"])
    r = client.post(f"/agents/{agent['id']}/tasks", json={"task_text": "hello"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "completed"
    assert body["output"] == "echo: hello"

    logs = client.get(f"/agents/{agent['id']}/logs").json()
    steps = [(l["step"], l["status"]) for l in logs if l["task_id"] == body["task_id"]]
    assert steps == [("activation_check", "ok"), ("tool_call:echo", "ok")]


def test_active_agent_without_tool_denied(client):
    """allowed_tools=[] (the default) -> runner refuses the echo tool."""
    agent = _agent(client, "bare", tools=[])
    r = client.post(f"/agents/{agent['id']}/tasks", json={"task_text": "hi"})
    # The request itself is well-formed, so it returns 200...
    assert r.status_code == 200
    # ...but the tool call inside was denied: no tools are allowed.
    assert r.json()["status"] == "rejected"

    logs = client.get(f"/agents/{agent['id']}/logs").json()
    assert any(l["step"] == "tool_denied" and l["status"] == "rejected"
               for l in logs)


def test_unknown_agent_404(client):
    r = client.post("/agents/999999/tasks", json={"task_text": "hi"})
    assert r.status_code == 404


def test_empty_task_text_422(client):
    agent = _agent(client, "picky")
    r = client.post(f"/agents/{agent['id']}/tasks", json={"task_text": ""})
    assert r.status_code == 422


def test_oversized_task_text_422(client):
    agent = _agent(client, "picky2")
    r = client.post(f"/agents/{agent['id']}/tasks", json={"task_text": "x" * 4001})
    assert r.status_code == 422


def test_unknown_field_in_task_rejected(client):
    agent = _agent(client, "picky3")
    r = client.post(f"/agents/{agent['id']}/tasks",
                    json={"task_text": "hi", "use_tools": ["echo"]})
    assert r.status_code == 422  # can't smuggle tools past the API
