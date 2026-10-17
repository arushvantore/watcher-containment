"""models.py — Pydantic schemas: the input/output "bouncers" of the API.

Every JSON body that enters the API is parsed through these classes FIRST.
If the data doesn't fit the declared shape, FastAPI automatically returns
HTTP 422 and the bad data never reaches the database.
"""

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentCreate(BaseModel):
    """Shape of the JSON body accepted by POST /agents.

    extra='forbid'  ->  unknown fields are REJECTED (not silently ignored).
    Field(...)      ->  constraints: lengths, non-empty, etc.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ..., min_length=1, max_length=100,
        description="Unique human label for the agent."
    )
    description: str = Field(
        default="", max_length=2000,
        description="Optional long description."
    )
    purpose: str = Field(
        default="", max_length=2000,
        description="What the agent is for."
    )
    allowed_tools: list[str] = Field(
        default_factory=list, max_length=50,
        description="Tools the agent may use. Empty = no tools (default)."
    )

    @field_validator("allowed_tools", mode="after")
    @classmethod
    def _clean_tool_names(cls, tools: list[str]) -> list[str]:
        """Validate each tool name: 1-50 chars, lowercase letters/digits/_/- only.

        NOTE: this only validates the FORMAT. Whether a tool actually EXISTS
        is enforced by the runner in step 4 — registry just stores the list.
        """
        cleaned = []
        for t in tools:
            t = t.strip().lower()
            if not re.fullmatch(r"[a-z0-9_-]{1,50}", t):
                raise ValueError(f"invalid tool name: {t!r}")
            cleaned.append(t)
        return cleaned


class AgentOut(BaseModel):
    """Shape of agent data we RETURN to the client.

    Same fields as the DB row, but allowed_tools is a real JSON list
    (the DB stores it as text; registry.py converts it).
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    description: str
    purpose: str
    allowed_tools: list[str]
    is_active: bool
    quarantined: bool
    created_at: str


class HealthOut(BaseModel):
    """Shape of GET /health — the server's checkup card."""

    model_config = ConfigDict(extra="forbid")

    status: str   # "ok" (DB answered) — errors return 503 instead
    db: str       # "connected" | "unavailable"


class DeactivateAllOut(BaseModel):
    """Shape of POST /agents/deactivate-all — how many agents were flipped off."""

    model_config = ConfigDict(extra="forbid")

    deactivated: int  # number of agents that were active and are now off


class TaskSubmit(BaseModel):
    """Shape of POST /agents/{id}/tasks body."""

    model_config = ConfigDict(extra="forbid")

    task_text: str = Field(
        ..., min_length=1, max_length=4000,
        description="The task for the agent to perform."
    )


class TaskLogOut(BaseModel):
    """One row of the audit trail, as returned by the logs endpoint."""

    model_config = ConfigDict(extra="forbid")

    id: int
    task_id: str
    agent_id: int
    task_text: str
    step: str
    status: str
    detail: str
    created_at: str


class TaskResultOut(BaseModel):
    """Response after submitting a task."""

    model_config = ConfigDict(extra="forbid")

    task_id: str
    agent_id: int
    status: str          # "completed" | "rejected"
    output: str
