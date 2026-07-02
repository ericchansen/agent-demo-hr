# Security Policy

## Synthetic data only

This repository contains **100% synthetic, fictional data** for the imaginary
company "Contoso." No real employees, salaries, or PII are present. See the
generator in `data/generate_hr.py`.

## Reporting a vulnerability

This is a public demo scaffold. If you find a security issue in the code
(e.g., a SQL-injection path, an RLS bypass), please open a GitHub issue or
email the maintainer listed in `CODEOWNERS`. Do not include real personal data
in reports.

## Security posture of this demo

- **Parameterized SQL only.** User-supplied filters are bound as parameters,
  never string-concatenated (`roster_mcp/queries.sql`, `roster_mcp/db.py`).
- **Row-level security** is enforced server-side in every tool via the caller's
  resolved scope (`roster_mcp/auth_obo.py`). Out-of-scope rows are never returned.
- **Sensitive attributes** (gender, age, salary, performance, etc.) are excluded
  from roster exports by default.
- The local identity is a **dev shim**. Real On-Behalf-Of (OBO) token exchange
  is a cloud phase — see the TODO in `roster_mcp/auth_obo.py`.
