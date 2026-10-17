"""test_quarantine.py — proves quarantine is a real flag set only by the
deliberate action, and that the server refuses tasks for quarantined agents.
"""

from fastapi.testclient import TestClient

from server.main import app


def _create_active(client, name):
    r = client.post("/agents",
                    json={"name": name, "allowed_tools": ["echo"]})
    assert r.status_code == 201
    agent = r.json()
    r = client.post(f"/agents/{agent['id']}/activate")
    assert r.status_code == 200
    return r.json()


def test_quarantine_flag_only_changes_via_action():
    with TestClient(app) as client:
        agent = _create_active(client, "flag-check")
        # new agents are not quarantined
        assert agent["quarantined"] is False

        # deliberate action sets it
        r = client.post(f"/agents/{agent['id']}/quarantine")
        assert r.status_code == 200
        assert r.json()["quarantined"] is True

        # release action clears it
        r = client.post(f"/agents/{agent['id']}/unquarantine")
        assert r.status_code == 200
        assert r.json()["quarantined"] is False

        # unknown agent -> 404 on both actions
        assert client.post("/agents/999999/quarantine").status_code == 404
        assert client.post("/agents/999999/unquarantine").status_code == 404


def test_quarantined_agent_refused_403_and_logged():
    with TestClient(app) as client:
        agent = _create_active(client, "red-gate")
        r = client.post(f"/agents/{agent['id']}/quarantine")
        assert r.json()["quarantined"] is True

        # still is_active=1 — quarantine must win anyway
        r = client.post(f"/agents/{agent['id']}/tasks",
                        json={"task_text": "should never run"})
        assert r.status_code == 403
        detail = r.json()["detail"]
        assert detail["message"] == "agent is quarantined; task refused"
        task_id = detail["task_id"]

        # the refusal is in the audit trail
        logs = client.get(f"/agents/{agent['id']}/logs").json()
        rows = [l for l in logs if l["task_id"] == task_id]
        assert rows, "refusal must be logged"
        assert rows[0]["step"] == "quarantine_check"
        assert rows[0]["status"] == "rejected"

        # released -> task runs again
        client.post(f"/agents/{agent['id']}/unquarantine")
        r = client.post(f"/agents/{agent['id']}/tasks",
                        json={"task_text": "echo back"})
        assert r.status_code == 200
        assert r.json()["status"] == "completed"
