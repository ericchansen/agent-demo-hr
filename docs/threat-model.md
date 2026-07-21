---
title: Threat model
nav_order: 7
---

# Threat model

Scope: the local scaffold. All data is **synthetic Contoso** — a real
deployment against live HR data raises the stakes on everything below.

## Assets
- Employee roster rows (identity + org).
- Sensitive attributes (gender, age, salary, performance, satisfaction).
- The signed-in user's identity/token.

## Controls in this scaffold

### 1. Row-level security (RLS)
Every Roster MCP tool resolves the caller's scope server-side (`auth_obo.py`)
and ANDs it into every query (`db.build_where`). The MCP surface deliberately
exposes **no** scope parameter, so message/tool arguments cannot widen the
resolved scope.
Negative tests in `roster_mcp/tests/test_rls.py` assert out-of-scope rows are
never returned (must pass 100%).

### 2. Sensitive-attribute gating
Roster list/export columns are a fixed allow-list (`db.ROSTER_COLUMNS`) that
**excludes** gender, age, salary/band, performance, and satisfaction. The
orchestrator instructions also tell the agent to decline sensitive-attribute
requests.

### 3. SQL injection vs prompt injection
- **SQL injection:** the boundary is `roster_mcp/queries.sql` + `db.build_where`
  — column names come from a code-owned whitelist, values are always bound
  parameters, never concatenated. A `'; DROP TABLE …` input is treated as a
  literal (test: `test_filters.py::test_injection_input_is_a_literal`).
- **Prompt injection** (cloud phase): the LLM may be tricked into *asking* for
  out-of-scope data, but RLS makes that harmless — the server still returns
  only in-scope rows. Never let the model supply the RLS scope.

### 4. Audit logging (cloud phase — TODO)
Log per call: `user_upn`, tool name, resolved scope, filters, row_count. This is
the record of *who asked what, and what they were allowed to see*. Not yet
implemented locally; wire it in when the OBO exchange lands (`auth_obo.py` TODO).

## Non-goals / accepted for the demo
- The local identity is a **dev shim** (env-var UPN), not a real token. Real OBO
  is a documented cloud TODO.
- The local web demo deliberately lets its operator choose a synthetic persona;
  it demonstrates RLS behavior but is not an authentication boundary.
- No encryption at rest for the local SQLite file (synthetic data, dev only).
