import streamlit as st
from src.followup_engine import followup_analysis
from src.exports import csv_bytes


def render_followups(data, analysis_date):
    st.subheader('Planned follow-ups')
    table = followup_analysis(data, analysis_date)
    if table is None:
        st.info('Map Next Contact in Data setup to see overdue, due-today and unscheduled follow-ups.')
        return
    st.caption('Open deals in the current filters only. Overdue means the planned date is strictly before the analysis date. It does not prove no contact happened and does not change inactivity risk.')
    if table.empty:
        st.info('No Open deals match the current filters.')
        return
    cols = st.columns(4)
    for col, label in zip(cols, ['Overdue', 'Due today', 'Upcoming', 'Not scheduled']):
        col.metric(label + ' follow-ups', int(table.followup_status.eq(label).sum()))
    shown = table[[c for c in ['deal_id','sales_rep','stage','next_contact_date','followup_status','days_overdue'] if c in table]].sort_values('next_contact_date', na_position='last')
    shown = shown.rename(columns={'deal_id':'Deal ID','sales_rep':'Sales Representative','stage':'Current Stage',
        'next_contact_date':'Next Contact','followup_status':'Follow-up status','days_overdue':'Days overdue'})
    st.dataframe(shown, hide_index=True, width='stretch')
    exported = shown.copy()
    exported['Analysis date'] = str(analysis_date)
    st.download_button('Download follow-up plan', csv_bytes(exported), 'follow_up_plan.csv', 'text/csv', on_click='ignore')
