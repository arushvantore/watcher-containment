# ROADMAP.md — ideas for future versions. Nothing here is built yet.

## Version 2+ candidates

- Real AI model integration (keys via environment variables only)
- Tool registry with existence checks enforced by the runner
- Task queue with async execution and live status updates
- Authentication / multi-user support
- Agent deletion endpoint (currently blocked by ON DELETE RESTRICT
  once an agent has task logs — deliberate audit-trail protection)

## Maintenance notes

- **Starlette/httpx deprecation warning** (seen in pytest output):
  `starlette.testclient` warns that using `httpx` is deprecated and
  suggests installing `httpx2` instead. Harmless in v1. When we next
  touch test infrastructure, evaluate migrating to `httpx2` (or a
  newer Starlette that drops the warning) and update `requirements.txt`
  with an explanation of the version change.
