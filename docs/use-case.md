---
title: Use case & requirements
nav_order: 2
---

# Use case & requirements
{: .no_toc }

1. TOC
{:toc}

---

## The problem

HR teams live in spreadsheets and dashboards. A Human Resources Business Partner
(HRBP) supporting a business unit repeatedly needs two very different kinds of
answer about their people, and today gets them from two different places:

- **Broad statistics** — "What's our attrition rate in EMEA this year?",
  "Which team has the highest turnover?", "Average tenure by region?" The answer
  is a number, a rate, or a ranking, and the *exact* underlying rows don't matter.
- **Specific rosters** — "List the active engineers on the Azure Data team in
  EMEA", "Who rolls up to this manager?", "Export everyone in my region to Excel."
  The answer is an exact, reproducible set of employees, and it often needs to
  leave the chat as a **file**.

The goal is a **single conversational entry point in Microsoft Teams** that
handles both, and only ever shows a user the people they are allowed to see.

## Why this needs two paths

It is tempting to point one natural-language agent at the data and call it done.
That fails on the second question shape for a concrete, documented reason:

> A Fabric data agent's responses are **capped at a maximum of 25 rows and 25
> columns** — even when the user explicitly asks to "show all rows."
> — [Fabric data agent limitations, Microsoft Learn](https://learn.microsoft.com/fabric/data-science/concept-data-agent#limitations)

A data agent is superb at turning "what's the attrition rate?" into governed
SQL/DAX over a semantic model and handing back *a number*. It is the wrong tool
for returning **several thousand exact rows as a downloadable file**, which is
exactly what a roster export for a large org rollup requires. So the design
splits retrieval into two paths and routes each question to the right one. See
[Architecture](architecture.html) for how they fit together.

## Users & scale

- **Primary users:** HR Business Partners doing ad-hoc workforce lookups; the
  same interface generalizes to adjacent teams (e.g. Finance) that need
  aggregated headcount and attrition data on demand.
- **Concurrency:** small, team-sized audiences — tens of users, not thousands.
- **Result-set size:** from a handful of employees (one small team) up to
  **several thousand** when a user rolls up an entire large organization. The
  export path must comfortably exceed the aggregate path's row cap.

## Functional requirements

| # | Requirement |
|---|-------------|
| **F1** | A single conversational surface in Microsoft Teams. |
| **F2** | Answer **aggregate / analytical** questions — rates, counts, rankings, trends — in natural language. |
| **F3** | Return **exact, reproducible** employee lists and counts for a given filter (team, org, region, status). |
| **F4** | **Export** large result sets (thousands of rows) to a downloadable **CSV / XLSX** file. |
| **F5** | Walk the **org tree** — everyone who rolls up to a given manager, recursively. |
| **F6** | **Route** each question to the correct path automatically, and handle a mixed request (aggregate *and* list in one turn) by running both. |

## Non-functional requirements

| # | Requirement |
|---|-------------|
| **N1 — Row-level security** | Every answer is scoped to the **signed-in user**. Two users asking the *identical* question receive *different rows*. Scope is decided server-side; a caller can never widen it. |
| **N2 — Sensitive-attribute gating** | Roster lists and exports **exclude** sensitive columns (compensation, performance ratings, demographics) by default. |
| **N3 — Determinism** | The retrieval path is reproducible: the same filter and the same identity always return the same rows. |
| **N4 — No real PII** | This reference runs entirely on **synthetic** data. Real HRIS data is out of scope for the public repo. |
| **N5 — Auditability** | Who asked what, and what scope they were granted, is a recordable event (wired in the hosted phase). |
| **N6 — Reproducible dev loop** | `clone → install → run → eval` works locally with no cloud dependency. |

## Out of scope

- Write-back or any action that mutates HR data — retrieval is **read-only**.
- Real HRIS / lakehouse integration in the public repo (synthetic stand-in only).
- Multi-tenant hosting, SLAs, and production operations (see
  [Local → cloud mapping](production-mapping.html) for what the hosted phase adds).
