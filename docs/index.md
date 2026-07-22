---
title: Home
nav_order: 1
---

# Fabric-first HR agent
{: .no_toc }

A **reference implementation** of a conversational HR analytics agent: one entry
point in Microsoft Teams that answers both *aggregate* questions ("what's the
attrition rate in EMEA?") and *deterministic* ones ("export the active roster
for my region"), with row-returning answers scoped to the signed-in user.

{: .warning }
> **Synthetic data only.** Every employee, name, email, salary, and metric in
> this project is 100% fictional — generated for the imaginary company "Contoso".
> **No real people or PII.** This repo mirrors a real-world architecture pattern;
> it carries none of the underlying data.

## Start here

| Page | What it covers |
|------|----------------|
| [Use case &amp; requirements](use-case.html) | The problem, the two question shapes, and the functional / non-functional requirements. |
| [Architecture](architecture.html) | Every piece — Teams, Foundry orchestrator, the two retrieval paths, Fabric, and identity — with a diagram. |
| [Demo script](demo-script.html) | Six questions that exercise both paths, including the row-level-security money-shot. |
| [Threat model](threat-model.html) &middot; [Identity &amp; RLS](identity-flow.html) | How access control works and what it defends against. |

## The one-sentence version

Aggregate questions route to a **Fabric data agent** (natural-language-to-SQL
over a semantic model); exact list/count/export questions route to a
**deterministic roster tool** — because a data agent is built for a *number*,
not a *full roster export*. The deterministic path enforces the caller's
row-level security server-side; production aggregate queries inherit Fabric's
data permissions.

## Running it locally

The whole roster path runs locally against SQLite with a mock identity — no
cloud required. See the [repository README](https://github.com/ericchansen/agent-demo-hr#quickstart)
for the `clone → install → run` quickstart, and the [Runbook](runbook.html) for
the day-to-day dev loop.
