"""test_deactivate_all.py — proves the emergency stop-all endpoint.

Two things are proven here:
1. One call flips every active agent off, and a second call honestly
   reports 0 (safe to hammer the button).
2. /agents/deactivate-all hits the LITERAL route — it is NOT parsed as
   an {agent_id} path parameter (we assert we got the count object,
   not an agent object or a 422/404 from int-parsing).
"""

from fastapi.testclient import TestClient

from server.main import app


def _create(client, name):
    r = client.post("/agents", json={"name": name})
    assert r.status_code == 201
    return r.json()


def test_deactivate_all_flips_and_counts():
    with TestClient(app) as client:
        # reset first: earlier tests in the session may have left agents on
        client.post("/agents/deactivate-all")

        a1 = _create(client, "stop-all-a")
        a2 = _create(client, "stop-all-b")
        client.post(f"/agents/{a1['id']}/activate")
        client.post(f"/agents/{a2['id']}/activate")

        r = client.post("/agents/deactivate-all")
        assert r.status_code == 200
        assert r.json() == {"deactivated": 2}

        # both really off now, straight from the database via the API
        assert client.get(f"/agents/{a1['id']}").json()["is_active"] is False
        assert client.get(f"/agents/{a2['id']}").json()["is_active"] is False

        # second call: nothing active, honest zero
        r = client.post("/agents/deactivate-all")
        assert r.status_code == 200
        assert r.json() == {"deactivated": 0}


def test_deactivate_all_route_not_parsed_as_agent_id():
    with TestClient(app) as client:
        r = client.post("/agents/deactivate-all")
        # The literal route answered: a count object, NOT an agent object
        # (no id/name keys) and NOT a 404/422 from path parsing.
        assert r.status_code == 200
        body = r.json()
        assert "deactivated" in body
        assert "id" not in body and "name" not in body
