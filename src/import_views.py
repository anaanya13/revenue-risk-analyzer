"""Reviewable suggestions and transformations for each uploaded file."""
from hashlib import sha256
import pandas as pd
import streamlit as st
from src.column_mapper import FIELD_LABELS, mapping_candidates, suggested_alternatives, mapping_basis
from src.data_cleaner import normalize_status
from src.import_choices import observed_labels, owner_variant_groups, suggest_outcome, suggest_delay


def review_import(raw, mapping, source_key, include_categories=False):
    selected = {v for v in mapping.values() if v}
    ignored = [c for c in raw.columns if c not in selected]
    with st.expander('Review column suggestions and coverage', expanded=any(not mapping.get(f) for f in ('deal_id','deal_value','created_date','last_activity_date','stage','status'))):
        from src.import_profiles import column_profiles, value_candidates
        profiles = column_profiles(raw)
        rows = []
        for field, label in FIELD_LABELS.items():
            candidates = mapping_candidates(raw.columns, field)
            reason = (mapping_basis(candidates[0], field) if len(candidates) == 1 else
                      'Several recognized headers; choose manually' if candidates else 'No recognized header; choose manually')
            alternatives = suggested_alternatives(raw.columns, field) if not candidates else []
            examples = {str(c): [str(v)[:80] for v in raw[c].head(3)] for c in candidates or [c for c, _ in alternatives]}
            rows.append({'Possible value-compatible columns (review only)': ', '.join(value_candidates(profiles, field)) if not candidates else 'See recognized headings', 'Selected match basis': mapping_basis(mapping.get(field), field), 'Review-only alternatives': ', '.join(str(c) for c, _ in alternatives) or 'None',
                         'Example values (first three rows)': str(examples), 'Dashboard field': label, 'Recognized candidates': ', '.join(candidates) or 'None',
                         'Your selection': mapping.get(field) or 'Not mapped', 'Suggestion basis': reason})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
        st.caption('Recognized headings use business synonyms, punctuation/case normalization and currency annotations on amount headers. Review-only alternatives use spelling similarity, not verified meaning; inspect the examples before choosing a column. Planned contact dates must not be mapped as historical activity. Your manual choices take priority.')
        st.caption('Value evidence samples up to 200 rows. Numeric/date-like contents do not establish a business meaning; date roles are never chosen from values alone. Full validation runs after Check data.')
        st.dataframe(profiles, hide_index=True, width='stretch')
        st.write('Ignored source columns: ' + (', '.join(ignored) or 'None'))
        st.caption('Ignored columns are not checked, analyzed or included in standardized downloads. They remain in the original workbook.')
    outcomes, owners, audit = {}, {}, []
    if mapping.get('status') in raw:
        with st.expander('Confirm outcome meanings', expanded=True):
            st.caption('Confirm how each nonblank source outcome should be interpreted for this file. Unknown outcomes have no default. Blank outcomes remain unclassified in default analysis; add them later when known. They are excluded from outcome-specific KPIs, not from the record count.')
            labels = observed_labels(raw[mapping['status']])
            proposals = [{'Source outcome': label, 'Suggested meaning': suggest_outcome(label)}
                         for label in labels if suggest_outcome(label)]
            use_suggestions = False
            if proposals:
                st.dataframe(pd.DataFrame(proposals), hide_index=True, width='stretch')
                st.caption('These are proposed synonyms, not verified business facts. Approve them for this file only or choose each meaning below.')
                suggestion_key = sha256((source_key + str(mapping['status'])).encode()).hexdigest()[:20]
                use_suggestions = st.checkbox('Use these suggested outcome meanings for this file', key='synonyms_' + suggestion_key)
            for label in labels:
                known = normalize_status(label)
                if use_suggestions and suggest_outcome(label):
                    known = suggest_outcome(label)
                options = ['Open', 'Won', 'Lost'] if known in ('Open', 'Won', 'Lost') else [None, 'Open', 'Won', 'Lost']
                key = sha256((source_key + str(mapping['status']) + label).encode()).hexdigest()[:20]
                target = st.selectbox('Outcome: ' + label, options,
                    index=options.index(known) if known in options else 0,
                    format_func=lambda v: 'Choose meaning' if v is None else v, key='outcome_' + key + str(use_suggestions))
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
            all_owners = observed_labels(raw[mapping['sales_rep']])
            st.markdown('**Other names for the same owner**')
            st.caption('For aliases beyond capitalization, select the source names and the name to use. Confirm they represent the same person; no fuzzy merge is applied automatically.')
            custom_key = sha256((source_key + str(mapping['sales_rep'])).encode()).hexdigest()[:20]
            aliases = st.multiselect('Owner aliases to combine', all_owners, key='owner_aliases_' + custom_key)
            canonical = st.selectbox('Use this owner name', [None] + all_owners,
                                     format_func=lambda v: 'Choose a name' if v is None else v,
                                     key='owner_canonical_' + custom_key)
            if aliases and canonical:
                for label in aliases:
                    owners[label] = canonical
                    audit = [row for row in audit if not (row['Field'] == 'Owner' and row['Source label'] == label)]
                    audit.append({'Field':'Owner','Source label':label,'Confirmed value':canonical})
    categories = {}
    for field in ('stage', 'delay_reason'):
        if mapping.get(field) not in raw:
            continue
        with st.expander('Combine equivalent ' + FIELD_LABELS[field].lower() + ' labels'):
            labels = observed_labels(raw[mapping[field]])
            st.caption('Different wording can split summaries. Select labels only when they mean the same thing for your company. Outcomes are confirmed separately; no rows are merged.')
            variants = owner_variant_groups(raw[mapping[field]])
            if variants:
                st.write('Capitalization/spacing variants to review: ' + '; '.join(' / '.join(g) for g in variants))
            key = source_key + field + str(mapping[field])
            choices = {}
            if field == 'delay_reason':
                proposals = {label: suggest_delay(label) for label in labels if suggest_delay(label)}
                if proposals:
                    st.dataframe(pd.DataFrame([{'Source label': k, 'Suggested delay group': v} for k,v in proposals.items()]), hide_index=True, width='stretch')
                    if st.checkbox('Use these suggested delay meanings for this file', key='delay_meanings_' + key):
                        choices.update(proposals)
                from src.explanations import PLAYBOOKS
                targets = sorted(set(labels) | {name.title() for name in PLAYBOOKS})
            else:
                targets = labels
            aliases = st.multiselect('Labels to combine: ' + FIELD_LABELS[field], labels, key='category_alias_' + key)
            canonical = st.selectbox('Use this label: ' + FIELD_LABELS[field], [None] + targets,
                                     format_func=lambda v: 'Keep separate' if v is None else v, key='category_target_' + key)
            if aliases and canonical:
                choices.update({alias: canonical for alias in aliases})
            if choices:
                categories[field] = choices
                audit.extend({'Field': FIELD_LABELS[field], 'Source label': alias, 'Confirmed value': value} for alias, value in choices.items())
    return (outcomes, owners, audit, ignored, categories) if include_categories else (outcomes, owners, audit, ignored)


def show_coverage(mapping, ignored):
    st.write('Checked fields: ' + ', '.join(FIELD_LABELS[k] for k, v in mapping.items() if v))
    st.write('Ignored source columns: ' + (', '.join(ignored) or 'None'))
    st.caption('Passing means mapped records meet the implemented completeness, format, uniqueness and date rules. It does not verify business truth, identity, currency consistency or ignored columns. Confirmed outcomes and owner choices affect the analysis; the source workbook is unchanged.')
    if mapping.get('next_contact_date'):
        st.caption('Next Contact may be blank or in the future. A supplied date must be valid and cannot precede creation. A past planned contact is overdue, not a validation error.')
    else:
        st.caption('Next Contact is not mapped: planned-contact dates and overdue follow-ups are not checked or analyzed.')
