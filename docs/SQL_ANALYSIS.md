# Independent SQL analysis

The app's optional **Check these calculations → Run calculation check** button compares the existing Python calculations with DuckDB SQL. It is useful for explaining and verifying the portfolio project; the user does not need Terminal or SQL knowledge.

## What is independent

The SQL engine receives the validated, filtered base fields: ID, value, created date, last activity date, stage, status, and optional follow-up count. It does not receive Python's calculated age, inactivity, stalled flag or severity as inputs to the SQL calculations.

1. `sql/assess_deals.sql` derives age, inactivity, stalled flags and severity using parameterized analysis date and threshold.
2. `sql/kpis.sql` computes all 15 KPI outputs, including null-safe rates and averages.
3. `sql/stages.sql` groups Open deals by current stage and calculates the same nine summary measures as Python.
4. `src/sql_engine.py` compares KPI outputs, stage presence and measures, and every selected deal's age/inactivity/stalled/severity.

Both methods share data validation, filters and business definitions. Agreement does not prove that the uploaded data is accurate or that the selected policy is appropriate. SQL equivalence does not imply improved performance; no performance benchmark is claimed.

## Query details

The SQL uses CASE expressions, date differences, aggregate FILTER clauses, grouped aggregates, and NULLIF to avoid dividing by zero. Empty counts and sums are zero; undefined averages and ratios are null. Follow-up averages exclude missing counts while including recorded zero. Floating-point sums use DuckDB `fsum` and Python `math.fsum`.

Comparisons accept relative tolerance 1e-10 or absolute tolerance 1e-7 for numbers, accommodating floating-point arithmetic without ordinary display-rounding differences. Null matches null; categories/text must agree. Tests deliberately corrupt Python-derived results and confirm that the check reports disagreement.

The input DataFrame is registered as a relation in a private in-memory connection. Data values are never interpolated into SQL. The app runs only the saved queries, not uploaded SQL. The date and threshold are bound parameters. Each connection closes after the queries finish. No database file or upload history is written.

## Saved evidence

The comparison download includes each compared item, both results, whether they match, the analysis date, threshold, matching row count, and filter settings. The action-plan download separately includes rule IDs, supporting deal IDs as a JSON list, counts, values, evidence and suggestions. Downloaded source text is protected using the existing CSV export helper.

Changing dashboard controls removes the previous check result; run it again for the new selection. If the check fails to run, the app explains that it is unavailable and leaves the main dashboard usable. Server logs capture the error for debugging.

## Developer verification

Run `bash scripts/check.sh` from the project folder. The complete suite currently has 71 tests. New tests cover hand-calculated results, thresholds 1/3/30/60/61/3650, date changes, empty and closed-only selections, zero values, absent follow-ups, decimal amounts, sample data, filtered populations, query-like labels, deliberate mismatches and UI failure paths.

DuckDB 1.4.5 is pinned in `requirements.txt` and tested locally with Python 3.9.13. The hosted application uses Python 3.12. For implementation background, see the official [DuckDB Python API documentation](https://duckdb.org/docs/lts/clients/python/overview) and [installation instructions](https://duckdb.org/docs/lts/guides/python/install).
