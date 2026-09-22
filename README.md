# Revenue Risk & Deal Bottleneck Analyzer

A portfolio application that helps teams turn their own sales-pipeline spreadsheets into useful analysis of stalled deals and operational delays.

Upload or choose a sample, match columns, and check the entire file before exploring pipeline KPIs, deal aging, inactivity risk, and bottlenecks. Interactive filters, configurable stalled thresholds, and downloadable analyses make every result reviewable.

## Open the app online

[Open Revenue Risk Analyzer](https://anaanya-revenue-risk-analyzer.streamlit.app/)

The app is hosted on Streamlit Community Cloud. Bookmark this link; you do not need Terminal or a running laptop to use it. Choose **Try sample data**, then **Check data** to explore the current build.

The code and version history are saved in [the GitHub repository](https://github.com/anaanya13/revenue-risk-analyzer). Request future changes in the project task; publishing changes to GitHub updates the hosted app.

## Run locally (optional)

Open Terminal and run:

```bash
cd ~/Desktop/revenue-risk-analyzer
bash scripts/start.sh
```

Keep Terminal open while using the app. If your browser does not open automatically, visit [http://localhost:8501](http://localhost:8501). To stop, return to Terminal and press **Control + C**.

For a guided first visit and troubleshooting, read [START_HERE.md](START_HERE.md).

## What works in this milestone

- Upload a CSV or Excel `.xlsx` file; choose the worksheet for Excel files.
- Try the original sample, a deliberately messy test file, or a file with different column names.
- Review the file and match its columns to the app's standard fields.
- Choose how dates should be interpreted and the date used for validation.
- Run data checks and review issues by row. Download the issue report, then download cleaned data once every row passes.

- View pipeline and outcome KPIs, aging charts, Low/Medium/High/Critical inactivity categories, and revenue at risk.
- Adjust the stalled threshold (default 30 days), apply dashboard filters, and review stage, representative, and recorded-delay summaries.
- Download filtered deal analysis with calculation settings, or the stage summary.

The checker keeps every row. It does not silently remove invalid or duplicate records to make a file pass.

The app supports compatible sales-pipeline data. Column mapping helps it understand different headers; it does not make every arbitrary spreadsheet suitable for analysis.

## Data the app needs

Required: **Deal ID, Deal Value, Created Date, Last Activity Date, Current Stage, Status**.

Optional: **Delay Reason, Follow Ups, Sales Representative, Lead Source, Industry, Product**.

Read the [data dictionary](docs/data_dictionary.md) for meanings and examples. The original synthetic workbook contains 120 deals, 14 columns, and two worksheets: `Deals` and `Data Dictionary`.

## Where things are saved

| Item | Purpose |
| --- | --- |
| `app.py` | The application you run |
| `src/` | Reusable data-processing code |
| `scripts/start.sh` | Starts the application using this project's Python environment |
| `scripts/check.sh` | Runs the project checks |
| `requirements.txt` | Records the Python packages needed by the project |
| `data/sample/revenue_risk_sample_data.xlsx` | Original synthetic workbook |
| `data/test/` | Deliberately messy data and alternate column names for testing |
| `docs/project_specification.md` | Product scope, definitions, and planned stages |
| `docs/PROGRESS.md` | Work record and next milestone |
| `docs/project_brief.pdf` | Historical brief for the earlier Excel/Power BI concept |
| `docs/archive/` | Original application and handoff text, kept locally and excluded from GitHub |
| `.venv/` | Local Python environment; do not edit its files |

The historical brief is background material. The [current specification](docs/project_specification.md) describes the automated application being built now.

## Check the project

From the project folder:

```bash
bash scripts/check.sh
```

The verification record is in [PROGRESS.md](docs/PROGRESS.md).

## What comes next

The analytics milestone has 50 passing automated tests. Broader explainable recommendations, DuckDB/SQL, close-date or stage-history analysis, and resume packaging remain. GitHub publishing and Streamlit deployment are in place.

This is a hosted portfolio project using synthetic examples. It has not been evaluated with a live company's workflow. A flagged deal represents pipeline exposure under a stated rule, not a prediction that its value will be lost.
