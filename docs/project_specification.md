# Project specification

## Purpose

Build a reusable application that accepts a team's sales-pipeline file and helps identify stalled opportunities and operational bottlenecks. It is intended to become a portfolio project the owner can demonstrate and explain in interviews.

The user specifically chose automated analysis of uploaded company data over a single dashboard tied to one prepared dataset. Development should remain understandable to someone beginning Python: keep the work saved in files and provide short, practical instructions for running it.

The motivating business question is: **Which deals need attention, and how much potential value is associated with operational delays?** This is a proposed business use case, not evidence that the prototype has produced commercial results.

## Completed data preparation

The current application covers:

1. CSV or Excel upload, with worksheet selection for Excel.
2. Built-in original sample, messy test data, and alternate company headers.
3. File preview and row/column counts.
4. Mapping to six required and six optional fields.
5. Date-order and validation-date settings.
6. Data standardization and validation.
7. Row-level issue reporting, downloadable issues, and a cleaned-data download after every row passes.
8. A hosted Streamlit app connected to the project's GitHub repository.

Mapping suggestions must be reviewable by the user. Required fields must be mapped before checking data. A source column should not be assigned to more than one standard field.

Data-quality results must distinguish missing values from malformed values. Invalid records must remain traceable in the issue report. The application does not invent missing information, remove failing rows, or select one copy of a duplicate ID. All records stay in the standardized data, and cleaned export is enabled only when the entire file passes.

See the [data dictionary](data_dictionary.md) for supported fields. The cleaned file preserves all deal rows using the mapped fields and standardized values. Keep the original workbook separately, including any extra unmapped fields.

## Input assumptions

- One row represents one deal; Deal ID identifies that deal.
- Files must be at most 20 MB, have unique nonblank headings in the first row, and contain at least one deal. CSV files must be comma-separated UTF-8; Excel files must be unprotected `.xlsx` workbooks.
- The file describes a snapshot of a pipeline, rather than a history of every stage change.
- All deal values use the same currency. This milestone does not perform currency conversion or verify exchange rates.
- The user confirms how ambiguous day/month dates should be read.
- The validation date is the date against which future-date checks are made; it also controls analytics aging and inactivity. A change requires revalidation and does not reconstruct historical statuses.
- Current Stage is the current workflow step; Status describes whether the deal is open, won, or lost.
- Unmapped additional columns are not automatically incorporated into analysis.

## Implemented analytics definitions

Calculations operate on the fully validated snapshot, then use one shared filtered population for all dashboard results and analysis downloads.

| Measure | Definition |
| --- | --- |
| Deal count | Number of unique records matching the filters |
| Open pipeline value | Sum of Deal Value for Open deals |
| Won / lost deal value | Sum of Deal Value for the respective status |
| Average deal value | Total value divided by all matching deal records |
| Win rate | Won count / (Won + Lost counts); N/A with no closed deals |
| Open deal age | Analysis date minus Created Date in whole days, Open only |
| Days inactive | Analysis date minus Last Activity Date in whole days, Open only |
| Stalled deal | Open and inactive for at least T days; T defaults to 30 and is configurable from 1 to 3650 in the dashboard |
| Revenue at risk | Full value of stalled Open deals |
| Open value at risk | Revenue at risk / Open pipeline value; N/A if the denominator is zero |

With threshold T, Low is inactivity below ceil(T/2); Medium is ceil(T/2) through T−1; High is T through 2T−1; Critical is 2T or more. High and Critical are stalled. T=1 leaves no Medium interval. Closed deals are labeled Closed with blank age and inactivity. Age buckets are 0–30, 31–60, 61–90 and 91+ days. Average age/inactivity use Open deals only; undefined averages are N/A.

Bottleneck tables group Open deals by current stage, recorded delay reason or representative. They show Open/stalled counts, pipeline/exposed value, stalled percentage, average age/inactivity and follow-up coverage/average. Missing group values remain a separate blank group; missing counts are excluded from follow-up averages while recorded zero is included. Missing optional fields produce an explanation instead of a fabricated summary. Groups sort by exposed value then Open value. Stalled deal review sorts by severity, value, then inactivity.

Filters include status, stage, severity, creation-date range (both ends inclusive), and available representative, lead source, industry and product. Filters intersect; clearing a selection means no matches. Reset restores all records. A status or severity filter also changes the win-rate denominator. No matching records displays an explanation. The full standardized export remains unfiltered; filtered analysis includes all matching rows and calculation date/threshold, irrespective of the review-table checkbox.

“Won deal value” is the amount recorded against won deals, not audited or accounting-recognized revenue. A risk flag expresses exposure under a rule; it does not predict loss or calculate expected financial loss.

Keep deal age, inactivity, and time in a stage distinct. Created Date supports deal age. Last Activity Date supports inactivity. Neither establishes how long a deal has occupied its current stage.

## Implemented recommendations and SQL verification

