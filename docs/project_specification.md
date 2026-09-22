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

## Later stages

| Stage | Intended result |
| --- | --- |
| KPI and aging calculations — complete | Tested calculations using explicit definitions and valid records |
| Bottleneck views — complete | Open/stalled deal counts and value by stage; delay and follow-up summaries when supplied |
| Interactive dashboard — complete | Charts and filters that recalculate for the uploaded file |
| Insights and recommendations | Explainable text generated from rules, with supporting counts/values |
| SQL | DuckDB queries for selected analysis after the Python app works |
| Portfolio packaging | GitHub repository, screenshots, clear README, deployment, and truthful resume/interview material |

Optional fields should enable additional views when present. Missing optional fields must not cause fabricated results.

## Limits that affect future analysis

- Current stage alone cannot measure stage residence time, stage-to-stage conversion, or a historical conversion funnel. Those require event history or stage-entry dates.
- Time to close and monthly won-deal trends require suitable close dates. The original sample has an extra Close Date field, but this milestone does not map it.
- Associations between follow-ups, delay reasons, and outcomes do not establish what caused a deal to be lost.
- The prototype has rule-based severity categories and a dashboard, but no predictive risk model, broader automated recommendations, SQL layer, application user accounts, or database. It is deployed on Streamlit Community Cloud.

Initial scope recommendations are to keep machine learning, AI APIs, complex accounts, and cloud infrastructure out of the first working product. Streamlit and Plotly are the application/dashboard tools; the historical Power BI brief records an earlier concept.

## Evidence and history

The original workbook is preserved at `data/sample/revenue_risk_sample_data.xlsx`: 120 synthetic rows, 14 columns, with `Deals` and `Data Dictionary` worksheets. Its status distribution is Open 70, Won 27, Lost 23. Dates extend through September 18, 2026.

The original workbook dictionary called Last Activity Date “Recommended.” The current required-field schema supersedes that designation because inactivity analysis depends on this date.

`docs/project_brief.pdf` is the historical Excel/Power BI brief. `docs/archive/` preserves the original application and the prior handoff. These are background records; current behavior is defined by the working code and this specification.
