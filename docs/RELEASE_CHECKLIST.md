# Portfolio version 1.0 release record

Release date: September 22, 2026.

**Status: the defined snapshot-analysis portfolio version is complete and deployed.** Personal demo practice and review of resume wording remain with the project owner. Historical analytics, accounts and persistent storage are optional extensions, not requirements for this release.

## Delivered scope

- [x] CSV/Excel upload, sheet selection, preview and configurable column mapping.
- [x] Whole-file validation and actionable issue reports, with no silently discarded deals.
- [x] Pipeline/outcome KPIs, deal aging, inactivity and configurable stalled rules.
- [x] Severity categories, exposed value and percentage, charts and shared filters.
- [x] Stage bottlenecks and optional owner, delay and follow-up summaries.
- [x] Traceable suggestions and downloadable action plans.
- [x] Independent saved SQL queries, comparison results and report downloads.
- [x] Beginner guide inside the app and saved operating instructions.
- [x] Live Streamlit deployment and published GitHub source.
- [x] Automated checks, portfolio case study, interview notes and demonstration walkthrough.
- [x] Screenshot gallery, handover and clearly documented limitations.

## Test evidence

| Check | Result |
| --- | --- |
| Local Python 3.9.13 suite | 69 tests passed after the final app guidance change |
| GitHub Linux / Python 3.9 | Passed |
| GitHub Linux / Python 3.12 | Passed |
| Final workflow | [Project checks run 2](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/35707160241), success |
| Live Excel upload | Original workbook loaded with 120 rows and 14 columns; validation and dashboard completed |
| Sample SQL comparison | All 555 comparisons agree at September 22, 2026 / threshold 30 / all filters |
| Sample action-plan evidence | 3 Critical deals worth 138,000; Documentation stage 5 stalled deals worth 180,000; 20 Medium deals worth 799,000 |
| Earlier hosted interaction checks | Threshold changes, empty filter/reset, messy-data blocking, alternate headers and downloads verified; see PROGRESS.md |

The GitHub workflow runs on relevant code, query, data or dependency changes, on matching pull requests, or manually. It has read-only repository permissions and does not deploy, write source files or use secrets. Streamlit continues to update from the connected main branch; this workflow is a check, not a deployment gate.

Automated tests cover malformed inputs, duplicate IDs, date rules, missing optional data, threshold boundaries, empty and closed-only selections, floating-point amounts, group reconciliation, recommendation evidence, deliberate Python/SQL disagreement and interface state changes. Passing tests demonstrate these covered cases; the app has not undergone enterprise load testing or evaluation against a live company workflow.

## Reproduce the demo

Open the app, select Try sample data, keep Deals, set the analysis date to September 22, 2026, and click Check data. Leave all filters selected and threshold 30. Expect Open value 3,102,500, Won value 1,046,000, win rate 54%, 14 stalled Open deals and exposed value 647,000. Then run the optional calculation check.

## Boundaries of this release

The app analyzes a snapshot using one currency. It does not predict loss, reconstruct past statuses, measure time in stage, calculate recognized revenue, save uploaded analyses persistently, or send recommendations to sales representatives. No commercial benefit is claimed from the synthetic demonstration.

## Ongoing maintenance

Request changes in the project task, run the saved checks, publish changed files to the connected repository, and verify Streamlit afterward. Update this record and the progress log when behavior changes. Review dependency updates with the checks before publishing them; the top-level dependencies are pinned, while transitive dependencies are resolved at installation.
