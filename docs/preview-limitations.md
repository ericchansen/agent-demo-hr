---
title: Current limitations
nav_order: 10
---

# Preview limitations

What the **local scaffold** does *not* do (yet). None of these are bugs — they
are the cloud phases, deferred by design.

- **No live LLM routing.** The orchestrator's prompt→path routing and natural-
  language answers require the live Foundry agent. The eval harness marks these
  `SKIP (requires live orchestrator)`.
- **No Fabric data agent.** Aggregate/attrition answers are validated against
  the seed in the eval, but the NL2SQL data-agent itself is a cloud phase.
- **Mock identity.** The signed-in user is an env var (`ROSTER_DEV_UPN`), not a
  real token. No real OBO exchange; RLS is emulated on `hr_access`.
- **Local file exports.** `export_roster` writes to local disk. The cloud target
  is Blob + SAS URL.
- **No Teams surface.** No SSO, no manifest, no publish.
- **No infra deploy.** `infra/` and `e2e/` are stubs; azd/Bicep and Playwright
  come later.
- **Single snapshot dataset.** "This year" maps to the one snapshot's trailing
  12 months — no time series.
