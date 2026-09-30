"""Explicit, file-scoped business vocabulary choices; never guess outcomes."""
from src.data_cleaner import normalize_text


def observed_labels(values):
    return sorted({normalize_text(v) for v in values if normalize_text(v) is not None})


def owner_variant_groups(values):
    groups = {}
    for label in observed_labels(values):
        groups.setdefault(label.casefold(), []).append(label)
    return [labels for labels in groups.values() if len(labels) > 1]


def apply_choices(frame, outcomes=None, owners=None):
    result = frame.copy(deep=True)
    if any(v not in ('Open', 'Won', 'Lost') for v in (outcomes or {}).values()):
        raise ValueError('Choose Open, Won or Lost for each mapped outcome.')
    for field, choices in (('status', outcomes), ('sales_rep', owners)):
        if field in result:
            result[field] = result[field].map(lambda v: (choices or {}).get(normalize_text(v), v))
    return result


OUTCOME_SUGGESTIONS = {
    'signed': 'Won', 'contract signed': 'Won', 'successful': 'Won', 'converted': 'Won',
    'not proceeding': 'Lost', 'declined': 'Lost', 'unsuccessful': 'Lost', 'closed unsuccessful': 'Lost',
    'ongoing': 'Open', 'in pipeline': 'Open', 'pending': 'Open', 'in negotiation': 'Open',
}


def suggest_outcome(label):
    text = normalize_text(label)
    return OUTCOME_SUGGESTIONS.get(text.casefold()) if text else None
