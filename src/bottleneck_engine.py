"""Snapshot bottlenecks grouped by current stage, owner or recorded delay."""

import pandas as pd

from src.kpi_engine import sum_value

SUMMARY_COLUMNS = (
    "open_deals", "open_value", "stalled_deals", "revenue_at_risk", "stalled_share",
    "average_open_age", "average_inactivity", "follow_ups_recorded", "average_follow_ups",
)


def summarize_bottlenecks(data, field="stage"):
    if field not in ("stage", "delay_reason", "sales_rep"):
        raise ValueError("Choose stage, delay_reason or sales_rep for a bottleneck summary.")
    if field not in data.columns:
        return None  # Unavailable optional data is different from no open records.
    active = data.loc[data["status"].eq("Open")]
    rows = []
    for label, group in active.groupby(field, dropna=False, sort=True):
        stalled = group.loc[group["is_stalled"]]
        counts = group["follow_ups"].dropna() if "follow_ups" in group else pd.Series(dtype=float)
        rows.append({
            field: label, "open_deals": len(group), "open_value": sum_value(group["deal_value"]),
            "stalled_deals": len(stalled), "revenue_at_risk": sum_value(stalled["deal_value"]),
            "stalled_share": len(stalled) / len(group),
            "average_open_age": float(group["deal_age_days"].mean()),
            "average_inactivity": float(group["days_inactive"].mean()),
            "follow_ups_recorded": len(counts),
            "average_follow_ups": float(counts.mean()) if len(counts) else None,
        })
    return pd.DataFrame(rows, columns=[field] + list(SUMMARY_COLUMNS)).sort_values(
        ["revenue_at_risk", "open_value"], ascending=False, kind="stable", ignore_index=True,
    )
