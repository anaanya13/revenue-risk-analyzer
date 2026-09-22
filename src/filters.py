"""Shared dashboard filters. Empty selections mean no matching deals."""

import pandas as pd

FILTER_FIELDS = ("status", "stage", "sales_rep", "lead_source", "industry", "product", "risk_severity")


def filter_options(data, field):
    values = sorted(data[field].dropna().unique().tolist())
    return values + ([None] if data[field].isna().any() else [])


def filter_deals(data, selections=None, created_from=None, created_to=None):
    mask = pd.Series(True, index=data.index)
    for field, values in (selections or {}).items():
        if field not in FILTER_FIELDS or field not in data:
            raise ValueError("Unknown or unavailable filter: {}".format(field))
        if values is None:
            continue
        present = [value for value in values if value is not None]
        match = data[field].isin(present)
        if None in values:
            match = match | data[field].isna()
        mask &= match
    if created_from is not None and created_to is not None and pd.Timestamp(created_from) > pd.Timestamp(created_to):
        raise ValueError("Created-date start must be on or before the end.")
    if created_from is not None:
        mask &= data["created_date"].ge(pd.Timestamp(created_from).normalize())
    if created_to is not None:
        mask &= data["created_date"].lt(pd.Timestamp(created_to).normalize() + pd.Timedelta(days=1))
    return data.loc[mask].copy()
