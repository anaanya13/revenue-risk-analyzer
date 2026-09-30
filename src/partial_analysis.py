"""Conservative row-level quarantine: no fabricated values or silent deduplication."""

def partition_validated(result, uploaded_rows):
    # File-level issues cannot be repaired by selecting rows.
    blocking = result.issues.loc[result.issues.issue.ne("Required value is missing.")]
    blocked = {int(row)-2 for row in blocking.source_row.dropna()}
    if result.issues.source_row.isna().any():
        blocked = set(range(uploaded_rows))
    include = [i for i in range(uploaded_rows) if i not in blocked]
    exclude = [i for i in range(uploaded_rows) if i in blocked]
    usable = result.cleaned_data.iloc[include].copy().reset_index(drop=True)
    quarantined = result.cleaned_data.iloc[exclude].copy()
    usable['source_row'] = [i+2 for i in include]
    quarantined['source_row'] = [i+2 for i in exclude]
    missing = result.issues.loc[result.issues.issue.eq("Required value is missing.")]
    notes = missing.groupby('source_row').field.apply(lambda fields: 'Not recorded: ' + ', '.join(fields))
    usable['data_quality_notes'] = usable.source_row.map(notes).fillna('')
    # These are display/row-reference labels, never inferred business facts.
    used_ids = set(usable.deal_id.dropna())
    for i in usable.index[usable.deal_id.isna()]:
        identifier = 'Unidentified source row ' + str(usable.at[i, 'source_row'])
        while identifier in used_ids:
            identifier += ' (reference)'
        usable.at[i, 'deal_id'] = identifier
        used_ids.add(identifier)
    usable['stage'] = usable.stage.fillna('Not recorded')
    incomplete = int(usable.data_quality_notes.ne('').sum())
    coverage = {'uploaded_rows': uploaded_rows, 'included_rows':len(include), 'excluded_rows':len(exclude),
                'incomplete_rows': incomplete,
                'analysis_scope': 'Partial: included rows with field-level limits' if exclude or incomplete else 'Complete validated file'}
    for key,value in coverage.items():
        usable[key] = value
    return usable, quarantined, coverage
