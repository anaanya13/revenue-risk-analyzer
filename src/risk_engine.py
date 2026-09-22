"""Explainable inactivity rules; these flags measure exposure, not loss probability."""

from math import ceil
from numbers import Integral

import pandas as pd

from src.data_cleaner import parse_date
from src.data_validator import REQUIRED_FIELDS, validate_data

RISK_LEVELS = ("Low", "Medium", "High", "Critical")
AGE_BUCKETS = ("0–30 days", "31–60 days", "61–90 days", "91+ days")


def assess_deals(frame, analysis_date, stalled_days=30):
    """Validate the whole snapshot, then annotate a copy before any filtering.

    Open deals: Medium starts at ceil(T/2), High at T, Critical at 2T.
    High and Critical are stalled. At T=1 the Medium interval is empty.
    Closed records have no age/inactivity assessment because close dates are
    not part of the mapped schema. Their value still contributes to outcome KPIs.
    """
    if isinstance(stalled_days, bool) or not isinstance(stalled_days, Integral) or stalled_days < 1:
        raise ValueError("Stalled threshold must be a positive whole number of days.")
    reference, error = parse_date(analysis_date)
    if error or pd.isna(reference):
        raise ValueError("Choose a valid analysis date.")
    if not set(REQUIRED_FIELDS).issubset(frame.columns):
        raise ValueError("Map all required fields before analysis.")
    if frame.empty:
        data = frame.copy(deep=True)
    else:
        result = validate_data(frame, as_of_date=reference)
        if not result.is_valid:
            raise ValueError("Resolve all data-quality issues before analysis; no records are excluded automatically.")
        data = result.cleaned_data

    active = data["status"].eq("Open")
    for source, target in (("created_date", "deal_age_days"), ("last_activity_date", "days_inactive")):
        dates = pd.to_datetime(data[source])
        data[target] = (reference - dates).dt.days.astype("Int64").where(active)
    inactive = data["days_inactive"]
    data["is_stalled"] = (active & inactive.ge(stalled_days)).fillna(False).astype(bool)
    data["risk_severity"] = pd.Series("Closed", index=data.index, dtype="string")
    data.loc[active, "risk_severity"] = "Low"
    data.loc[active & inactive.ge(ceil(stalled_days / 2)), "risk_severity"] = "Medium"
    data.loc[active & inactive.ge(stalled_days), "risk_severity"] = "High"
    data.loc[active & inactive.ge(2 * stalled_days), "risk_severity"] = "Critical"
    data["age_bucket"] = pd.Series(pd.NA, index=data.index, dtype="string")
    age = data["deal_age_days"]
    for lower, upper, label in ((0, 30, AGE_BUCKETS[0]), (31, 60, AGE_BUCKETS[1]), (61, 90, AGE_BUCKETS[2])):
        data.loc[active & age.between(lower, upper), "age_bucket"] = label
    data.loc[active & age.ge(91), "age_bucket"] = AGE_BUCKETS[3]
    data["analysis_date"] = reference
    data["stalled_threshold_days"] = int(stalled_days)
    return data


def _distribution(data, field, labels):
    from src.kpi_engine import sum_value
    active = data.loc[data["status"].eq("Open")]
    return pd.DataFrame([
        {field: label, "deals": int(active[field].eq(label).sum()),
         "deal_value": sum_value(active.loc[active[field].eq(label), "deal_value"])}
        for label in labels
    ])


def risk_distribution(data):
    return _distribution(data, "risk_severity", RISK_LEVELS)


def aging_distribution(data):
    return _distribution(data, "age_bucket", AGE_BUCKETS)
