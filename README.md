# WATCHER — AI Agent Containment Platform

> **Let AI do my work — without trusting it blindly.**
> Working name **Watcher**. The console you open is titled **CONTAINMENT**.

**Creator:** arush ([@arushvantore](https://github.com/arushvantore)) · LinkedIn: TBD
**Status:** v1 complete, **26 tests passing**. No AI model yet (v1 runner is a safe
stand-in) — real models arrive in M2. Everything below is labeled honestly:
**works today** vs **planned**.

---

## 1. What it is

A self-hosted **control room for AI agents**: register them, switch them on/off,
quarantine them, watch every step they take in an audit log — and stop everything
with one button. Agents are treated like things you **contain**, not things you
trust.

The long-term vision: the **control + proof layer for autonomous AI** — a kill
switch, a black box, and verifiable proof of what an agent did. Identity for
agents comes later (see *Agent Passport* below).

---

## 2. What works TODAY (v1)

- **Register agents** — name, purpose, allowed tools. Empty tools = **no tools**, by design.
- **Three real states**
  - 🟢 `active` — accepts tasks
  - 🔵 `standby` — refuses tasks **and logs the refusal**
  - 🔴 `quarantined` — set only by a deliberate action; refuses tasks **even if active**
- **Server-enforced gates** — deactivation and quarantine are checked on the
  server before anything runs. The UI cannot bypass them (proven by tests).
- **Audit log** — every step, timestamped, grouped by `task_id`. Refusals logged too.
  Logs survive state changes (`ON DELETE RESTRICT`).
- **Emergency stop** — `POST /agents/deactivate-all` turns everything off in one call.
- **Health check** — `GET /health` really queries the database (503 if it fails).
- **Containment dashboard** — dark console at `/`: draggable globe map, sector
  cards, unit view, owner-only maker console. Every number comes from the live
  API. **No mock data anywhere. Zero external requests — enforced by a test.**

### What it is NOT (yet)

- Not on the internet — binds this computer only, on purpose
- No accounts (M4), no alerts (M5), no public API (M6), no hosting (M7)
- No real AI model (M2), no billing of any user (ever, for the core)
- No update channel, no observer console — planned, see §3

---

## 3. Services — the full ladder

Every service we discussed, in one list. **Status is honest**: *works today* vs
*planned* with its milestone.

| # | Service | Status | Who pays |
|---|---|---|---|
| 1 | **Self-hosted open-source core** — everything in §2 | ✅ Works today | Nobody — free forever |
| 2 | **Hosted free tier** — we run it, limited agents/history | Planned (M7) | Nobody |
| 3 | **Pro hosted** — alerts, viewer links, proof export, history | Planned (M7+) | Us (subscriptions, later) |
| 4 | **Business / Enterprise** — teams, roles, compliance pack, audit views | Planned (post-M7) | Companies |
| 5 | **Platform API** — other products plug verification into us (SDK, signed events) | Planned (M6) | Platforms (metered) |
| 6 | **Update-notify channel** — ship features, users tap to update (§3.1) | Planned (post-M4) | Nobody (core) |
| 7 | **Observer security console** — operator-only view for our IT team (§3.2) | Planned (M4→M7) | Us (it secures *our* service) |
| 8 | **Anonymous industry insights** — aggregate opt-in stats (§3.3) | Planned (M6+, after interviews) | Companies (aggregate only) |
| 9 | **Marketplace** — agent/tool integrations listed by others | Idea bank | Us (small cut) |
| 10 | **Agent Passport** — verifiable agent identity (§3.4) | Vision | Part of Pro/Business |
| 11 | **Proof export / black box** — signed audit packages as verifiable proof | Vision | Part of Pro/Business |

**Sponsors / open source** also count as revenue (way 3: someone else pays) —
companies sponsor the core instead of their users paying for it.

### 3.1 Update-notify channel (tap-to-update)

1. We ship a new version → the server publishes an **update notice** (version,
   what's new, when).
2. Every connected console shows an in-app notification banner — no email, no spam.
3. User taps **Update** → pulls the update and restarts (self-hosted: `git pull` +
   restart; hosted: handled by us automatically).

Planned with accounts (M4+). Notifications are **read from our own server** —
the console never talks to any outside service.

### 3.2 Observer security console (second database)

A **separate database**, distinct from all agent/task data, that records service-
level events for **security operations only**:

- who logged in, from which IP, when
- account condition (active / locked / flagged)
- abuse events (rate-limit hits, failed logins, suspicious patterns)

**Rules written into the product, not optional:**

1. Visible **only to the operator team** (you + designated IT) — never to other users
2. **Disclosed to users** in plain language — they know it exists and why
3. Kept only for security, **never sold**, never used for ads
4. Retention-limited — old records get deleted, not hoarded

That boundary is the difference between *security operations* and *spyware* —
and since Watcher sells trust, we hold ourselves to it.

### 3.3 Anonymous industry insights

Opt-in, **aggregate-only** numbers (e.g. "how often agents were quarantined this
month across participants"). No task text, no credentials, no identifiable data —
only possible after user interviews (the 3-of-10 rule) and only with opt-in.

### 3.4 Agent Passport (vision)

Later layer: every agent gets a **verifiable identity** — who runs it, what
permissions it claims, its containment history. "Would you trust a bot with no
ID?" Passport is the answer, and it feeds Pro/Business tiers.

---

## 4. Rules locked (how this project is built)

1. Plan → approval → build → **tests after every step** — no exceptions
2. Binds this machine only; network exposure only with hardening (M7)
3. **No secrets in git.** `.env` (gitignored) holds config; `.env.example` has placeholders
4. Every gate is enforced **server-side**; the UI is convenience, not authority
5. Every refusal is logged with its `task_id`
6. Dashboard makes **relative requests only** — enforced by a test
7. No mock/fake data in the UI — if it's on screen, it came from the API
8. No scope jumps — new ideas go to the idea bank first
9. The console carries **no ads** — ever
10. UI follows the creator's designs; animations only react to real actions

## 5. What we will NEVER do

- ❌ Sell or store login credentials of users
- ❌ Sell or expose identifiable user data or task text — the promise is "we don't read your task text"
- ❌ Sell surveillance data from the observer console — security use only
- ❌ Put ads or trackers in the console
- ❌ Charge users for the core self-hosted product

## 6. Earning model (no user pays for the core)

| Way | Example |
|---|---|
| **Someone else pays (3)** | Companies/teams fund hosted tiers; platforms pay for API calls; sponsors fund open source |
| **Marketplace cut (4)** | Later — others list integrations, we take a small cut |
| **Anonymous insights (safe extra)** | Opt-in aggregate stats, non-identifiable, after interviews |

Billing code and pricing pages only after M7 hardening — nothing before that.

---

## 7. Roadmap

| Milestone | What | Status |
|---|---|---|
| **M1** | Control core: states, gates, quarantine, audit, stop-all, health, dashboard | ✅ Done (26 tests) |
| **M2** | Real model integration (keys via env only) | Planned |
| **M3** | Tools/queue with live task status | Planned |
| **M4** | Accounts + the observer security database (§3.2) | Planned |
| **M5** | Alerts (offline, refusal streaks, manual rules) | Planned |
| **M6** | Public API/SDK + opt-in insights + update channel (§3.1) | Planned |
| **M7** | Hosting, hardening, rate limits, license/scale, first honest launch | Planned |

**Gate:** post-M1 features are chosen by **user interviews (3-of-10 rule)** —
if 3 of 10 interviewed users name the same forced need, it jumps the idea bank.
Candidates in the bank: budget kill-switch, secret-guard (what the agent could
see), compliance pack export, rollback, scale-up detection.

---

## 8. Install & run

Requirements: Python 3.11+, no other services.

```bash
# 1. virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. configure (first time only) — never commit .env
cp .env.example .env

# 3. start the server
venv/bin/python -m server.main

# 4. open the dashboard
open http://127.0.0.1:8000/
```

The server only accepts connections from **this computer**. That is a security
default, not a limitation to work around.

## 9. Tests

```bash
source venv/bin/activate
python -m pytest tests/ -q
# expected: 26 passed
```

The suite proves the security promises: server-side activation gate (403 + logged
refusal), quarantine gate, tool allowlist, `deactivate-all` route parsing, real
`/health` checks, dashboard served, and **no outside URLs anywhere in the dashboard**.

---

## 10. API

| Method & path | What it does |
|---|---|
| `GET /health` | real DB checkup → `{"status":"ok","db":"connected"}` |
| `GET /agents` | list all agents |
| `POST /agents` | register an agent (`name` required; unknown fields rejected) |
| `GET /agents/{id}` | one agent |
| `POST /agents/{id}/activate` | switch on |
| `POST /agents/{id}/deactivate` | switch off |
| `POST /agents/{id}/quarantine` | **deliberate lock** — only way `quarantined` becomes true |
| `POST /agents/{id}/unquarantine` | release the lock |
| `POST /agents/deactivate-all` | emergency: turn every active agent off (idempotent) |
| `POST /agents/{id}/tasks` | submit a task → `200`, or `403` if off/quarantined (refusal logged) |
| `GET /agents/{id}/logs` | full audit trail for one agent |

Security behavior baked in:

- Pydantic rejects unknown/oversized input (`422`)
- `allowed_tools` must match `^[a-z0-9_-]{1,50}$` — format junk is refused
- Runner denies any tool not on the agent's allowlist (`tool_denied` logged)
- `403` responses carry the `task_id` of the logged refusal

---

## 11. Project layout

```
agent-platform/
├── server/          # FastAPI app: routes, DB, validation, gates
│   ├── main.py      # endpoints + dashboard mount (host is loopback, hardcoded)
│   ├── db.py        # sqlite3 schema + auto-migrations
│   ├── models.py    # Pydantic bouncers (extra="forbid")
│   ├── registry.py  # agent CRUD + quarantine + deactivate-all
│   └── tasks.py     # server-side gates + audit logging
├── runner/
│   └── echo_agent.py  # v1 stand-in runner (pure function, no network)
├── dashboard/
│   └── index.html   # containment console (vanilla JS, zero dependencies)
├── tests/           # 26 tests — the proof for every security claim
├── db/agents.sqlite # your data (gitignored)
├── ROADMAP.md       # idea bank (nothing there is built yet)
├── .env.example     # config template — real .env is gitignored
├── LICENSE          # MIT
└── requirements.txt # pinned: fastapi, uvicorn, pydantic, dotenv, pytest, httpx
```

## 12. Contributing

Change code the way this project is built: **plan → approval → build → tests
after each step.** Nothing ships untested. New features start in the idea bank.

## 13. License

MIT — see [LICENSE](LICENSE). © 2026 arush.
