"""Conservative row-level quarantine: no fabricated values or silent deduplication."""

def partition_validated(result, uploaded_rows):
    # File-level issues cannot be repaired by selecting rows.
    blocked = {int(row)-2 for row in result.issues.source_row.dropna()}
    if result.issues.source_row.isna().any():
        blocked = set(range(uploaded_rows))
    include = [i for i in range(uploaded_rows) if i not in blocked]
    exclude = [i for i in range(uploaded_rows) if i in blocked]
    usable = result.cleaned_data.iloc[include].copy().reset_index(drop=True)
    quarantined = result.cleaned_data.iloc[exclude].copy()
    usable['source_row'] = [i+2 for i in include]
    quarantined['source_row'] = [i+2 for i in exclude]
    coverage = {'uploaded_rows': uploaded_rows, 'included_rows':len(include), 'excluded_rows':len(exclude),
                'analysis_scope':'Partial: valid rows only' if exclude else 'Complete validated file'}
    for key,value in coverage.items():
        usable[key] = value
    return usable, quarantined, coverage
