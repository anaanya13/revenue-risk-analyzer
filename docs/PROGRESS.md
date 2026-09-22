# Project progress

## September 22, 2026: portfolio version 1.0 completed

Finished the defined snapshot-analysis portfolio release. Added an in-app quick guide, a clear project handover, a case study with truthful resume wording, interview notes, a screenshot gallery, and RELEASE_CHECKLIST.md. The optional local start script now checks every direct application dependency.

The final local suite passes all 69 tests. Automatic GitHub checks also passed on both Python 3.9 and 3.12 in [run 2](https://github.com/anaanya13/revenue-risk-analyzer/actions/runs/35707160241). Checks now run on relevant code, query, data and dependency changes. They report results; they do not gate or perform Streamlit deployment.

Verified a real upload of the original Excel workbook, retained all 120 rows, and confirmed the live calculation check still reports all 555 comparisons agreeing. Captured the live app, KPI, recommendation, risk and verification views using synthetic data for portfolio evidence.

The owner has no required coding or setup steps. Remaining personal steps are the short walkthrough, practicing the explanation, and reviewing resume wording against their actual role. Close-date analysis, stage history, accounts and persistent storage are optional future extensions requiring additional requirements/data, not unfinished version-1 features.

## September 22, 2026: action plans and independent SQL verification

Added an explainable action plan with Critical-deal reviews, tied highest-exposure stages, missing-owner/reason prompts, and Medium-risk watch items. Every suggestion has a supporting count/value, next step, and downloadable deal IDs. Filters and threshold changes rebuild the plan; overlapping values are explicitly not additive. Closed-only and no-stalled selections receive appropriate explanations.

Added three saved SQL queries and an independent DuckDB calculation engine. The optional **Run calculation check** independently recomputes age/risk from raw selected columns, all 15 KPIs, and current-stage summaries. It compares values, displays disagreement, and exports a report with the settings and filters. Each check uses a fresh in-memory connection and does not persist uploads. The existing dashboard remains usable if the check cannot finish.

**69 automated tests pass locally**: 50 existing tests plus 19 new recommendation, SQL, and interface tests. New coverage includes exact supporting IDs/amounts, missing optional columns, tied/zero-value stages, filter/threshold changes, empty/Open/closed populations, decimal amounts, the original sample, SQL-like input labels, deliberate disagreement, and error handling. DuckDB 1.4.5 is pinned alongside the existing dependencies.

Saved beginner instructions in START_HERE.md, technical definitions in SQL_ANALYSIS.md and project_specification.md, and a portfolio demonstration in DEMO_WALKTHROUGH.md. Published to the existing Streamlit app and verified in the hosted Python 3.12 environment. The September 22 sample produced 3 Critical deals worth 138,000, a Documentation-stage review covering 5 stalled deals worth 180,000, and 20 Medium deals worth 799,000. Both action-plan and calculation-report downloads succeeded. The SQL check reported all 555 comparisons agreeing. Changing the threshold to 3650 showed the no-stalled explanation and cleared the old check result; the default 30 days was restored.

## September 22, 2026: analytics milestone completed and deployed

Implemented the KPI engine, Open-deal age and inactivity, a configurable stalled threshold (default 30 days), revenue-at-risk exposure, four severity categories, and bottleneck summaries by current stage, recorded delay reason, and representative. Added dashboard cards, charts, filters, a prioritized deal list, and filtered-analysis/stage-summary CSV downloads. Existing uploads, worksheet selection, mapping, validation and full standardized downloads remain available.

Definitions are saved in [project_specification.md](project_specification.md). High and Critical Open deals are stalled; revenue at risk is their full value, not expected loss. All dashboard sections use the same filtered population. A file must pass validation in full before analytics become available.

**50 automated tests pass** on the local Python 3.9.13 environment: the original 27 tests plus 18 calculation tests and 5 analytics interaction tests. Coverage includes hand-calculated KPI examples, every risk/age boundary, threshold and date changes, zero values, no closed/Open deals, empty filters, optional missing data, group reconciliation, source preservation, download metadata, filter reset, and validation blocking. The sample retains all 120 rows, with 70 Open, 27 Won, 23 Lost, and a 54% win rate before filtering.

New implementation files: `src/kpi_engine.py`, `src/risk_engine.py`, `src/bottleneck_engine.py`, `src/filters.py`, `src/dashboard.py`. New tests: `tests/test_analytics.py`. Existing interface checks were extended for the added dashboard cards.

Published to the existing [Streamlit app](https://anaanya-revenue-risk-analyzer.streamlit.app/) through GitHub main. Hosted checks on September 22 confirmed: all 120 sample deals retained, Open value 3,102,500, Won value 1,046,000, win rate 54%, and 14 stalled Open deals exposing 647,000 at the 30-day threshold. Setting 3650 days reduced stalled count/value to zero while retaining all 120 deals. Clearing the status filter showed zero matching records; Reset filters restored 120. The filtered-analysis CSV download succeeded. These browser checks are separate from the 50 local automated tests; Streamlit uses Python 3.12.

## September 21, 2026: online deployment completed

Published the app to [Streamlit Community Cloud](https://anaanya-revenue-risk-analyzer.streamlit.app/) using [anaanya13/revenue-risk-analyzer](https://github.com/anaanya13/revenue-risk-analyzer), branch `main`, entry point `app.py`, and Python 3.12 selected in Advanced settings. Removed the shared localhost binding (the local start script retains it), and excluded local history, generated HTML, and archived handoff notes from publishing. Settings are saved in [DEPLOYMENT.md](DEPLOYMENT.md).

Verified in the hosted browser: original sample 120 deals / 0 issues; alternate headers 12 deals / 0 issues; messy sample 12 deals / 11 affected rows / 11 issues. The full standardized CSV and issue-report CSV both download successfully. Users can now open a saved web link without starting the local app. Future code changes need publishing to the connected GitHub branch.

## Previous milestone

**Organize the project and complete upload, mapping, and data validation.**

The project began as a resume/dashboard concept, then changed to a reusable application that analyzes a company's uploaded file. The current milestone establishes a reliable starting dataset for that future analysis.

## Work included in this organization pass

- Keep one application entry point, `app.py`, and separate reusable data-processing code into `src/`.
- Preserve the original app and previous handoff in `docs/archive/`.
- Preserve the original 120-deal synthetic workbook and historical project brief.
- Provide CSV/Excel upload, worksheet selection, built-in test datasets, preview, and column mapping.
- Add date settings, validation, row-level issue reporting, and cleaned-data downloads.
- Record package requirements and provide scripts to start the app and run checks.
- Save a beginner guide, current specification, data dictionary, and this progress record.

## Verification results

Verified on **September 19, 2026**, using the existing Python 3.9.13 environment and the package versions in `requirements.txt`.

- **27 automated tests pass**: 15 cleaning/validation cases, 8 file/mapping/export cases, and 4 app interaction cases.
- Original workbook: **120 deals, 0 issues**, with every record retained.
- Alternate company headers: **12 deals, 0 issues**. Leading-zero IDs, currency formatting, and status aliases are handled.
- Deliberately messy file: **12 deals, 11 affected rows, 11 issues** at a September 19, 2026 validation date. See `data/test/README.md` for the expected problems.
- Tested empty/corrupt files, blank/duplicate headers, missing/invalid values, duplicate IDs, date order, numeric date serials, reversed/future dates, and optional follow-up counts.
- Tested worksheet selection, duplicate mappings, CSV export, and clearing previous results when the source or mapping changes. The full cleaned download is unavailable while any row fails.
- Started the application locally and checked the browser interface with the sample data: it displays 120 deals checked and zero issues.

The browser check used a temporary local preview on port 8502. Normal startup uses port 8501. No public deployment existed at that earlier check; the September 21 deployment above supersedes this.

Run the saved checks from the project folder with:

```bash
bash scripts/check.sh
```

For the manual walkthrough, start the app and try the original sample, messy test data, alternate column names, and a file upload. Verify that the worksheet selector, mappings, report, and downloads correspond to the selected file.

## Version 1.0 handover and optional extensions

The version-1 technical and portfolio deliverables are complete. See [PROJECT_HANDOVER.md](PROJECT_HANDOVER.md) for the owner's short checklist and [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) for verification evidence.

Optional extensions require suitable inputs: close dates for time-to-close/trends, event history for time-in-stage/conversion, or defined retention/access needs before persistent storage and accounts. The current app makes none of those claims.

## Where to resume

Use [START_HERE.md](../START_HERE.md) to open and explore the app. The [specification](project_specification.md) records implemented definitions and limitations. The historical PDF describes an earlier concept.
