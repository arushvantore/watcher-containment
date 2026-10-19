# WATCHER — AI Agent Containment Platform

> **Let AI do my work — without trusting it blindly.**
> Working name **Watcher**. The console you open is titled **CONTAINMENT**.

**Creator:** arush ([@arushvantore](https://github.com/arushvantore)) · LinkedIn: TBD
**Status:** M1 complete, **26 tests passing**. No AI model yet (the v1 runner is a
safe stand-in) — real models arrive in M2. Everything below is labeled honestly:
**works today** vs **planned** vs **vision**.

---

## 1. What it is — the two-sided vision

Watcher is **two products that reinforce each other**:

1. **Watcher (the control room)** — a self-hosted console for *your own* AI
   agents: register them, switch them on/off, quarantine them, watch every step
   in an audit log, and stop everything with one button. Agents are things you
   **contain**, not things you trust. This is what's built today (M1).

2. **Sentinel (the trust network)** — a later, global layer: a **verifiable
   identity + reputation network for AI agents**. Think *"Truecaller for bots."*
   Every agent gets a passport; defenders share signals so a malicious agent
   flagged on one network is known at everyone else's door — with due process
   and an appeal path. This is the long-term moat (M8–M9, vision).

**The gap we're attacking:** ~400 AI-security startups exist, but almost all
target enterprises defending *perimeters*. Nobody owns **personal, cross-platform
agent containment** (protect a normal person's agents across Gmail/Slack/etc.)
plus a **global reputation network**. That combined gap is the opportunity — and
the reputation side has a **network effect** (the more nodes, the more valuable),
which is the durable moat.

**Honest framing (locked):** we do **not** claim to remotely kill third-party
bots we don't run. We can only (a) control **enrolled runners we ship**, and
(b) help **defenders enforce a passport at their own door**. No fake precision
(e.g. banned "5 ms" claims), no "first / best ever" marketing. We **align** with
open standards (OpenA2A Agent Passport, A2A, FIDO) rather than fighting them.

---

## 2. What works TODAY (M1)

- **Register agents** — name, purpose, allowed tools. Empty tools = **no tools**, by design.
- **Three real states**
  - 🟟 `active` — accepts tasks
  - 🔵 `standby` — refuses tasks **and logs the refusal**
  - 🔴 `quarantined` — set only by a deliberate action; refuses tasks **even if active**
- **Server-enforced gates** — deactivation and quarantine are checked on the
  server before anything runs. The UI cannot bypass them (proven by tests).
- **Audit log** — every step, timestamped, grouped by `task_id`. Refusals logged
  too. Logs survive state changes (`ON DELETE RESTRICT`).
- **Emergency stop** — `POST /agents/deactivate-all` turns everything off in one call.
- **Health check** — `GET /health` really queries the database (503 if it fails).
- **Containment dashboard** — dark console at `/`. Every number comes from the
  live API. **No mock data anywhere. Zero external requests — enforced by a test.**

### What it is NOT (yet)

- Not on the internet — binds this computer only, on purpose
- No accounts (M4), no alerts (M5), no public API (M6), no hosting (M7)
- No real AI model (M2), no billing of any user (ever, for the core)
- No passport / reputation network (M8–M9) — vision only

---

## 3. Services — the full ladder

**Status is honest**: *works today* vs *planned* (with milestone) vs *vision*.

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
| 10 | **Agent Passport** — verifiable agent identity (§3.4) | Vision (M8) | Part of Pro/Business |
| 11 | **Sentinel reputation network** — cross-organization trust signals (§3.5) | Vision (M9) | Part of Business / Platform |

**Sponsors / open source** also count as revenue (someone else pays) —
companies sponsor the core instead of their users paying for it.

### 3.1 Update-notify channel (tap-to-update)

1. We ship a new version → the server publishes an **update notice** (version,
   what's new, when).
2. Every connected console shows an in-app banner — no email, no spam.
3. User taps **Update** → pulls the update and restarts (self-hosted: `git pull` +
   restart; hosted: handled by us automatically).

Notifications are **read from our own server** — the console never talks to any
outside service.

### 3.2 Observer security console (second database)

A **separate database**, distinct from all agent/task data, that records service-
level events for **security operations only**: who logged in, from which IP, when;
account condition; abuse events.

**Rules written into the product, not optional:**

1. Visible **only to the operator team** — never to other users
2. **Disclosed to users** in plain language — they know it exists and why
3. Kept only for security, **never sold**, never used for ads
4. Retention-limited — old records get deleted, not hoarded

That boundary is the difference between *security operations* and *spyware* —
and since Watcher sells trust, we hold ourselves to it.

### 3.3 Anonymous industry insights

Opt-in, **aggregate-only** numbers (e.g. "how often agents were quarantined this
month across participants"). No task text, no credentials, no identifiable data —
only after user interviews (the 3-of-10 rule) and only with opt-in.

### 3.4 Agent Passport (vision, M8)

Every agent gets a **verifiable identity** — who runs it, what permissions it
claims, its containment history. "Would you trust a bot with no ID?" Passport is
the answer. It feeds Pro/Business tiers and is the seed of Sentinel.

### 3.5 Sentinel reputation network (vision, M9)

The **global trust layer**: agents present a passport; participating networks
share signed signals (verified / reported / flagged) so a bad actor is known at
multiple doors at once. Built with **due process** — every flag has a human
**appeal path**, and a flag never silently kills an agent. This is the
"Truecaller for agents" and the network-effect moat.

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
| **Someone else pays** | Companies/teams fund hosted tiers; platforms pay for API calls; sponsors fund open source |
| **Marketplace cut** | Later — others list integrations, we take a small cut |
| **Anonymous insights (safe extra)** | Opt-in aggregate stats, non-identifiable, after interviews |

Billing code and pricing pages only after M7 hardening — nothing before that.

---

## 7. Roadmap

| Milestone | What | Status |
|---|---|---|
| **M1** | Control core: states, gates, quarantine, audit, stop-all, health, dashboard | ✅ Done (26 tests) |
| **M2** | Real model integration (keys via env only) + kill-running-tasks + timeouts + breach ledger | Planned |
| **M3** | Tool registry + task queue (live status) | Planned |
| **M4** | Accounts + the observer security database (§3.2) | Planned |
| **M5** | Alerts (offline, refusal streaks, manual rules) | Planned |
| **M6** | Public API/SDK + opt-in insights + update channel (§3.1) + proof export | Planned |
| **M7** | Hosting, hardening, rate limits, license/scale, first honest launch | Planned |
| **M8** | **Agent Passport** — verifiable agent identity (§3.4) | Vision |
| **M9** | **Sentinel** — cross-org reputation network with due process (§3.5) | Vision |

**Timeline (honest estimate):** M1→M7 ≈ **3–4 months part-time**. Reaching a
credible **enterprise** offering (M7+): **12–18+ months**. M8–M9 are longer-horizon.

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
├── AGENTS.md        # AI-assistant handoff brief (how to continue this repo)
├── .env.example     # config template — real .env is gitignored
├── LICENSE          # MIT
└── requirements.txt # pinned: fastapi, uvicorn, pydantic, dotenv, pytest, httpx
```

## 12. For AI assistants working on this repo

This project has a companion brief, **[AGENTS.md](AGENTS.md)** — read it before
changing anything. It captures the working style (plan → approval → build →
tests), the locked security invariants, the never-list, and the immediate next
steps, so any assistant can pick up the work consistently. In short:

- **Plan and get approval before editing.** Run tests after every step.
- **Never** weaken a security gate, add secrets to git, or introduce mock data.
- The current milestone is **M2** (real model integration). Everything else is
  gated behind user interviews (3-of-10 rule) or is later vision.

## 13. Contributing

Change code the way this project is built: **plan → approval → build → tests
after each step.** Nothing ships untested. New features start in the idea bank.

## 14. License

MIT — see [LICENSE](LICENSE). © 2026 arush.
