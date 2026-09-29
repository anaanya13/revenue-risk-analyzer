"""Planned contact dates are distinct from historical inactivity."""
import pandas as pd


def followup_analysis(data, analysis_date):
    if 'next_contact_date' not in data:
        return None
    result = data.loc[data.status.eq('Open')].copy()
    today = pd.Timestamp(analysis_date).normalize()
    dates = pd.to_datetime(result.next_contact_date)
    result['followup_status'] = 'Upcoming'
    result.loc[dates.isna(), 'followup_status'] = 'Not scheduled'
    result.loc[dates.eq(today), 'followup_status'] = 'Due today'
    result.loc[dates.lt(today), 'followup_status'] = 'Overdue'
    result['days_overdue'] = (today - dates).dt.days.clip(lower=0).astype('Int64')
    return result
