"""Review-only value evidence for unknown headings; never infer date roles."""
import pandas as pd
from src.data_cleaner import normalize_text, normalize_status, parse_amount, parse_date
from src.import_choices import suggest_outcome


def column_profiles(frame):
    rows = []
    for column in frame:
        values = [v for v in frame[column].head(200) if normalize_text(v) is not None]
        n = len(values)
        numeric = sum(parse_amount(v)[0] is not None and parse_amount(v)[1] is None for v in values)
        dates = sum(pd.notna(parse_date(v)[0]) for v in values)
        outcomes = sum(normalize_status(v) in ('Open','Won','Lost') or suggest_outcome(v) is not None for v in values)
        rows.append({'Source column': str(column), 'Sample values': ' | '.join(str(v)[:80] for v in values[:3]),
                     'Sampled nonblank cells': n,
                     'Number-like cells': numeric, 'Date-like cells': dates, 'Recognized outcome words': outcomes})
    return pd.DataFrame(rows)


def value_candidates(profiles, field):
    """Possible compatible fields only. A date column cannot reveal its event type."""
    role = {'deal_value':'Number-like cells', 'follow_ups':'Number-like cells',
            'created_date':'Date-like cells', 'last_activity_date':'Date-like cells',
            'next_contact_date':'Date-like cells', 'status':'Recognized outcome words'}.get(field)
    if role is None:
        return []
    candidates = profiles.loc[(profiles['Sampled nonblank cells'] > 0) &
                              (profiles[role] / profiles['Sampled nonblank cells'].clip(lower=1) >= .8)]
    return candidates['Source column'].tolist()
