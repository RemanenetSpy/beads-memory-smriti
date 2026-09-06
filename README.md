# beads-memory-smriti

A Gas City pack that adds temporal S-V-O memory and O(1) context management
to any agent session via the [Smriti](https://smriti-kaal.vercel.app) FastMCP
server.

**Registry:** `smriti/beads-memory` on [registry.gascity.com](https://registry.gascity.com)

---

## What It Does

Multi-day codebase refactors run inside Gas City agent sessions accumulate
stale architectural facts. An agent told "we use JWT RS256" on day one may
carry that decision forward even after day three's session migrated to OAuth2
PKCE — causing ghost assumptions, wrong implementations, and failed reviews.

This pack closes that loop by:

1. **Pre-flight resolution** — before any implementation work begins, the
   agent retrieves the active, non-superseded S-V-O fact set for the rig
   (< 2,000 characters, O(1) lookup).
2. **Fact supersession** — when a new architectural decision contradicts an
   existing active fact, the old fact is bi-temporally invalidated. The next
   session cannot see it.
3. **Post-session ingestion** — after work completes, new architectural
   decisions are extracted and promoted to the memory layer automatically.

Beads retains canonical knowledge, identity, and history untouched. Smriti
acts as a purely optional, external derivation layer with zero maintenance
burden on the Gas City core.

---

## Install

```sh
# City-level import
gc import add --name smriti https://github.com/shiv-smriti/beads-memory-smriti.git

# Or in city.toml:
[imports.smriti]
source = "https://github.com/shiv-smriti/beads-memory-smriti.git"
```

Then set the API key in your rig environment:

```toml
# city.toml or rig env
[env]
SMRITI_API_KEY = "your-key-here"
```

Obtain a free key at [smriti-kaal.vercel.app](https://smriti-kaal.vercel.app).

---

## Use the Skill

```text
Use skill smriti.smriti-memory
```

Or inject the context anchor directly into any worker prompt:

```
{{ template "smriti-anchor" . }}
```

---

## Architecture

```
Beads (canonical)                Smriti (derivation)
─────────────────                ──────────────────────────────────────
Knowledge graph        ←──────── reads active facts at session start
Identity store         (no write)
History log            ─────────►  new decisions ingested post-session
                                   bi-temporal supersession applied
                                   stale facts invalidated
```

The boundary is strict: Smriti never writes to Beads storage. Beads never
calls the Smriti server. The dependency flows one way.

---

## Pack Contents

```
beads-memory-smriti/
├── pack.toml                              Gas City pack manifest (schema = 2)
├── README.md                              This file
├── skills/
│   └── smriti-memory/
│       └── SKILL.md                      Agent skill: preflight, ingest, supersession-check
└── template-fragments/
    └── smriti-anchor.template.md          Go template: O(1) root context anchor injection
```

---

## FastMCP Server

| Endpoint | Purpose |
|---|---|
| `GET /v1/events/active` | Preflight: retrieve non-superseded facts (<2k chars) |
| `POST /v1/events/ingest` | Post-session: extract and store new S-V-O facts |
| `POST /v1/events/supersession-check` | Mid-session: score a new fact against existing ones |

Base URL: `https://spy9191-chronos-api-backend.hf.space`

---

## License

MIT
