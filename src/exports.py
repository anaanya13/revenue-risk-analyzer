"""CSV exports that preserve dates and display uploaded text safely in Excel."""

from datetime import date, datetime

import pandas as pd


def csv_bytes(frame):
    def display(value):
        if isinstance(value, (datetime, date, pd.Timestamp)) and not pd.isna(value):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + value
        return value

    return frame.map(display).to_csv(index=False).encode("utf-8-sig")
