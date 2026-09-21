"""Read a pipeline without guessing away identifiers or hiding duplicate headers."""

import csv
from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd

MAX_FILE_BYTES = 20 * 1024 * 1024


class DataLoadError(ValueError):
    """A file problem that can be explained directly in the app."""


def _check_file(content, filename):
    if not content:
        raise DataLoadError("This file is empty. Choose a file with a header row and deal records.")
    if len(content) > MAX_FILE_BYTES:
        raise DataLoadError("Choose a file smaller than 20 MB.")
    suffix = Path(filename).suffix.lower()
    if suffix not in (".csv", ".xlsx"):
        raise DataLoadError("Choose a CSV (.csv) or Excel (.xlsx) file.")
    return suffix


def excel_sheet_names(content):
    _check_file(content, "workbook.xlsx")
    try:
        with pd.ExcelFile(BytesIO(content), engine="openpyxl") as workbook:
            return workbook.sheet_names
    except Exception as error:
        raise DataLoadError(
            "This workbook could not be opened. Save an unprotected .xlsx copy in Excel and try again."
        ) from error


def _headers(values):
    headers = []
    for value in values:
        if pd.isna(value) or not str(value).strip():
            raise DataLoadError("Every column needs a name in the first row. A column heading is blank.")
        headers.append(str(value).strip())
    if len({value.casefold() for value in headers}) != len(headers):
        raise DataLoadError("Two columns have the same name. Give each column a unique heading and try again.")
    return headers


def load_pipeline(content, filename, sheet_name=None):
    """Return source rows in their original order, with text IDs preserved."""
    suffix = _check_file(content, filename)
    try:
        if suffix == ".csv":
            try:
                decoded = content.decode("utf-8-sig")
            except UnicodeDecodeError as error:
                raise DataLoadError("Save this file as CSV UTF-8 in Excel and upload that copy.") from error
            rows = list(csv.reader(StringIO(decoded), strict=True))
            if not rows:
                raise DataLoadError("This CSV has no header row.")
            headers = _headers(rows[0])
            records = []
            for row_number, row in enumerate(rows[1:], start=2):
                if not row:
                    row = [""] * len(headers)
                if len(row) != len(headers):
                    raise DataLoadError(
                        "Record {} has a different number of columns than the header. "
                        "Save the table as a comma-separated CSV and try again.".format(row_number)
                    )
                records.append(row)
            frame = pd.DataFrame(records, columns=headers, dtype=object)
        else:
            raw = pd.read_excel(
                BytesIO(content), sheet_name=0 if sheet_name is None else sheet_name,
                header=None, dtype=object, keep_default_na=False, engine="openpyxl",
            )
            if raw.empty:
                raise DataLoadError("This worksheet is empty. Select the worksheet containing deals.")
            headers = _headers(raw.iloc[0].tolist())
            frame = raw.iloc[1:].copy()
            frame.columns = headers
            frame = frame.reset_index(drop=True)
    except DataLoadError:
        raise
    except Exception as error:
        raise DataLoadError(
            "The file could not be read. Check that it is a CSV or an unprotected Excel workbook, "
            "with column names in the first row."
        ) from error
    if frame.empty:
        raise DataLoadError("There are column headings but no deals. Add at least one deal and try again.")
    return frame
