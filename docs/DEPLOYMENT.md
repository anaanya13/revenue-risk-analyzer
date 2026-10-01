# Streamlit deployment

**Missing-field records included in default analysis; deployed September 30, 2026.**


## September 30: missing-field inclusion

The hosted app now retains incomplete records, shows field-coverage notes and a review table on every result tab, and independently verifies null-aware calculations. Missing amounts contribute to counts but not monetary sums; averages use recorded amounts. Missing outcomes stay unclassified. Missing Open activity dates give Unknown risk. Duplicate IDs and invalid values remain excluded. Strict whole-file validation is still available.

Tested the supplied excluded-record CSV live: 3 of 7 rows included, all three marked with missing details, 2/3 amounts recorded and one outcome missing. All 37 independent comparisons agreed. Reuploading the full regional workbook replaced that selection. At September 29 with approved outcome meanings, hosted and local calculations include 95/100 rows (46 Open, 27 Won, 21 Lost, one unknown outcome), 11 stalled deals and known-value exposure 250,550. One stalled deal has an unknown amount. All 445 hosted and local comparisons agree. The hosted note shows 94/95 recorded amounts and one missing outcome. The earlier 93/100 record below is historical and superseded.

All 106 automated tests pass locally. [GitHub run 28](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/36786273221) passed on Python 3.9 and 3.12. No original workbook was changed or published, and no paid AI call was made.

## September 30: partial analysis for messy files

Published the default usable-row analysis, coverage labels, excluded-record download and optional strict check. Tested the raw regional workbook in the hosted app at a fixed September 29 analysis date and 30-day threshold. Before approving proposed outcomes, 45 of 100 rows reached Dashboard. After explicit synonym approval, 93 rows were included and seven excluded. Dashboard showed open pipeline 1,282,200, revenue at risk 250,550 and win rate 56.2%, all explicitly limited to included rows. Action plan rendered recommendations and planned follow-ups. Verification returned all 437 comparisons agreeing. The excluded-record CSV download started successfully. Optional strict mode correctly blocked analysis on the seven remaining issues; partial mode was restored afterward.

All 101 local tests passed. [GitHub run 23](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/36785004079) passed on Python 3.9 and 3.12. Uploaded workbooks are unchanged and are not published in the repository. No paid AI call was made. Unresolved records can be corrected in Data setup; unknown outcomes still require confirmation rather than a global business assumption.

## September 23: guidance verification

Verified the guide before loading data, then validated the 120-row synthetic sample. The Dashboard explained the 54% win rate as 27 Won divided by 50 closed deals. In Action plan, selecting Missing Documents showed 8 Open deals, 1 stalled deal, 50,000 exposed value, 12.5% within-group stalled share and 7.7% of selected exposure at September 23 and a 30-day threshold. The document checklist and progress-review instructions rendered, and the delay-guidance CSV download started successfully.

All 79 tests pass locally. [GitHub run 9](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/35927901490) also passed on Python 3.9 and 3.12. Tests include calculation reconciliation, filters, threshold changes, missing reasons and Streamlit guide/explorer workflows. See [KPI_AND_DELAY_GUIDE.md](KPI_AND_DELAY_GUIDE.md) for definitions and the walkthrough.

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

## September 23: optional Ask AI release

Added the fifth Ask AI tab, current-filter aggregate context, private session key entry, explicit sharing consent, summary preview, suggested questions and a bounded conversation. The local suite passes 87 tests with mocked AI responses; no paid live provider request has been made. Full activation requires the visitor's own API key and API account access. See [AI_ASSISTANT.md](AI_ASSISTANT.md).

[GitHub run 12](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/35947097261) passed on both Python 3.9 and 3.12. Streamlit needed a reboot after publishing to replace a cached older dashboard function signature.

After reboot, validated the hosted 120-row sample and opened Ask AI successfully. Confirmed setup instructions, password field, summary preview, sharing disclosure, suggestions and question field render; Ask AI remains disabled without a key and consent. This verifies the deployed interface, not an authenticated provider answer.

## September 29: business mappings and planned follow-ups

Published all five import improvements. The full local suite passes 94 tests. [GitHub run 15](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/36640951222) passed. No source workbooks or private export evidence were published.

Live verification used the original regional workbooks without editing them, at analysis date September 29, 2026. All 13 supported columns were suggested. Signed and Not proceeding remained unconfirmed until explicitly selected as Won and Lost. Corrected data then passed with 100 rows and zero issues; the page identified Client / Business and Internal Comments as ignored. Action plan showed 8 overdue, 1 due today, 39 upcoming and 3 unscheduled Open follow-ups. The follow-up CSV download succeeded. Original independent SQL verification reported all 465 comparisons agreeing.

For the raw workbook, confirmed outcome meanings (including lowercase signed) and reviewed the owner variant group. Keep separate was the default; selecting Mei-Lin Zhao explicitly chose that common spelling. Validation retained seven issues across seven rows, including row 78's Next Contact before creation. No deal rows were merged or dropped. Original files remain unchanged. The earlier baseline test report is preserved as historical evidence and marked as superseded by this release.

## September 29: guided synonym approval and in-app corrections

The full local suite passes 98 tests. An additional local Streamlit integration run used the original raw regional export and only the corrections explicitly documented in the supplied testing notes. Approving suggested outcomes, choosing the owner spelling and applying six documented cell corrections resolved seven flagged rows (both sides of the duplicate are reported), unlocked analysis and produced all 465 agreeing SQL comparisons. Original workbook files were not modified.

Verified on the hosted app: the raw file shows a File uploaded tick, status synonyms are initially unapproved, one checkbox approves the displayed suggestions, seven genuine issues remain, and the correction editor and Apply corrections and recheck control render. Dashboard now explicitly reports that the file is uploaded but blocked by seven issues across seven rows. Synonyms are proposals for the current file, not permanent global business rules. In-app correction application and discard were exercised by the local automated Streamlit tests; no real-world unknown values were guessed.

The hosted corrected workbook also passed with one synonym-approval checkbox and Check data. Dashboard displayed Open pipeline 1,434,650.00 CAD, win rate 57.1% and revenue at risk 292,450.00 CAD. [GitHub run 19](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/36657014578) passed the 98-test release. A final context safeguard resets analysis state when applied cell corrections change.


## Visible exclusion reasons

Verified the live regional Dashboard after outcome approval: 95/100 rows included and a reason table directly beneath the partial-analysis notice. The table retains original invalid values, including created_date = 2026-02-30, both OP-3161 duplicates, the planned-contact date preceding creation, and future historical activity. CSV exports include exclusion_reason and original_flagged_values. All 106 local tests pass; [GitHub run 31](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/36788487625) passed on Python 3.9 and 3.12.


## Flexible company exports

Published broader business-header synonyms, review-only spelling alternatives with examples, explicit absent-core-field handling, outcome/delay vocabulary proposals, manual stage/delay grouping and comma/semicolon/tab/pipe CSV support. Added the fictional data/test/flexible_business_export.csv. All 113 local tests passed; seven focused flexible-import tests also passed after the compatibility adjustment. Import processing does not call a paid AI service or modify source files.

Live verification: the fictional semicolon export uploaded as six rows and nine columns; all six core headings mapped automatically. Approved outcome and delay suggestions retained all six rows, with three incomplete records, 5/6 recorded amounts, one missing outcome and one Open deal lacking activity. At September 29 and a 30-day threshold, win rate was 50%, known-value exposure was 12,000 and the pricing delay selected Commercial clarification guidance. All 59 independent SQL comparisons agreed. [GitHub run 35](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/36824224737) passed on Python 3.9 and 3.12.
