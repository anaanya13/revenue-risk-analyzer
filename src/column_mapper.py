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
    "next_contact_date": "Next Contact",
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

# Explicit header vocabulary only. Outcomes are confirmed separately.
for _field, _labels in {
    "deal_id": ("opportunity ref",), "deal_value": ("expected contract amount cad", "expected contract amount"),
    "created_date": ("first entered",), "last_activity_date": ("latest touchpoint",),
    "stage": ("where things stand",), "status": ("outcome so far",),
    "sales_rep": ("account handler",), "delay_reason": ("what's holding it up",),
    "follow_ups": ("chases so far",), "lead_source": ("came from",),
    "industry": ("business type",), "product": ("package interested in",),
    "next_contact_date": ("next contact", "next contact date", "next follow up date", "next followup date"),
}.items():
    ALIASES[_field] = ALIASES.get(_field, ()) + _labels



# Recognized business vocabulary; broad/generic words are deliberately avoided
# where they could confuse planned events with historical activity or stage with outcome.
for _field, _labels in {
    'deal_id': ('opportunity identifier', 'opp id', 'opp ref', 'deal reference', 'deal ref', 'record id', 'crm id'),
    'deal_value': ('deal amount', 'contract value', 'contract amount', 'estimated value', 'estimated revenue', 'expected revenue', 'pipeline value', 'sales value'),
    'created_date': ('created on', 'date created', 'creation date', 'opened on', 'opportunity opened', 'record created'),
    'last_activity_date': ('last contacted', 'last contacted on', 'last touch', 'last touch date', 'most recent activity', 'most recent contact', 'last engagement date'),
    'next_contact_date': ('next touchpoint', 'next touch date', 'follow up due', 'follow up due date', 'scheduled follow up', 'next outreach date'),
    'stage': ('deal stage', 'opportunity stage', 'funnel stage', 'sales phase', 'pipeline phase'),
    'status': ('deal outcome', 'opportunity status', 'sales outcome', 'win loss', 'win loss status', 'result'),
    'sales_rep': ('assigned to', 'assigned rep', 'salesperson', 'sales person', 'account executive', 'relationship manager', 'representative'),
    'delay_reason': ('delay cause', 'hold reason', 'stalled reason', 'reason stalled', 'blocker reason', 'bottleneck', 'obstacle'),
    'follow_ups': ('follow ups count', 'followups', 'number of followups', 'contact attempts', 'outreach attempts'),
    'lead_source': ('lead channel', 'source channel', 'marketing channel', 'origin'),
    'industry': ('customer industry', 'business sector', 'vertical'),
    'product': ('service', 'offering', 'solution name', 'product service'),
}.items():
    ALIASES[_field] += _labels


def _heading(text):
    # Currency annotation affects units, not field meaning; never convert amounts.
    return re.sub(r'\b(?:usd|cad|gbp|eur|inr|aud|nzd)\b', '', str(text), flags=re.I)


def suggested_alternatives(columns, field):
    """Review-only spelling suggestions; never silently replace a manual mapping."""
    from difflib import SequenceMatcher
    vocabulary = [_normalize(v) for v in (field, FIELD_LABELS[field]) + ALIASES[field]]
    matches = []
    for column in columns:
        key = _normalize(_heading(column) if field == 'deal_value' else column)
        score = max(SequenceMatcher(None, key, alias).ratio() for alias in vocabulary)
        if len(key) >= 5 and score >= 0.78:
            matches.append((column, score))
    return sorted(matches, key=lambda item: (-item[1], str(item[0])))[:3]


def _normalize(text):
    return re.sub(r"[^a-z0-9]", "", str(text).casefold())


def suggest_mapping(columns):
    """Suggest only unambiguous matches; the user can change every suggestion."""
    return {field: candidates[0] if len(candidates) == 1 else None
            for field in FIELD_LABELS
            for candidates in [mapping_candidates(columns, field)]}


def mapping_candidates(columns, field):
    aliases = {_normalize(v) for v in (field, FIELD_LABELS[field]) + ALIASES[field]}
    return [column for column in columns if _normalize(_heading(column) if field == "deal_value" else column) in aliases or _normalize(column) in aliases]


def mapping_errors(columns, mapping, allow_absent=False):
    errors = []
    for field, label in REQUIRED_FIELDS.items():
        if not mapping.get(field) and not allow_absent:
            errors.append("Choose a column for {}.".format(label))
    if allow_absent and (sum(bool(mapping.get(f)) for f in REQUIRED_FIELDS) < 2
                         or not any(mapping.get(f) for f in ('status', 'deal_value'))):
        errors.append("Map at least two core fields, including Status or Deal Value, to identify a usable pipeline table.")
    selected = [value for field, value in mapping.items() if field in FIELD_LABELS and value]
    for value in selected:
        if value not in columns:
            errors.append("The selected column '{}' is not in this file.".format(value))
    for value, count in Counter(selected).items():
        if count > 1:
            errors.append("'{}' is selected more than once. Use a different column for each field.".format(value))
    return errors


def standardize_columns(frame, mapping, allow_absent=False):
    errors = mapping_errors(frame.columns, mapping, allow_absent=allow_absent)
    if errors:
        raise ValueError(" ".join(errors))
    selected = {field: column for field, column in mapping.items() if field in FIELD_LABELS and column}
    result = frame[list(selected.values())].rename(
        columns={column: field for field, column in selected.items()}
    ).copy()

    if allow_absent:
        for field in REQUIRED_FIELDS:
            if field not in result:
                result[field] = None
    return result
