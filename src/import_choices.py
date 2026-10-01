"""Explicit, file-scoped business vocabulary choices; never guess outcomes."""
from src.data_cleaner import normalize_text


def observed_labels(values):
    return sorted({normalize_text(v) for v in values if normalize_text(v) is not None})


def owner_variant_groups(values):
    groups = {}
    for label in observed_labels(values):
        groups.setdefault(label.casefold(), []).append(label)
    return [labels for labels in groups.values() if len(labels) > 1]


def apply_choices(frame, outcomes=None, owners=None, categories=None):
    result = frame.copy(deep=True)
    if any(v not in ('Open', 'Won', 'Lost') for v in (outcomes or {}).values()):
        raise ValueError('Choose Open, Won or Lost for each mapped outcome.')
    if any(field not in ('stage', 'delay_reason') for field in (categories or {})):
        raise ValueError('Category choices support only stage and delay reason.')
    for field, choices in [('status', outcomes), ('sales_rep', owners)] + list((categories or {}).items()):
        if field in result:
            result[field] = result[field].map(lambda v: (choices or {}).get(normalize_text(v), v))
    return result


OUTCOME_SUGGESTIONS = {
    'signed': 'Won', 'contract signed': 'Won', 'successful': 'Won', 'converted': 'Won',
    'not proceeding': 'Lost', 'declined': 'Lost', 'unsuccessful': 'Lost', 'closed unsuccessful': 'Lost',
    'closed - won': 'Won', 'closed - lost': 'Lost', 'won deal': 'Won', 'lost deal': 'Lost',
    'sale completed': 'Won', 'order confirmed': 'Won', 'customer declined': 'Lost',
    'cancelled': 'Lost', 'canceled': 'Lost', 'in progress': 'Open', 'active opportunity': 'Open',
    'awaiting decision': 'Open', 'work in progress': 'Open',
    'ongoing': 'Open', 'in pipeline': 'Open', 'pending': 'Open', 'in negotiation': 'Open',
}


def suggest_outcome(label):
    text = normalize_text(label)
    return OUTCOME_SUGGESTIONS.get(text.casefold()) if text else None


DELAY_SUGGESTIONS = {
    'awaiting documents': 'Missing Documents', 'waiting for paperwork': 'Missing Documents',
    'documents outstanding': 'Missing Documents', 'missing paperwork': 'Missing Documents',
    'customer has not replied': 'Customer Unresponsive', "customer hasn't replied": 'Customer Unresponsive',
    'no response': 'Customer Unresponsive', 'awaiting customer response': 'Customer Unresponsive',
    'price being discussed': 'Pricing / Terms', 'price negotiation': 'Pricing / Terms',
    'pricing discussion': 'Pricing / Terms', 'awaiting internal approval': 'Internal Processing',
    'internal approval pending': 'Internal Processing', 'incorrect details': 'Incorrect Information',
}


def suggest_delay(label):
    text = normalize_text(label)
    return DELAY_SUGGESTIONS.get(text.casefold()) if text else None
