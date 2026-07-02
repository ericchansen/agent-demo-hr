-- Parameterized query templates for the Roster MCP server.
--
-- {where} and {columns} are filled from CODE-CONTROLLED whitelists only
-- (see roster_mcp/db.py: FILTER_COLUMNS / ROSTER_COLUMNS). User-supplied
-- *values* are ALWAYS bound with ? placeholders — never string-concatenated.
-- This is the SQL-injection boundary. Keep it even for a demo.

-- name: count_roster
SELECT COUNT(*) AS n FROM fact_employee WHERE {where};

-- name: list_roster
SELECT {columns} FROM fact_employee WHERE {where} ORDER BY employee_id LIMIT ?;

-- name: export_roster
SELECT {columns} FROM fact_employee WHERE {where} ORDER BY employee_id;

-- name: schema_distinct
SELECT DISTINCT {col} AS v FROM fact_employee WHERE {where} AND {col} IS NOT NULL ORDER BY v;

-- name: org_under
WITH RECURSIVE reports(employee_id, depth) AS (
    SELECT employee_id, 1 FROM fact_employee WHERE manager_id = ?
    UNION ALL
    SELECT f.employee_id, r.depth + 1
    FROM fact_employee f
    JOIN reports r ON f.manager_id = r.employee_id
    WHERE r.depth < ?
)
SELECT {columns} FROM fact_employee
WHERE employee_id IN (SELECT employee_id FROM reports)
  AND {where}
ORDER BY employee_id;
