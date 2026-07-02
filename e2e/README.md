# E2E — notes / TODO (cloud phase)

> **Not built in this scaffold.** End-to-end tests come with the Teams/cloud
> phases. This directory exists so the structure is in place.

## Planned (TODO)
- [ ] Playwright, run against **Microsoft Edge** (not Chrome).
- [ ] Sign in as the EMEA HR-BP persona via Teams SSO.
- [ ] Walk the six demo-script questions (`docs/demo-script.md`).
- [ ] Assert the RLS money-shot: EMEA vs APAC personas get different rows for
      the same export request.
- [ ] Verify the export download (row count + no sensitive columns).

The deterministic roster/RLS behavior is already covered locally by
`orchestrator/eval/run_eval.py` and `roster_mcp/tests/` — the E2E layer adds the
live Teams/Foundry round-trip on top.
