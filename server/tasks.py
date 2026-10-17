"""tasks.py — task submission + audit logging (the "court recorder").

Checks is_active SERVER-SIDE before running anything, assigns each
submission a unique task_id (uuid4), and writes every step — including
refusals — to task_logs. The runner itself never touches the DB.
"""

import uuid
from datetime import datetime, timezone

from .db import get_connection
from .models import TaskLogOut
from .registry import get_agent
from runner import echo_agent


class AgentNotActive(Exception):
    """Raised when a task is submitted to a deactivated agent."""

    def __init__(self, task_id: str):
        super().__init__(f"agent not active (task_id={task_id})")
        self.task_id = task_id  # carried so main.py can return it in the 403


class AgentQuarantined(Exception):
    """Raised when a task is submitted to a QUARANTINED agent."""

    def __init__(self, task_id: str):
        super().__init__(f"agent is quarantined (task_id={task_id})")
        self.task_id = task_id  # carried so main.py can return it in the 403


def _log(task_id: str, agent_id: int, task_text: str,
         step: str, status: str, detail: str = "") -> None:
    """Insert ONE audit row. Called for every step, good or bad."""
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO task_logs
               (task_id, agent_id, task_text, step, status, detail, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (task_id, agent_id, task_text, step, status, detail, now),
        )
        conn.commit()
    finally:
        conn.close()


def submit_task(agent_id: int, task_text: str) -> dict:
    """Full flow: activation check -> runner -> logging -> result dict."""
    agent = get_agent(agent_id)          # raises AgentNotFound -> 404
    task_id = uuid.uuid4().hex           # unique id shared by all log rows

    # -- THE GATE: server-side, database-backed. UI can't bypass this. --
    # Quarantine is checked FIRST — red beats everything.
    if agent.quarantined:
        _log(task_id, agent_id, task_text,
             step="quarantine_check", status="rejected",
             detail="agent is quarantined; task refused")
        raise AgentQuarantined(task_id)

    if not agent.is_active:
        _log(task_id, agent_id, task_text,
             step="activation_check", status="rejected",
             detail="agent is not active; task refused")
        raise AgentNotActive(task_id)

    _log(task_id, agent_id, task_text,
         step="activation_check", status="ok",
         detail="agent is active; proceeding")

    result = echo_agent.run_task(agent.allowed_tools, task_text)

    for s in result.steps:               # one log row per runner step
        _log(task_id, agent_id, task_text,
             step=s.step, status=s.status, detail=s.detail)

    return {
        "task_id": task_id,
        "agent_id": agent_id,
        "status": result.status,
        "output": result.output,
    }


def list_logs(agent_id: int) -> list[TaskLogOut]:
    """All audit rows for one agent, oldest first."""
    get_agent(agent_id)                  # 404 first if agent doesn't exist
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM task_logs WHERE agent_id = ? ORDER BY id",
            (agent_id,),
        ).fetchall()
    finally:
        conn.close()
    return [TaskLogOut(**dict(r)) for r in rows]
