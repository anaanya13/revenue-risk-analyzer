"""Rebuild deterministic CSV practice files from the original synthetic workbook."""

import csv
from datetime import date, datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_pipeline


def write_csv(path, records):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main():
    sample = ROOT / "data/sample/revenue_risk_sample_data.xlsx"
    frame = load_pipeline(sample.read_bytes(), sample.name, "Deals").head(12)
    rows = frame.to_dict("records")
    for row in rows:
        for field, value in row.items():
            if isinstance(value, (datetime, date)):
                row[field] = value.strftime("%Y-%m-%d")
    destination = ROOT / "data/test"
    destination.mkdir(parents=True, exist_ok=True)

    rename = {
        "Deal ID": "Opportunity Number", "Deal Value": "Potential Revenue",
        "Created Date": "Date Opened", "Last Activity Date": "Last Contact",
        "Current Stage": "Pipeline Step", "Status": "Opportunity Result",
        "Sales Rep": "Account Owner", "Follow Ups": "Followup Count",
    }
    alternate = []
    for index, row in enumerate(rows, start=1):
        record = {new: row[old] for old, new in rename.items()}
        record["Opportunity Number"] = str(index).zfill(4)
        record["Potential Revenue"] = "${:,.2f}".format(float(row["Deal Value"]))
        record["Opportunity Result"] = {"Open": " Active ", "Won": "Closed Won", "Lost": "Closed Lost"}[row["Status"]]
        alternate.append(record)
    write_csv(destination / "alternate_company_data.csv", alternate)

    messy = [dict(row) for row in rows]
    messy[0]["Deal Value"] = " $19,000.00 "
    messy[0]["Status"] = " Closed Won "
    messy[1]["Deal Value"] = ""
    messy[2]["Deal Value"] = "not recorded"
    messy[3]["Deal ID"] = messy[4]["Deal ID"]
    messy[5]["Created Date"] = "not a date"
    messy[6]["Last Activity Date"] = "1900-01-01"
    messy[7]["Status"] = "Maybe"
    messy[8]["Follow Ups"] = "-2"
    messy[9]["Deal ID"] = ""
    messy[10]["Deal Value"] = "-500"
    messy[11]["Last Activity Date"] = "2099-01-01"
    write_csv(destination / "messy_pipeline_data.csv", messy)
    print("Created the two 12-row synthetic CSV practice files in data/test.")


if __name__ == "__main__":
    main()
