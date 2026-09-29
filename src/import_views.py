"""Reviewable suggestions and transformations for each uploaded file."""
from hashlib import sha256
import pandas as pd
import streamlit as st
from src.column_mapper import FIELD_LABELS, mapping_candidates
from src.data_cleaner import normalize_status
from src.import_choices import observed_labels, owner_variant_groups


def review_import(raw, mapping, source_key):
    selected = {v for v in mapping.values() if v}
    ignored = [c for c in raw.columns if c not in selected]
    with st.expander('Review column suggestions and coverage'):
        rows = []
        for field, label in FIELD_LABELS.items():
            candidates = mapping_candidates(raw.columns, field)
            reason = ('Recognized header spelling' if len(candidates) == 1 else
                      'Several recognized headers; choose manually' if candidates else 'No recognized header; choose manually')
            rows.append({'Dashboard field': label, 'Recognized candidates': ', '.join(candidates) or 'None',
                         'Your selection': mapping.get(field) or 'Not mapped', 'Suggestion basis': reason})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
        st.caption('Suggestions match a published vocabulary of header spellings, ignoring punctuation and case. They do not inspect values or infer business meanings. Your choices take priority.')
        st.write('Ignored source columns: ' + (', '.join(ignored) or 'None'))
        st.caption('Ignored columns are not checked, analyzed or included in standardized downloads. They remain in the original workbook.')
    outcomes, owners, audit = {}, {}, []
    if mapping.get('status') in raw:
        with st.expander('Confirm outcome meanings', expanded=True):
            st.caption('Confirm how each nonblank source outcome should be interpreted for this file. Unknown outcomes have no default. Blank outcomes must still be corrected in the source.')
            for label in observed_labels(raw[mapping['status']]):
                known = normalize_status(label)
                options = ['Open', 'Won', 'Lost'] if known in ('Open', 'Won', 'Lost') else [None, 'Open', 'Won', 'Lost']
                key = sha256((source_key + str(mapping['status']) + label).encode()).hexdigest()[:20]
                target = st.selectbox('Outcome: ' + label, options,
                    index=options.index(known) if known in options else 0,
                    format_func=lambda v: 'Choose meaning' if v is None else v, key='outcome_' + key)
                if target:
                    outcomes[label] = target
                    audit.append({'Field': 'Outcome', 'Source label': label, 'Confirmed value': target})
    if mapping.get('sales_rep') in raw:
        with st.expander('Review owner-name variants'):
            groups = owner_variant_groups(raw[mapping['sales_rep']])
            st.caption('Only spelling variants differing by capitalization or spaces are suggested. Names stay separate unless you choose a common name. No deal rows are merged.')
            if not groups:
                st.info('No capitalization variants were found. Spaces are trimmed during normal cleaning.')
            for labels in groups:
                key = sha256((source_key + str(mapping['sales_rep']) + repr(labels)).encode()).hexdigest()[:20]
                target = st.selectbox('Use one name for: ' + ' / '.join(labels), [None] + labels,
                                     format_func=lambda v: 'Keep separate' if v is None else v, key='owner_' + key)
                if target:
                    for label in labels:
                        owners[label] = target
                        audit.append({'Field': 'Owner', 'Source label': label, 'Confirmed value': target})
    return outcomes, owners, audit, ignored


def show_coverage(mapping, ignored):
    st.write('Checked fields: ' + ', '.join(FIELD_LABELS[k] for k, v in mapping.items() if v))
    st.write('Ignored source columns: ' + (', '.join(ignored) or 'None'))
    st.caption('Passing means mapped records meet the implemented completeness, format, uniqueness and date rules. It does not verify business truth, identity, currency consistency or ignored columns. Confirmed outcomes and owner choices affect the analysis; the source workbook is unchanged.')
    if mapping.get('next_contact_date'):
        st.caption('Next Contact may be blank or in the future. A supplied date must be valid and cannot precede creation. A past planned contact is overdue, not a validation error.')
    else:
        st.caption('Next Contact is not mapped: planned-contact dates and overdue follow-ups are not checked or analyzed.')
