"""db.py — the database layer.

This file is the ONLY place that talks raw SQL. It creates the database
file, defines the tables (the "schema"), and hands out connections.
Other modules (registry.py, tasks.py) will import from here.

Why sqlite3 (built into Python)? Zero extra installs, one file on disk,
and you can open it with any SQLite viewer to SEE your data while learning.
"""

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

# Project root = the folder that CONTAINS server/ (one level up from this file).
# We use this so the database path works no matter where you launch the
# server from (project folder, tests, etc.).
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env FIRST, so any os.getenv() below actually sees your .env values.
# We pass an explicit path (not bare load_dotenv()) so this works no matter
# which directory you run the server or tests from.
load_dotenv(PROJECT_ROOT / ".env")

# Where the database file lives. Reads DATABASE_PATH from .env if set,
# otherwise falls back to db/agents.sqlite inside the project.
DB_PATH = Path(os.getenv("DATABASE_PATH", "db/agents.sqlite"))
if not DB_PATH.is_absolute():
    DB_PATH = PROJECT_ROOT / DB_PATH


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database.

    Every call gives a fresh connection (simple and safe for our scale).
    Two important settings:
      - row_factory=sqlite3.Row  ->  query results can be accessed by
        column NAME (row["name"]) instead of index, which is far more
        readable and less error-prone.
      - PRAGMA foreign_keys = ON  ->  SQLite IGNORES foreign keys by
        default (!). This line makes the database actually enforce that
        task_logs.agent_id must point at a real agent.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create the tables if they don't exist yet.

    CREATE TABLE IF NOT EXISTS means: safe to run repeatedly — it will
    never wipe existing data. We call this once at server startup.
    """
    conn = get_connection()
    try:
        # Auto-migration: add task_id to DBs created before step 4.
        # Runs BEFORE executescript so old tables gain the column.
        # PRAGMA returns no rows if task_logs doesn't exist yet (fresh DB).
        cols = [r[1] for r in conn.execute("PRAGMA table_info(task_logs)")]
        if cols and "task_id" not in cols:
            conn.execute(
                "ALTER TABLE task_logs ADD COLUMN task_id TEXT NOT NULL DEFAULT ''"
            )
        # Auto-migration: add quarantined to agents tables created before
        # the quarantine feature. Fresh DBs get it from SCHEMA instead.
        acols = [r[1] for r in conn.execute("PRAGMA table_info(agents)")]
        if acols and "quarantined" not in acols:
            conn.execute(
                "ALTER TABLE agents ADD COLUMN quarantined INTEGER NOT NULL DEFAULT 0"
            )
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()  # always release the connection, even if SQL failed


# The schema lives in one string so you can read the "shape" of the
# database top-to-bottom in one place.
SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique number, auto-assigned
    name           TEXT NOT NULL UNIQUE,               -- human label, must be unique
    description    TEXT NOT NULL DEFAULT '',           -- optional long text
    purpose        TEXT NOT NULL DEFAULT '',           -- what the agent is FOR
    allowed_tools  TEXT NOT NULL DEFAULT '[]',         -- JSON list, e.g. ["echo"]
                                                   -- stored as TEXT because SQLite
                                                   -- has no native list type
    is_active      INTEGER NOT NULL DEFAULT 0,         -- 0 = off, 1 = on
                                                   -- (SQLite has no boolean type)
    quarantined    INTEGER NOT NULL DEFAULT 0,         -- 0 = normal, 1 = QUARANTINED
                                                   -- set ONLY by the deliberate
                                                   -- /quarantine action
    created_at     TEXT NOT NULL                       -- ISO-8601 UTC string,
                                                       -- e.g. "2026-10-17T05:20:00+00:00"
);

CREATE TABLE IF NOT EXISTS task_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,      -- unique log line number
    task_id    TEXT NOT NULL,                          -- groups all steps of
                                                       -- one submission together
    agent_id   INTEGER NOT NULL,                       -- which agent this belongs to
    task_text  TEXT NOT NULL,                          -- the task the user submitted
    step       TEXT NOT NULL,                          -- what happened, e.g. "activation_check"
    status     TEXT NOT NULL,                          -- "ok" | "rejected" | "error" | ...
    detail     TEXT NOT NULL DEFAULT '',               -- extra info (reason, echo output...)
    created_at TEXT NOT NULL,                          -- when this step happened
    FOREIGN KEY (agent_id) REFERENCES agents(id)
        ON DELETE RESTRICT                            -- audit trail protection:
                                                       -- refuse to delete an agent
                                                       -- that still has task logs
);
"""
