# Streamlit deployment

**Action plans and SQL verification deployed and verified on September 22, 2026.**

- App: [Revenue Risk Analyzer](https://anaanya-revenue-risk-analyzer.streamlit.app/)
- Code: [anaanya13/revenue-risk-analyzer](https://github.com/anaanya13/revenue-risk-analyzer)
- Hosting dashboard: [Streamlit Community Cloud](https://share.streamlit.io/)

## Deployment settings

| Setting | Value |
| --- | --- |
| Repository | anaanya13/revenue-risk-analyzer |
| Branch | main |
| Main file | app.py |
| Python selected | 3.12 |
| Dependencies | Root requirements.txt |
| Secrets | None required by this version |

The shared configuration does not force a localhost address. The optional local start script still uses localhost.

## Midnight & Teal visual refresh

Published the navy/teal presentation, four workflow tabs, sidebar filters, KPI cards, coordinated charts and priority badges. The live sample Dashboard rendered correctly and the Verification tab returned all 555 comparisons agreeing. The local suite passes 71 tests, including two new navigation/state checks. Screenshot examples are saved in the gallery. The underlying calculation engines and data formats are unchanged. Final GitHub checks passed on both Python 3.9 and 3.12 in [run 6](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/35796468337). The finished live previews were saved on September 23 with the fixed September 22 sample analysis date.

## Version 1.0 release verification

The in-app quick guide is deployed. A real Excel upload and the final live SQL comparison were verified. The code remains connected to GitHub main, with the same Streamlit entry point and dependencies. The complete 69-test suite also passes in GitHub on both Python 3.9 and 3.12; see [Project checks run 2](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/35707160241).

The workflow checks relevant code/query/data/dependency changes with read-only repository permissions. It does not deploy or block deployment. Documentation and screenshot-only commits do not rerun the calculation suite. Full release and scope details are saved in [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

## Previous milestone verification

The action-plan cards rendered with supporting counts, values and next steps. The action-plan CSV and calculation-check CSV both downloaded. At the September 22 sample date and 30-day threshold, the independent SQL check reported **all 555 comparisons agree**. Increasing the threshold to 3650 changed the suggestions to the no-stalled explanation and removed the earlier check result; the 30-day default was restored.

The complete local suite now has **69 passing tests** on Python 3.9.13. The hosted smoke check above uses Python 3.12 and DuckDB 1.4.5. Saved queries are published in `sql/`; the in-memory SQL engine does not create a database file or retain uploads. Core dependencies and the original workflow remain in place.

## Previous analytics verification

The analytics update is live. At analysis date September 22, 2026, the hosted sample showed 120 deals, 70 Open, 27 Won, 23 Lost, 54% win rate, and Open pipeline value 3,102,500. With a 30-day threshold, 14 stalled deals had a combined value of 647,000. A 3650-day threshold recalculated stalled count/value to zero without removing records. Clearing a filter showed no matches; Reset filters restored all 120. The filtered-analysis download succeeded, and the charts and stage summaries rendered.

All 50 automated tests pass locally on Python 3.9.13. These include the original validation/upload/export checks plus 23 new calculation and analytics interaction cases. Hosted browser verification uses the deployed Python 3.12 environment; the full unittest suite was run locally.

The initial deployment also verified alternate headers (12 deals, zero issues), messy data (12 deals, 11 affected rows/issues), and standardized/issue CSV downloads.

## Published files

The current app, source modules, requirements, Streamlit configuration, synthetic data, tests, scripts, and current documentation are published. The private local environment, secrets, private uploads, local history, generated START_HERE.html, and archived chat handoff stay local. Git-based publishing respects .gitignore; browser uploads must explicitly select the intended files.

## Future changes

Open the app's saved link to use it. Request changes in this project task. Changes must be published to the connected GitHub main branch before Streamlit updates; editing local files alone does not change the hosted app.

Initial publishing used GitHub's browser interface. This local folder has not been initialized as a Git checkout or configured with push credentials. Future updates can use the same authenticated browser interface, or set up a local Git connection when needed. The deployed app already uses the remote repository.

Official instructions: [Deploy on Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
