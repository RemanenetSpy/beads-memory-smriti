---
name: smriti-memory
description: >
  Temporal S-V-O memory layer for Gas City agents. Provides O(1) pre-flight
  context resolution, fact supersession, and stale-fact garbage collection via
  the Smriti FastMCP server. Use this skill to prevent context poisoning across
  multi-day codebase refactors and long-running agent sessions.
---

# Smriti Memory Skill

This skill integrates the Smriti temporal knowledge graph into any Gas City
agent session. It teaches agents how to:

1. **Pre-flight context resolution** — pull only the active, non-superseded
   facts relevant to the current task before starting work.
2. **S-V-O extraction** — extract Subject-Verb-Object tuples from new context
   and promote them into the memory layer after completing work.
3. **Fact supersession** — identify and invalidate stale facts that contradict
   new architectural decisions, preventing ghost assumptions.

## When to Use

Invoke this skill at the start of any implementation session that spans
multiple days, involves architectural changes, or operates on a codebase where
prior decisions may have been revised.

## FastMCP Endpoints

The Smriti memory server is accessible via FastMCP at:

```
Base URL: https://spy9191-chronos-api-backend.hf.space
Console:  https://smriti-kaal.vercel.app
```

### Tool: `preflight_context`

Retrieves the active, non-superseded S-V-O facts for the current rig scope.
Returns a context block guaranteed to be under 2,000 characters — suitable as
an L0 root anchor injected into the session prompt.

**Call pattern:**
```
GET /v1/events/active?scope={rig_name}&limit=20
Authorization: Bearer {SMRITI_API_KEY}
```

**Response shape:**
```json
{
  "facts": [
    {
      "subject": "AuthService",
      "verb": "uses",
      "object": "JWT RS256",
      "valid_from": "2026-09-01T00:00:00Z",
      "valid_to": null
    }
  ],
  "total_active": 14,
  "context_chars": 1847
}
```

### Tool: `ingest_facts`

After completing an implementation task, extract new S-V-O tuples and push
them to the memory layer. The server automatically runs supersession scoring
against existing facts.

**Call pattern:**
```
POST /v1/events/ingest
Content-Type: application/json
Authorization: Bearer {SMRITI_API_KEY}

{
  "source_id": "{rig_name}",
  "scope": "{rig_name}",
  "raw_text": "{summary_of_changes}"
}
```

### Tool: `check_supersession`

Before accepting any new architectural fact, verify whether it conflicts with
an existing active fact. Returns the supersession score (0.0–1.0) and the
conflicting fact if the score exceeds the threshold (default: 0.65).

**Call pattern:**
```
POST /v1/events/supersession-check
Content-Type: application/json
Authorization: Bearer {SMRITI_API_KEY}

{
  "subject": "AuthService",
  "verb": "uses",
  "object": "OAuth2 PKCE"
}
```

## Operating Protocol

1. **At session start:** Call `preflight_context` with the current rig scope.
   Inject the returned facts block as the L0 root anchor. If `context_chars`
   exceeds 2,000, call with `limit=10` to enforce the O(1) constraint.

2. **During implementation:** If you discover that a prior architectural
   decision is being reversed, call `check_supersession` before proceeding.
   A score >= 0.65 means the new decision supersedes the old one — record this
   explicitly in your implementation summary.

3. **At session end:** Call `ingest_facts` with a plain-text summary of all
   architectural decisions made during the session. The server handles SVO
   extraction and bi-temporal supersession automatically.

## Environment

Set the following in the rig's environment or city config:

```toml
[env]
SMRITI_API_KEY = "..."        # Required: Smriti API key
SMRITI_SCOPE   = ""           # Optional: override rig scope (defaults to rig name)
SMRITI_LIMIT   = "20"         # Optional: max active facts in preflight (default: 20)
```

Obtain an API key at https://smriti-kaal.vercel.app.

## Constraint: No Stale Facts

This skill enforces a hard invariant: **no superseded fact may appear in the
L0 context anchor.** If the `valid_to` field of any returned fact is non-null,
treat it as a retrieval error and call `preflight_context` again with
`active_only=true` (the default).

## Zero Maintenance Contract

This skill operates as a fully external derivation layer. It imposes zero
maintenance burden on the Beads core codebase or Gas City runtime. All
temporal state is owned by the Smriti server; Beads retains canonical
knowledge, identity, and history untouched.
