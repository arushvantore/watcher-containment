"""registry.py — all agent database operations (the "librarian").

This module talks to SQLite through db.py and knows NOTHING about HTTP.
main.py catches the exceptions below and turns them into HTTP status codes.
"""

import json
import sqlite3
from datetime import datetime, timezone

from .db import get_connection
from .models import AgentCreate, AgentOut


class AgentNotFound(Exception):
    """No agent with that id exists."""


class AgentAlreadyExists(Exception):
    """An agent with that name already exists."""


def _row_to_out(row) -> AgentOut:
    """Convert a raw DB row into an AgentOut, parsing the JSON tool list."""
    return AgentOut(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        purpose=row["purpose"],
        allowed_tools=json.loads(row["allowed_tools"]),  # "[]"/'["echo"]' -> list
        is_active=bool(row["is_active"]),                 # 0/1 -> False/True
        quarantined=bool(row["quarantined"]),             # 0/1 -> False/True
        created_at=row["created_at"],
    )


def create_agent(data: AgentCreate) -> AgentOut:
    """Insert a new agent. Starts deactivated (is_active=0) per spec."""
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO agents
               (name, description, purpose, allowed_tools, is_active, created_at)
               VALUES (?, ?, ?, ?, 0, ?)""",
            (data.name, data.description, data.purpose,
             json.dumps(data.allowed_tools), now),
        )
        conn.commit()
        agent_id = cur.lastrowid
    except sqlite3.IntegrityError as e:
        # SQLite raises IntegrityError when a UNIQUE constraint (our
        # agents.name) is violated. Catching the typed exception is
        # reliable — no string-matching on error messages.
        raise AgentAlreadyExists(data.name) from e
    finally:
        conn.close()
    return get_agent(agent_id)


def list_agents() -> list[AgentOut]:
    """Return every agent, oldest first."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM agents ORDER BY id").fetchall()
    finally:
        conn.close()
    return [_row_to_out(r) for r in rows]


def get_agent(agent_id: int) -> AgentOut:
    """Return one agent or raise AgentNotFound."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM agents WHERE id = ?", (agent_id,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise AgentNotFound(agent_id)
    return _row_to_out(row)


def set_agent_active(agent_id: int, active: bool) -> AgentOut:
    """Flip is_active on/off. Raises AgentNotFound if the agent is missing."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE agents SET is_active = ? WHERE id = ?",
            (1 if active else 0, agent_id),
        )
        conn.commit()
        if cur.rowcount == 0:  # UPDATE matched no rows
            raise AgentNotFound(agent_id)
    finally:
        conn.close()
    return get_agent(agent_id)


def set_agent_quarantined(agent_id: int, quarantined: bool) -> AgentOut:
    """Deliberate quarantine/release action. Separate from is_active:
    quarantined=1 is red ONLY when set here — never inferred from logs."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE agents SET quarantined = ? WHERE id = ?",
            (1 if quarantined else 0, agent_id),
        )
        conn.commit()
        if cur.rowcount == 0:  # UPDATE matched no rows
            raise AgentNotFound(agent_id)
    finally:
        conn.close()
    return get_agent(agent_id)


def deactivate_all() -> int:
    """Turn off EVERY active agent in one statement.
    Returns how many were flipped (0 on a second call — safe to repeat)."""
    conn = get_connection()
    try:
        cur = conn.execute("UPDATE agents SET is_active = 0 WHERE is_active = 1")
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
