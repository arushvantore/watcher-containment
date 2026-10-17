"""echo_agent.py — the FAKE agent for version 1. No AI, no network.

Design rule: this module NEVER imports the database or FastAPI.
It is a pure function: tools + task text in → output + steps out.
The server (tasks.py) decides what gets logged and what HTTP
status is returned. This isolation is what lets version 2 swap
in a real model without rewriting the API.

Version 1 has exactly one tool: "echo". The dead "is this tool
known?" check was removed — the allowlist check below is the real
gate, and the runner only ever calls "echo" itself, so a known-tools
set could never fail (nothing else is invoked).
"""

from dataclasses import dataclass, field


@dataclass
class Step:
    """One line of the audit trail the runner wants recorded."""
    step: str      # e.g. "tool_call:echo", "tool_denied"
    status: str    # "ok" | "rejected" | "error"
    detail: str = ""


@dataclass
class RunResult:
    """What the runner produced for one task."""
    status: str                 # "completed" | "rejected" | "error"
    output: str = ""            # what the user sees back
    steps: list[Step] = field(default_factory=list)


def run_task(allowed_tools: list[str], task_text: str) -> RunResult:
    """Echo the task back — but ONLY if the 'echo' tool is allowed.

    SECURITY RULE IN ACTION: having an agent is not enough. The tool
    must be explicitly listed in allowed_tools. Default is no tools,
    so a fresh agent's tool call is denied here.
    """
    if "echo" not in allowed_tools:
        return RunResult(
            status="rejected",
            output="",
            steps=[Step(
                step="tool_denied",
                status="rejected",
                detail="tool 'echo' not in allowed_tools",
            )],
        )

    # Tool is allowed: perform it. (Real agents in v2+ would branch
    # over multiple tools here.)
    return RunResult(
        status="completed",
        output=f"echo: {task_text}",
        steps=[Step(
            step="tool_call:echo",
            status="ok",
            detail=f"echoed back {len(task_text)} characters",
        )],
    )
