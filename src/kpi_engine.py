"""KPI definitions for an already assessed, filtered set of deal records."""

import math


def sum_value(values):
    try:
        total = math.fsum(float(value) for value in values)
    except OverflowError as error:
        raise ValueError("The total deal value is too large to calculate. Check the source amounts.") from error
    if not math.isfinite(total):
        raise ValueError("Deal totals must be finite numbers.")
    return total


def _average(series):
    valid = series.dropna()
    return float(valid.mean()) if len(valid) else None


def calculate_kpis(data):
    """Return fractions as 0..1 and undefined rates/averages as None, never zero."""
    active = data.loc[data["status"].eq("Open")]
    won = data.loc[data["status"].eq("Won")]
    lost = data.loc[data["status"].eq("Lost")]
    stalled = active.loc[active["is_stalled"]]
    pipeline = sum_value(active["deal_value"])
    exposure = sum_value(stalled["deal_value"])
    closed_count = len(won) + len(lost)
    total_value = sum_value(data["deal_value"])
    return {
        "deal_count": len(data), "open_deals": len(active), "won_deals": len(won), "lost_deals": len(lost),
        "total_deal_value": total_value, "open_pipeline_value": pipeline,
        "won_deal_value": sum_value(won["deal_value"]), "lost_deal_value": sum_value(lost["deal_value"]),
        "average_deal_value": total_value / len(data) if len(data) else None,
        "win_rate": len(won) / closed_count if closed_count else None,
        "average_open_age": _average(active["deal_age_days"]),
        "average_inactivity": _average(active["days_inactive"]),
        "stalled_deals": len(stalled), "revenue_at_risk": exposure,
        "revenue_at_risk_share": exposure / pipeline if pipeline else None,
    }
