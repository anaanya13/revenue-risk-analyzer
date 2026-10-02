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



# Conversational export headings. These map fields, not business outcomes.
for _field, _labels in {
    'deal_id': ('ref', 'reference', 'reference number', 'record reference'),
    'deal_value': ('rough value', 'rough amount', 'estimated contract size', 'approximate value'),
    'created_date': ('added on', 'date added', 'logged on', 'entered on', 'first logged'),
    'last_activity_date': ('last spoke', 'last spoken', 'last conversation', 'last reached out'),
    'stage': ("where it's at", 'where it is at', 'where we are', 'current step'),
    'status': ("how it's going", 'how it is going', 'final outcome', 'deal result'),
    'sales_rep': ('rep', 'handled by', 'responsible person'),
    'product': ('what they want', 'requested solution', 'requested product', 'interested in'),
    'delay_reason': ('stuck on', 'held up by', 'why stalled', 'what is blocking'),
    'lead_source': ('how they found us', 'how they heard about us', 'where they came from'),
    'next_contact_date': ('follow up by', 'followup by', 'contact by', 'reach out by'),
}.items():
    ALIASES[_field] += _labels


def _phrase_match(column, field):
    """Conservative word combinations, never fuzzy auto-selection or date guessing."""
    words = set(re.findall(r'[a-z]+', str(column).casefold()))
    if field == 'deal_value':
        return bool(words & {'amount','value','revenue'} and
                    words & {'deal','opportunity','contract','estimated','expected','potential','rough','approximate','pipeline'} and
                    not words & {'weighted','actual','booked','paid','tax','probability'})
    if field == 'created_date':
        return bool(words & {'created','added','opened','entered','logged'} and
                    words & {'date','on','at'} and not words & {'last','next','closed','updated','modified'})
    if field == 'last_activity_date':
        return bool(words & {'last','latest','recent'} and
                    words & {'spoke','contact','touch','activity','interaction','conversation','engagement'} and
                    not words & {'next','planned','scheduled','closed'})
    if field == 'next_contact_date':
        return bool(words & {'next','planned','scheduled'} and
                    words & {'contact','touch','call','outreach','followup'} and not words & {'last','actual','completed'})
    if field == 'stage':
        return bool(words & {'stage','phase','step'} and words & {'deal','opportunity','pipeline','sales','funnel'})
    if field == 'status':
        return bool(words & {'status','outcome','result'} and words & {'deal','opportunity','sales','pipeline'})
    if field == 'deal_id':
        return bool(words & {'id','ref','reference','identifier'} and words & {'deal','opportunity','record','crm'})
    return False


def mapping_basis(column, field):
    if column is None:
        return 'Not selected'
    aliases = {_normalize(v) for v in (field, FIELD_LABELS[field]) + ALIASES[field]}
    key = _normalize(_heading(column) if field == 'deal_value' else column)
    if key in aliases or _normalize(column) in aliases:
        return 'Recognized heading or synonym'
    if _phrase_match(column, field):
        return 'Recognized combination of field words'
    return 'Manual selection; review its sample values'


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
    suggested = {field: candidates[0] if len(candidates) == 1 else None
                 for field in FIELD_LABELS
                 for candidates in [mapping_candidates(columns, field)]}
    counts = Counter(value for value in suggested.values() if value is not None)
    return {field: value if value is None or counts[value] == 1 else None
            for field, value in suggested.items()}


def mapping_candidates(columns, field):
    aliases = {_normalize(v) for v in (field, FIELD_LABELS[field]) + ALIASES[field]}
    return [column for column in columns if _normalize(_heading(column) if field == "deal_value" else column) in aliases or _normalize(column) in aliases or _phrase_match(column, field)]


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
