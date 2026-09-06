{{/*
smriti-anchor.template.md
=========================
Inject this fragment into any Gas City worker agent prompt to enforce O(1)
root context resolution via the Smriti temporal memory layer.

Usage in an agent prompt.template.md:
  {{ template "smriti-anchor" . }}

This fragment:
  1. Retrieves the active S-V-O fact set for the current rig scope (<2k chars).
  2. Asserts a zero-tolerance invariant: no superseded fact enters the prompt.
  3. Instructs the agent to call ingest_facts at session end.
*/}}

## Active Context (Smriti L0 Root Anchor)

Before beginning any implementation work, resolve the active architectural
context for this rig by calling the Smriti preflight endpoint:

```
GET https://spy9191-chronos-api-backend.hf.space/v1/events/active
  ?scope={{ .RigName }}
  &limit=20
  &active_only=true
Authorization: Bearer {{ .Env.SMRITI_API_KEY }}
```

This call is mandatory. Do not proceed until it returns successfully.

**Invariants you must enforce:**

- The returned `context_chars` value MUST be ≤ 2,000 characters.
  If it exceeds this, re-call with `limit=10`.
- Every returned fact MUST have `valid_to: null`.
  If any fact has a non-null `valid_to`, discard it — it is a superseded fact
  and must not influence your implementation decisions.
- If the endpoint is unreachable, log the failure and proceed without the
  anchor, but record `SMRITI_UNAVAILABLE` in your implementation summary.

**Treat the returned facts as ground truth for this session.**
If your implementation contradicts any active fact, call
`POST /v1/events/supersession-check` before proceeding and record the result.

At session end, call:

```
POST https://spy9191-chronos-api-backend.hf.space/v1/events/ingest
Content-Type: application/json
Authorization: Bearer {{ .Env.SMRITI_API_KEY }}

{
  "source_id": "{{ .RigName }}",
  "scope": "{{ .RigName }}",
  "raw_text": "<plain text summary of all architectural decisions made this session>"
}
```

This closes the bi-temporal loop and ensures the next session inherits only
valid, non-stale context.
