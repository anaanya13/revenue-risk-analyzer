# Project progress

## September 21, 2026: online deployment completed

Published the app to [Streamlit Community Cloud](https://anaanya-revenue-risk-analyzer.streamlit.app/) using [anaanya13/revenue-risk-analyzer](https://github.com/anaanya13/revenue-risk-analyzer), branch `main`, entry point `app.py`, and Python 3.12 selected in Advanced settings. Removed the shared localhost binding (the local start script retains it), and excluded local history, generated HTML, and archived handoff notes from publishing. Settings are saved in [DEPLOYMENT.md](DEPLOYMENT.md).

Verified in the hosted browser: original sample 120 deals / 0 issues; alternate headers 12 deals / 0 issues; messy sample 12 deals / 11 affected rows / 11 issues. The full standardized CSV and issue-report CSV both download successfully. Users can now open a saved web link without starting the local app. Future code changes need publishing to the connected GitHub branch.

## Current milestone

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

The browser check used a temporary local preview on port 8502. Normal startup uses port 8501. No public deployment was created.

Run the saved checks from the project folder with:

```bash
bash scripts/check.sh
```

For the manual walkthrough, start the app and try the original sample, messy test data, alternate column names, and a file upload. Verify that the worksheet selector, mappings, report, and downloads correspond to the selected file.

## Next milestone: agreed calculations

1. Review definitions for active pipeline value, won deal value, win rate, deal age, and inactivity.
2. Decide how an analysis date and inactivity threshold should be selected.
3. Implement calculations against valid records and verify them with small examples whose answers can be checked by hand.
4. Show these measures in the app with plain-language definitions.

The proposed starting rule is an Open deal with **at least 30 days** since its Last Activity Date. This is a proposal for review, not an approved policy or a prediction of loss.

## Later roadmap

Add stage/delay summaries, charts, filters, explainable insights, and recommendations. Introduce DuckDB/SQL after the analysis works. Finish with screenshots and resume/interview material that accurately reflects completed functionality. GitHub and initial deployment are complete.

KPIs, revenue-risk calculations, charts, and SQL are **not completed in this milestone**.

## Where to resume

Use [START_HERE.md](../START_HERE.md) to open the application. Use [project_specification.md](project_specification.md) for the product decisions and limitations. Treat the older PDF as historical background.

Future work should update this record with what changed, how it was checked, and the next unfinished step so progress remains reviewable outside Terminal and chat history.