The action plan uses the assessed, filtered rows and never sends messages or edits data. Rules identify Critical deals (at least twice the threshold), stages tied for the greatest stalled value, stalled deals with unavailable owner/reason fields, and Medium deals that are approaching the threshold. Each rule gives counts, values, a next step, and supporting IDs in the download. Tied stages are all included; a combined evidence amount is labeled as combined. Zero-value stalled deals still appear. Closed-only, no-stalled and empty selections are handled explicitly. A rule is an operational review prompt, not evidence of causation or predicted recovery. Overlapping suggestion amounts must not be added.

The optional calculation check uses a separate DuckDB in-memory connection and fixed saved queries. It receives the same selected raw columns, independently derives age, inactivity and severity from the shared date/threshold, and compares every KPI, every stage-summary cell, and each selected deal's age/inactivity/stalled/severity with Python. SQL does not consume Python-derived risk values. Both methods share validation and selected records; this check does not independently validate filtering, source truth, or business policy. Tests separately cover filtering.

Undefined results compare as null. Numeric comparison tolerance is relative 1e-10 or absolute 1e-7; text/categories must agree. The check runs on request and its result clears on the next normal dashboard rerun. Disagreement is visible and never reported as success. The connection is closed after calculation; no uploaded data is saved in a database. See [SQL_ANALYSIS.md](SQL_ANALYSIS.md).

## Later stages

| Stage | Intended result |
| --- | --- |
| KPI and aging calculations — complete | Tested calculations using explicit definitions and valid records |
| Bottleneck views — complete | Open/stalled deal counts and value by stage; delay and follow-up summaries when supplied |
| Interactive dashboard — complete | Charts and filters that recalculate for the uploaded file |
| Insights and recommendations — complete | Explainable text generated from rules, with supporting counts/values |
| SQL — complete | DuckDB queries for selected analysis after the Python app works |
| Portfolio packaging — complete for version 1.0 | GitHub repository, screenshots, clear README, deployment, and truthful resume/interview material |

Optional fields should enable additional views when present. Missing optional fields must not cause fabricated results.

## Limits that affect future analysis

- Current stage alone cannot measure stage residence time, stage-to-stage conversion, or a historical conversion funnel. Those require event history or stage-entry dates.
- Time to close and monthly won-deal trends require suitable close dates. The original sample has an extra Close Date field, but this milestone does not map it.
- Associations between follow-ups, delay reasons, and outcomes do not establish what caused a deal to be lost.
- The prototype has rule-based severity categories and a dashboard, with rule-based review suggestions and an in-memory DuckDB/SQL verification layer, but no predictive risk model, application user accounts, or persistent database. It is deployed on Streamlit Community Cloud.

Initial scope recommendations are to keep machine learning, AI APIs, complex accounts, and cloud infrastructure out of the first working product. Streamlit and Plotly are the application/dashboard tools; the historical Power BI brief records an earlier concept.

## Evidence and history

The original workbook is preserved at `data/sample/revenue_risk_sample_data.xlsx`: 120 synthetic rows, 14 columns, with `Deals` and `Data Dictionary` worksheets. Its status distribution is Open 70, Won 27, Lost 23. Dates extend through September 18, 2026.

The original workbook dictionary called Last Activity Date “Recommended.” The current required-field schema supersedes that designation because inactivity analysis depends on this date.

`docs/project_brief.pdf` is the historical Excel/Power BI brief. `docs/archive/` preserves the original application and the prior handoff. These are background records; current behavior is defined by the working code and this specification.

## KPI and recorded-delay explanations

KPI explanations reuse the filtered KPI engine outputs and display the denominator, plain-language meaning and suggested review. No target, historical trend or good/bad grading is invented. The four status count cards are explained together. Undefined rates/averages remain N/A.

The delay explorer groups selected Open records by their entire recorded reason, preserving blanks. Within-group stalled share is stalled count / Open count; share of exposure is group stalled value / total selected stalled value, undefined when total exposure is zero. Group value/ordering reuse the existing bottleneck calculation. Supporting IDs include stalled Open records only. The exported report includes all selected reason groups with IDs, calculation date, threshold and filters; fraction columns are 0–1.

Mitigations match a small explicit set of labels after case/whitespace normalization. The recorded categories are not merged or split. Unknown/combined labels use a general owner-review checklist; missing reasons prompt clarification. Suggestions do not establish causation, prescribe unapproved commercial/credit decisions, guarantee recovery, or send messages. Users record actions externally and re-upload a changed snapshot to reassess.

## Import decisions and planned contacts (September 29, 2026)

Header suggestions use exact normalized aliases only. Multiple candidates produce no automatic selection; duplicate field assignments remain blocked. Suggestions display their candidates and basis. No source values are used to infer outcome meanings.

