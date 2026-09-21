"""Translate company headings into one stable set of business fields."""

import re
from collections import Counter

REQUIRED_FIELDS = {
    "deal_id": "Deal ID", "deal_value": "Deal Value", "created_date": "Created Date",
    "last_activity_date": "Last Activity Date", "stage": "Current Stage", "status": "Status",
}
OPTIONAL_FIELDS = {
    "delay_reason": "Delay Reason", "follow_ups": "Follow Ups", "sales_rep": "Sales Representative",
    "lead_source": "Lead Source", "industry": "Industry", "product": "Product",
}
FIELD_LABELS = {**REQUIRED_FIELDS, **OPTIONAL_FIELDS}
ALIASES = {
    "deal_id": ("opportunity id", "opportunity number", "opportunity code", "deal number"),
    "deal_value": ("opportunity amount", "opportunity value", "potential revenue", "amount"),
    "created_date": ("date opened", "open date", "opportunity created date"),
    "last_activity_date": ("last contact", "last contact date", "last activity", "last interaction"),
    "stage": ("pipeline step", "pipeline stage", "sales stage"),
    "status": ("opportunity result", "outcome", "deal status"),
    "delay_reason": ("blocker", "reason for delay"),
    "follow_ups": ("number of follow ups", "followup count", "follow up count"),
    "sales_rep": ("sales rep", "owner", "account owner", "deal owner"),
    "lead_source": ("source", "acquisition channel"), "industry": ("sector",),
    "product": ("solution", "product name"),
}


def _normalize(text):
    return re.sub(r"[^a-z0-9]", "", str(text).casefold())


def suggest_mapping(columns):
    """Suggest only unambiguous matches; the user can change every suggestion."""
    mapping = {}
    for field, label in FIELD_LABELS.items():
        aliases = {_normalize(v) for v in (field, label) + ALIASES[field]}
        matches = [column for column in columns if _normalize(column) in aliases]
        mapping[field] = matches[0] if len(matches) == 1 else None
    return mapping


def mapping_errors(columns, mapping):
    errors = []
    for field, label in REQUIRED_FIELDS.items():
        if not mapping.get(field):
            errors.append("Choose a column for {}.".format(label))
    selected = [value for field, value in mapping.items() if field in FIELD_LABELS and value]
    for value in selected:
        if value not in columns:
            errors.append("The selected column '{}' is not in this file.".format(value))
    for value, count in Counter(selected).items():
        if count > 1:
            errors.append("'{}' is selected more than once. Use a different column for each field.".format(value))
    return errors


def standardize_columns(frame, mapping):
    errors = mapping_errors(frame.columns, mapping)
    if errors:
        raise ValueError(" ".join(errors))
    selected = {field: column for field, column in mapping.items() if field in FIELD_LABELS and column}
    return frame[list(selected.values())].rename(
        columns={column: field for field, column in selected.items()}
    ).copy()
