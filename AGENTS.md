# AGENTS.md — how to continue the Watcher repo

> Paste this file (or point your AI at it) to brief any assistant on this
> project. It is the single source of truth for **how the work is done** and
> **what not to do**. The public spec lives in [README.md](README.md).

---

## What this is

**Watcher** — a self-hosted **AI-agent containment platform**. You register your
AI agents, switch them on/off, quarantine them, and watch every step in an
audit log. The core idea: agents are things you **contain**, not things you
trust. The console you open is titled **CONTAINMENT**.

The two-sided vision (only the first half is built):

1. **Watcher** (built, M1) — control room for *your own* agents.
2. **Sentinel** (vision, M8–M9) — a global **agent identity + reputation
   network** ("Truecaller for bots") with due process. Network-effect moat.

Creator: **arush** ([@arushvantore](https://github.com/arushvantore)).

---

## Current state (honest)

- **M1 is done** — backend + a working dashboard. **26 tests pass.**
- **No real AI model yet** — `runner/echo_agent.py` is a pure-function stand-in.
  Real models arrive in **M2**.
- **Loopback only** — the server binds `127.0.0.1` on purpose. Not on the internet.
- The dashboard shows only live API data. **Zero mock data. Zero external requests** (both enforced by tests).

**Current milestone: M2** — integrate a real model (keys via env only), plus
kill-running-tasks, timeouts, and a breach ledger. Do **not** jump ahead of M2.

---

## How to work on this repo (non-negotiable)

1. **Plan → explain in plain language → wait for approval → build → run tests
   after every step.** No exceptions, no surprise edits.
2. **One step at a time.** Run `python -m pytest tests/ -q` after each change
   (expect `26 passed` until you legitimately add a test).
3. **Ask one question instead of guessing** when requirements are ambiguous.
4. **Simple language.** The creator is a student; explain like a teammate, not a manual.
5. **Never** commit, push, install packages, or change pinned requirements
   without explicit approval.

## Locked security invariants (never break these)

- **Server-side gates**: `is_active` and `quarantined` are checked on the server
  *before* any task runs. The UI is convenience, never authority.
- `quarantined` becomes true **only** via `POST /agents/{id}/quarantine` — a
  deliberate action. Never set it automatically (auto-quarantine on malformed
  payloads was **rejected** — it's an attacker DoS vector; log `validation_breach`
  instead, add streak-threshold quarantine in M5).
- **Every refusal is logged** with its `task_id`.
- **No secrets in git.** `.env` is gitignored; `.env.example` holds placeholders.
- **Never write the literal `0.0.0.0`** in `.env.example`, `README.md`, or
  `dashboard/` (a grep test filters comment lines matching `:[0-9]+:\s*#`).
- Pydantic models use `extra="forbid"`; empty `allowed_tools` = **no tools**.
- Dashboard makes **relative fetches only**; `WATCHER` must appear in served HTML.

## Pinned requirements (do NOT change without approval)

`fastapi==0.143.3`, `uvicorn==0.54.0`, `pydantic==2.14.1`,
`python-dotenv==1.2.4`, `pytest==9.1.1`, `httpx==0.28.1`.
**`supabase` is explicitly rejected** (violates the zero-external-deps rule).

## Things we will NEVER do

- Sell/store user credentials; sell identifiable user data or task text; sell
  observer-console surveillance data; put ads/trackers in the console; charge
  users for the core self-hosted product.
- Claim to remotely kill third-party bots we don't run — we only control
  **enrolled runners we ship** and help **defenders enforce a passport at their
  own door**.
- Use fake precision (banned "5 ms") or "first / best ever" marketing.
- Add scope without routing it through the idea bank / 3-of-10 interview gate.

---

## How to run & test

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # first time only; never commit .env
venv/bin/python -m server.main        # serves 127.0.0.1:8000
open http://127.0.0.1:8000/           # the CONTAINMENT console

# tests
python -m pytest tests/ -q            # expect: 26 passed
```

## Repo map

- `server/main.py` — FastAPI routes + dashboard mount (loopback hardcoded)
- `server/db.py` — sqlite schema + auto-migrations
- `server/models.py` — Pydantic bouncers (`extra="forbid"`)
- `server/registry.py` — agent CRUD + quarantine + deactivate-all
- `server/tasks.py` — server-side gates + audit logging
- `runner/echo_agent.py` — v1 stand-in runner (pure function, no network)
- `dashboard/index.html` — containment console (vanilla JS, zero deps)
- `tests/` — the proof for every security claim (26 tests)
- `ROADMAP.md` — idea bank (nothing there is built yet)

## Immediate next steps (M2)

1. Integrate a real model behind the **same runner interface** — keys read from
   env only, never hardcoded, never committed.
2. Add **kill-running-tasks** (cancel an in-flight task server-side).
3. Add **task timeouts** so a hung model can't run forever.
4. Add a **breach ledger** (structured record of gate violations).
5. Keep the existing API shape and the audit-trail guarantees intact; extend
   tests to cover each new behavior.

## Roadmap (beyond M2)

M3 tool registry + queue · M4 accounts + observer DB · M5 alerts ·
M6 public API/SDK + insights + update channel + proof export ·
M7 hosting/hardening/first launch · **M8 Agent Passport** ·
**M9 Sentinel reputation network**. Post-M1 features are gated by the
**3-of-10 user-interview rule** — 3 of 10 interviewed users naming the same
forced need promotes it out of the idea bank.