Each observed nonblank outcome has a file-scoped selection. Existing known aliases may default to their established meaning; unfamiliar labels default to unconfirmed and remain validation errors until chosen. The source workbook is not rewritten. Owner variants are grouped only by whitespace normalization and case folding, with Keep separate as the default. Selecting a name explicitly maps that group's labels to a common name without combining rows. Decisions and column selections are part of the validation signature, so changes invalidate results and AI context.

Optional next_contact_date uses the selected text-date order, permits nulls and future plans, and rejects malformed dates or dates before creation. It is not constrained to follow the last activity date: an older plan may genuinely be overdue. Follow-up analysis is limited to filtered Open deals. Dates before the analysis date are Overdue; equal dates Due today; later dates Upcoming; blanks Not scheduled. Days overdue is max(analysis date minus planned date, 0), null when not scheduled. Closed deals are excluded. Missing optional mapping is distinguished from zero follow-ups. CSV includes the analysis date. Planned contacts do not change risk severity or revenue at risk.

Validation coverage lists mapped and ignored columns. A pass establishes implemented checks on mapped fields only, not source truth, owner identity, currency consistency or correctness of ignored fields. Original SQL verification coverage is unchanged; follow-up rules are tested separately.

## Guided normalization and in-app repair

Upload and validation are separate states. A successful load displays a tick and file shape; blocked result tabs show the current blocking issue/row counts rather than asking for another upload. Every rerun starts with a fresh import notice, preventing an old source's status from leaking into another source.

A proposed outcome synonym vocabulary covers common business phrases and case/whitespace variants. Suggestions require a per-file approval checkbox, with individual overrides available. They do not change global STATUS_ALIASES or infer missing outcomes. Other owner aliases can be explicitly combined into an observed target name; no row is merged or discarded.

The repair editor exposes the original validation-failing records, with immutable source-row numbers and fixed row count. Only changed mapped cells are applied to a deep copy. All corrections undergo the same complete validation before analysis. Missing or incorrect source truth is not fabricated. A downloadable correction history records source row, field, original mapped value and replacement. Discard restores the mapped input. Correction state is scoped to the source fingerprint, column/outcome/owner choices, date order and analysis date. These changes invalidate previous corrections and results. Session reloads do not provide durable storage; downloads are the preservation mechanism.

## Partial-analysis scope (September 30, 2026)

This supersedes the earlier default whole-file gate. Check data still validates every uploaded row. By default, any row with a blocking mapped-field issue is quarantined; file-level issues block all rows. Both sides of duplicate identifiers are excluded. Usable rows retain original one-based source-row references. No missing amount/date/status is imputed and unresolved optional-field errors also quarantine their rows. Zero usable rows does not produce a dashboard.

Require every row to pass before analysis enables the previous strict behavior. Changing the mode requires Check data again and resets the import/repair context. All result tabs display whole-upload included/excluded counts before sidebar filtering; numbers and suggestions describe the filtered usable subset only. Core SQL verification runs on that same subset. Coverage accompanies standardized/filtered CSV rows, stage/follow-up summaries, action/delay/verification settings, and AI evidence. Excluded-record exports contain standardized values; the issue report preserves original problematic values. Global vocabulary guesses and silent row dropping remain prohibited.


## September 30: field-level missingness

Default analysis retains rows whose only issues are missing required values. Strict validation remains opt-in. Missing amount is unknown: count the row, sum only recorded amounts, and average over non-null amounts (including zero). Missing status remains null and is outside outcome KPIs; Open activity missingness yields Unknown risk and no affirmative stalled flag. Missing creation dates do not contribute to ages. Stage blanks get a display label; missing IDs receive collision-safe source-row references. Raw inputs remain unchanged, and data_quality_notes preserves absent fields. Metric coverage is shown on every result tab and sent in aggregate AI context. Invalid values, unknown nonblank outcomes and duplicate IDs remain quarantined. Date filters explicitly omit unknown creation dates. SQL independently uses the same null semantics.


## Flexible business imports

Header vocabulary covers CRM and business synonyms; normalized currency annotations are accepted on amount headings without converting currency. Unmatched headings get review-only spelling alternatives with examples; ambiguous mappings stay unselected and one-to-one mapping checks remain. Whole core fields may be explicitly marked absent, with at least two mapped core fields including amount or status; resulting nulls follow the missing-value rules. CSV separators may be comma, semicolon, tab or pipe. Outcome proposals and delay-group proposals require per-file approval; custom stage/delay grouping is opt-in and audited. Interpretation changes invalidate results. No semantic model/API call is required for imports. Source workbooks remain unchanged.


## Conversational field recognition

A curated vocabulary and conservative word-combination rules map informal business headings. More than one candidate for a field, or a column matching multiple fields, prevents automatic selection. Manual mappings are preserved; restoring suggestions is an explicit action and invalidates prior results. Review-only profiles sample up to 200 rows per source column and show nonblank counts, sample values, parseable number/date counts and recognized outcome words. Type-compatible alternatives never assign date roles or outcomes automatically. Full validation still runs over the entire selected file.
