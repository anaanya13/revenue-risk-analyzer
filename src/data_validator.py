"""Clean mapped pipeline fields and report every blocking data-quality issue."""

from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd

from src.data_cleaner import (
    is_missing,
    normalize_status,
    normalize_text,
    parse_amount,
    parse_date,
    parse_follow_ups,
)


REQUIRED_FIELDS = (
    "deal_id", "deal_value", "created_date", "last_activity_date", "stage", "status"
)
TEXT_FIELDS = (
    "deal_id", "stage", "delay_reason", "sales_rep", "lead_source", "industry", "product"
)
ISSUE_COLUMNS = ("source_row", "deal_id", "field", "issue", "value", "severity")


@dataclass
class ValidationResult:
    cleaned_data: pd.DataFrame
    issues: pd.DataFrame
    is_valid: bool
    invalid_row_count: int


def validate_data(
    frame: pd.DataFrame,
    day_first: bool = False,
    as_of_date: Optional[Any] = None,
) -> ValidationResult:
    """Return cleaned values and blocking issues without changing the input.

    Source rows are one-based file row numbers with row 1 reserved for headers.
    No rows are removed, combined, or filled with guessed business values.
    ``invalid_row_count`` counts distinct affected records, not issue messages.
    Empty data is invalid even though its invalid-record count is zero.
    """
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame containing mapped columns.")
    if not frame.columns.is_unique:
        raise ValueError("Mapped column names must be unique before validation.")

    reference_date, reference_error = parse_date(
        pd.Timestamp.today() if as_of_date is None else as_of_date,
        day_first=day_first,
    )
    if reference_error or pd.isna(reference_date):
        raise ValueError("The analysis date must be a valid date.")

    raw = frame.copy(deep=True).reset_index(drop=True)
    cleaned = raw.copy(deep=True)
    issues = []
    missing_columns = [field for field in REQUIRED_FIELDS if field not in raw.columns]
    for field in missing_columns:
        raw[field] = None
        cleaned[field] = None

    def add_issue(position: Optional[int], field: str, message: str, value: Any = "") -> None:
        identifier = "" if position is None else normalize_text(raw.at[position, "deal_id"])
        issues.append({
            "source_row": pd.NA if position is None else position + 2,
            "deal_id": identifier or "",
            "field": field,
            "issue": message,
            "value": "" if is_missing(value) else str(value),
            "severity": "Error",
        })

    if raw.empty:
        add_issue(None, "dataset", "The file has no data rows. Add at least one deal.")

    for field in TEXT_FIELDS:
        if field in cleaned:
            cleaned[field] = pd.Series(
                [normalize_text(value) for value in raw[field]], dtype="string"
            )

    amounts = []
    statuses = []
    created_dates = []
    activity_dates = []
    follow_ups = []

    for position in range(len(raw)):
        row = raw.iloc[position]
        for field in REQUIRED_FIELDS:
            if is_missing(row[field]):
                message = (
                    "Required column is missing from the mapped data."
                    if field in missing_columns else "Required value is missing."
                )
                add_issue(position, field, message, row[field])

        amount, amount_error = parse_amount(row["deal_value"])
        if amount_error:
            add_issue(position, "deal_value", amount_error, row["deal_value"])
        elif amount is not None and amount < 0:
            add_issue(position, "deal_value", "Deal value cannot be negative.", row["deal_value"])
        amounts.append(amount)

        status = normalize_status(row["status"])
        if status is not None and status not in ("Open", "Won", "Lost"):
            add_issue(
                position, "status",
                "Unrecognized status. Use Open, Active, In Progress, Won, Closed Won, Lost, or Closed Lost.",
                row["status"],
            )
        statuses.append(status)

        parsed_dates = {}
        for field in ("created_date", "last_activity_date"):
            parsed, date_error = parse_date(row[field], day_first=day_first)
            parsed_dates[field] = parsed
            if date_error:
                add_issue(position, field, date_error, row[field])
            elif pd.notna(parsed) and parsed > reference_date:
                add_issue(
                    position, field,
                    "Date is after the analysis date ({}).".format(reference_date.date()),
                    row[field],
                )
        created = parsed_dates["created_date"]
        activity = parsed_dates["last_activity_date"]
        created_dates.append(created)
        activity_dates.append(activity)
        if pd.notna(created) and pd.notna(activity) and activity < created:
            add_issue(
                position, "last_activity_date", "Last activity date is before the created date.",
                row["last_activity_date"],
            )

        if "follow_ups" in raw:
            count, count_error = parse_follow_ups(row["follow_ups"])
            follow_ups.append(count)
            if count_error:
                add_issue(position, "follow_ups", count_error, row["follow_ups"])

    cleaned["deal_value"] = pd.Series(amounts, dtype="Float64")
    cleaned["status"] = pd.Series(statuses, dtype="string")
    cleaned["created_date"] = pd.Series(created_dates, dtype="datetime64[ns]")
    cleaned["last_activity_date"] = pd.Series(activity_dates, dtype="datetime64[ns]")
    if "follow_ups" in raw:
        cleaned["follow_ups"] = pd.Series(follow_ups, dtype="Int64")

    duplicates = cleaned["deal_id"].notna() & cleaned["deal_id"].duplicated(keep=False)
    for position in cleaned.index[duplicates]:
        add_issue(
            int(position), "deal_id", "Duplicate deal ID. Each deal needs a unique identifier.",
            raw.at[position, "deal_id"],
        )

    issue_frame = pd.DataFrame(issues, columns=ISSUE_COLUMNS)
    issue_frame["source_row"] = issue_frame["source_row"].astype("Int64")
    return ValidationResult(
        cleaned_data=cleaned,
        issues=issue_frame,
        is_valid=issue_frame.empty,
        invalid_row_count=int(issue_frame["source_row"].nunique()),
    )
