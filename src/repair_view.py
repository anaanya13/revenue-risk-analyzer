"""In-session corrections for flagged records; originals never overwritten."""
import pandas as pd
import streamlit as st
from src.data_validator import validate_data
from src.exports import csv_bytes


def apply_repairs(frame, repairs):
    result = frame.copy(deep=True).reset_index(drop=True)
    for position, changes in repairs.items():
        if not isinstance(position, int) or position < 0 or position >= len(result):
            raise ValueError('Correction row is outside this file.')
        for field, value in changes.items():
            if field not in result:
                raise ValueError('Correction field is not mapped.')
            result[field] = result[field].astype(object)
            result.at[position, field] = value
    return result


def repair_and_validate(mapped, signature_key, day_first, as_of):
    key = 'repairs_' + signature_key
    repairs = st.session_state.get(key, {})
    current = apply_repairs(mapped, repairs)
    result = validate_data(current, day_first=day_first, as_of_date=as_of)
    # Build editor from original failed rows so its identity remains stable after applying edits.
    original = validate_data(mapped, day_first=day_first, as_of_date=as_of)
    positions = sorted(set(int(v)-2 for v in original.issues.source_row.dropna()))
    if positions:
        with st.expander('Fix flagged records here — no workbook editing needed', expanded=not result.is_valid):
            st.caption('Edit only values you can verify. Use YYYY-MM-DD for dates and Open, Won or Lost for outcomes. Duplicate IDs need the correct identifiers; missing amounts and dates cannot be safely guessed. Original files stay unchanged. Finish column/outcome/owner choices and the analysis date first; changing those settings starts a fresh correction set. Download cleaned data before leaving the session.')
            source = mapped.iloc[positions].copy().astype('string').fillna('')
            source.insert(0, 'Source row', [p+2 for p in positions])
            source = source.reset_index(drop=True)
            with st.form('repair_form_' + signature_key):
                edited = st.data_editor(source, disabled=['Source row'], hide_index=True,
                                        num_rows='fixed', key='repair_editor_' + signature_key, width='stretch')
                submitted = st.form_submit_button('Apply corrections and recheck')
            if submitted:
                updates = {}
                for index, position in enumerate(positions):
                    changes = {field: edited.at[index,field] for field in mapped.columns
                               if str(edited.at[index,field]) != str(source.at[index,field])}
                    if changes:
                        updates[position] = changes
                st.session_state[key] = updates
                st.rerun()
            if repairs:
                if st.button('Discard these corrections', key='discard_' + signature_key):
                    st.session_state.pop(key, None)
                    st.session_state.pop('repair_editor_' + signature_key, None)
                    st.rerun()
                audit = pd.DataFrame([{'Source row': pos+2, 'Field': field, 'Original mapped value': str(mapped.iloc[pos][field]), 'Replacement': value}
                                      for pos, fields in repairs.items() for field,value in fields.items()])
                st.dataframe(audit, hide_index=True, width='stretch')
                st.download_button('Download correction history',csv_bytes(audit),'correction_history.csv','text/csv',on_click='ignore')
    return result
