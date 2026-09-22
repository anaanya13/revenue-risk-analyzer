# Revenue Risk & Deal Bottleneck Analyzer

A portfolio application that will help teams turn their own sales-pipeline spreadsheets into useful analysis of stalled deals and operational delays.

The current milestone prepares the data: upload or choose a sample, match columns, check data quality, and download standardized data once the entire file passes. Revenue KPIs, risk calculations, charts, and automated recommendations are the next stages.

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

Define and test pipeline KPIs, deal aging, and an inactivity-based risk rule. Then add charts, filters, explainable insights, and recommendations. SQL with DuckDB and resume packaging come later. GitHub publishing and Streamlit deployment are complete.

This is a hosted portfolio project using synthetic examples. It has not been evaluated with a live company's workflow. A flagged deal will represent pipeline exposure under a stated rule, not a prediction that its value will be lost.
