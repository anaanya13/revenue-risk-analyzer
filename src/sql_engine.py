"""Independent SQL calculations in a private, short-lived in-memory connection."""

import math
from numbers import Integral
from pathlib import Path

import duckdb
import pandas as pd

from src.bottleneck_engine import summarize_bottlenecks
from src.data_cleaner import parse_date
from src.data_validator import validate_data
from src.kpi_engine import calculate_kpis

SQL_DIR = Path(__file__).resolve().parents[1] / "sql"


def query_text(name):
    if name not in ("assess_deals", "kpis", "stages"):
        raise ValueError("Unknown saved query.")
    return (SQL_DIR / (name + ".sql")).read_text()


def sql_analysis(data, analysis_date, threshold):
    """Accept filtered validated data; never read Python-derived risk/aging columns."""
    if isinstance(threshold, bool) or not isinstance(threshold, Integral) or not 1 <= threshold <= 3650:
        raise ValueError("Choose a whole-day threshold from 1 to 3650.")
    reference, error = parse_date(analysis_date)
    if error or pd.isna(reference):
        raise ValueError("Choose a valid analysis date.")
    columns = ["deal_id", "deal_value", "created_date", "last_activity_date", "stage", "status"]
    if not set(columns).issubset(data):
        raise ValueError("SQL analysis requires all mapped required fields.")
    raw = data[columns + (["follow_ups"] if "follow_ups" in data else [])].copy()
    if len(raw):
        result = validate_data(raw, as_of_date=reference)
        if not result.is_valid:
            raise ValueError("Resolve data-quality issues before checking calculations.")
        raw = result.cleaned_data
    if "follow_ups" not in raw:
        raw["follow_ups"] = pd.Series(float("nan"), index=raw.index, dtype=float)
    # Explicit types also let DuckDB bind empty selections and all-null optional data.
    for field in ("deal_id", "stage", "status"):
        raw[field] = raw[field].astype("string")
    for field in ("deal_value", "follow_ups"):
        raw[field] = raw[field].astype("float64")
    for field in ("created_date", "last_activity_date"):
        raw[field] = pd.to_datetime(raw[field])
    with duckdb.connect(":memory:", config={"threads": 1}) as connection:
        connection.register("input_deals", raw)
        connection.execute(query_text("assess_deals"), [reference.date(), int(threshold)])
        cursor = connection.execute(query_text("kpis"))
        kpis = dict(zip([c[0] for c in cursor.description], cursor.fetchone()))
        stages = connection.execute(query_text("stages")).df()
        deals = connection.execute("SELECT deal_id, deal_age_days, days_inactive, is_stalled, risk_severity FROM assessed ORDER BY deal_id").df()
    return {"kpis": kpis, "stages": stages, "deals": deals}


def compare_analysis(data, analysis_date, threshold):
    """Compare all KPIs, stage cells and each deal's age/risk; never hide disagreement."""
    sql = sql_analysis(data, analysis_date, threshold)
    rows = []

    def record(scope, item, python, other):
        if pd.isna(python) or pd.isna(other):
            same = bool(pd.isna(python) and pd.isna(other))
        elif isinstance(python, (str, bool)):
            same = python == other
        else:
            same = math.isclose(float(python), float(other), rel_tol=1e-10, abs_tol=1e-7)
        rows.append({"scope": scope, "item": item, "python_result": python, "sql_result": other, "matches": bool(same)})

    for key, value in calculate_kpis(data).items():
        record("KPI", key, value, sql["kpis"][key])
    python_stages = summarize_bottlenecks(data).set_index("stage")
    sql_stages = sql["stages"].set_index("stage")
    for stage in sorted(set(python_stages.index) | set(sql_stages.index)):
        record("Stage", stage + ": present", stage in python_stages.index, stage in sql_stages.index)
        if stage in python_stages.index and stage in sql_stages.index:
            for column in python_stages:
                record("Stage", stage + ": " + column, python_stages.at[stage, column], sql_stages.at[stage, column])
    python_deals = data.set_index("deal_id")
    for deal in sql["deals"].to_dict("records"):
        for column in ("deal_age_days", "days_inactive", "is_stalled", "risk_severity"):
            record("Deal", str(deal["deal_id"]) + ": " + column, python_deals.at[deal["deal_id"], column], deal[column])
    return pd.DataFrame(rows)
