"""Field-level completeness: blank is unknown, never zero or a business outcome."""
import pandas as pd
import streamlit as st


def missing_coverage(data):
    """Count metric inputs in the current selection, independent of file coverage."""
    opened = data.loc[data.status.eq('Open')]
    return {
        'selected_records': len(data),
        'recorded_amounts': int(data.deal_value.notna().sum()),
        'missing_amounts': int(data.deal_value.isna().sum()),
        'missing_outcomes': int(data.status.isna().sum()),
        'open_with_activity_date': int(opened.last_activity_date.notna().sum()),
        'open_without_activity_date': int(opened.last_activity_date.isna().sum()),
        'open_with_created_date': int(opened.created_date.notna().sum()),
        'open_without_created_date': int(opened.created_date.isna().sum()),
    }


def show_missing_coverage(data):
    notes = data.get('data_quality_notes', pd.Series('', index=data.index))
    if not notes.ne('').any():
        return
    coverage = missing_coverage(data)
    st.warning('Included with missing details: {} selected records. Missing means not recorded; it does not prove zero, no activity or no outcome.'.format(int(notes.ne('').sum())))
    st.caption('Amounts are known-value subtotals, excluding blank amounts; an all-blank subtotal displays 0 recorded, not a true zero. Average value uses recorded amounts only. Blank outcomes count toward total records but not Open/Won/Lost or win rate. Open deals without activity dates have Unknown risk; missing creation dates cannot contribute to average age. Risk share uses recorded amounts and may understate exposure when details are missing.')
    st.caption('Current selection: {recorded_amounts}/{selected_records} amounts recorded; {missing_outcomes} outcomes missing; {open_without_activity_date} Open deals lack activity dates; {open_without_created_date} Open deals lack creation dates. Reupload the full updated file and click Check data whenever details become available; it replaces this analysis rather than adding duplicate records.'.format(**coverage))
    with st.expander('Review included records with missing details'):
        columns = [c for c in ('source_row', 'deal_id', 'deal_value', 'status', 'created_date', 'last_activity_date', 'stage', 'data_quality_notes') if c in data]
        st.dataframe(data.loc[notes.ne(''), columns], hide_index=True, width='stretch')
