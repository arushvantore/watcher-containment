"""main.py — the FastAPI app: routes, error mapping, startup.

The server binds to 127.0.0.1 ONLY (hardcoded below). It is never
reachable from other machines or the internet.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .db import init_db, get_connection
from .models import AgentCreate, AgentOut, TaskSubmit, TaskResultOut, TaskLogOut
from .models import HealthOut, DeactivateAllOut
from . import registry
from . import tasks as tasksvc


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once when the server starts / stops."""
    init_db()  # create tables if missing
    yield      # server is now running
    # (nothing to clean up in v1)


app = FastAPI(
    title="Agent Platform",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthOut)
def health():
    """Real checkup: runs SELECT 1 against the actual database.
    200 + "ok" only if the DB answers; 503 if it doesn't."""
    try:
        conn = get_connection()
        try:
            conn.execute("SELECT 1").fetchone()
        finally:
            conn.close()
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return HealthOut(status="ok", db="connected")


@app.get("/agents", response_model=list[AgentOut])
def list_agents():
    """List all agents."""
    return registry.list_agents()


@app.post("/agents", response_model=AgentOut, status_code=201)
def create_agent(body: AgentCreate):
    """Create a new agent (starts deactivated)."""
    try:
        return registry.create_agent(body)
    except registry.AgentAlreadyExists as e:
        raise HTTPException(status_code=409, detail=f"agent name already exists: {e}")


# Literal path — registered BEFORE the {agent_id} routes on purpose so it
# can never be swallowed by path-parameter parsing (proven by a test).
@app.post("/agents/deactivate-all", response_model=DeactivateAllOut)
def deactivate_all_agents():
    """Emergency stop: turn off every active agent in one call."""
    return DeactivateAllOut(deactivated=registry.deactivate_all())


@app.get("/agents/{agent_id}", response_model=AgentOut)
def get_agent(agent_id: int):
    """Fetch one agent by id."""
    try:
        return registry.get_agent(agent_id)
    except registry.AgentNotFound:
        raise HTTPException(status_code=404, detail="agent not found")


@app.post("/agents/{agent_id}/activate", response_model=AgentOut)
def activate_agent(agent_id: int):
    """Server-side activation: sets is_active=1 in the DATABASE."""
    try:
        return registry.set_agent_active(agent_id, active=True)
    except registry.AgentNotFound:
        raise HTTPException(status_code=404, detail="agent not found")


@app.post("/agents/{agent_id}/deactivate", response_model=AgentOut)
def deactivate_agent(agent_id: int):
    """Server-side deactivation: sets is_active=0 in the DATABASE."""
    try:
        return registry.set_agent_active(agent_id, active=False)
    except registry.AgentNotFound:
        raise HTTPException(status_code=404, detail="agent not found")


@app.post("/agents/{agent_id}/quarantine", response_model=AgentOut)
def quarantine_agent(agent_id: int):
    """DELIBERATE quarantine action — the only way quarantined becomes true.
    A quarantined agent refuses all tasks (403), even if is_active=1."""
    try:
        return registry.set_agent_quarantined(agent_id, quarantined=True)
    except registry.AgentNotFound:
        raise HTTPException(status_code=404, detail="agent not found")


@app.post("/agents/{agent_id}/unquarantine", response_model=AgentOut)
def unquarantine_agent(agent_id: int):
    """Release from quarantine (symmetric with the quarantine action)."""
    try:
        return registry.set_agent_quarantined(agent_id, quarantined=False)
    except registry.AgentNotFound:
        raise HTTPException(status_code=404, detail="agent not found")


@app.post("/agents/{agent_id}/tasks", response_model=TaskResultOut)
def submit_task(agent_id: int, body: TaskSubmit):
    """Submit a task. 404 unknown agent; 403 if agent is deactivated
    (the refusal is still written to task_logs — see task_id in detail)."""
    try:
        return tasksvc.submit_task(agent_id, body.task_text)
    except registry.AgentNotFound:
        raise HTTPException(status_code=404, detail="agent not found")
    except tasksvc.AgentQuarantined as e:
        raise HTTPException(status_code=403, detail={
            "message": "agent is quarantined; task refused",
            "task_id": e.task_id,   # find the refusal in the logs
        })
    except tasksvc.AgentNotActive as e:
        raise HTTPException(status_code=403, detail={
            "message": "agent is not active; task refused",
            "task_id": e.task_id,   # find the refusal in the logs
        })


@app.get("/agents/{agent_id}/logs", response_model=list[TaskLogOut])
def list_logs(agent_id: int):
    """Audit trail: every step of every task for this agent."""
    try:
        return tasksvc.list_logs(agent_id)
    except registry.AgentNotFound:
        raise HTTPException(status_code=404, detail="agent not found")


# --- Dashboard (static) -------------------------------------------------
# Registered LAST: API routes above always win; everything else falls
# through to dashboard/index.html. Absolute path so it works from any CWD.
DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"
app.mount("/", StaticFiles(directory=DASHBOARD_DIR, html=True), name="dashboard")


# Entry point:  venv/bin/python -m server.main
# NOTE: host is hardcoded to loopback on purpose. Do not change to 0.0.0.0.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000)
