# Project progress

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

## Next unfinished work

1. Add broader explainable recommendations with supporting counts and values; the current dashboard already identifies stages with the highest stalled value.
2. Introduce DuckDB/SQL equivalents and check agreement with the Python calculations.
3. Add suitable close dates or stage-event history before attempting time-to-close, historical trends, or time-in-stage analysis.
4. Prepare portfolio screenshots, a demonstration walkthrough, and truthful resume/interview material.

The application has no database, saved upload history, machine-learning loss prediction, or application-level user accounts. Missing optional data does not create invented results.

## Where to resume

Use [START_HERE.md](../START_HERE.md) to open and explore the app. The [specification](project_specification.md) records implemented definitions and limitations. The historical PDF describes an earlier concept.
