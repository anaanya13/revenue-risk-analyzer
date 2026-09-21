"""Conservative, reusable cell parsers for uploaded pipeline data.

Amounts use a period for decimals and optional comma thousands separators,
with optional $, USD, or CAD prefixes. Standard e/E notation is supported so
exported numbers can be uploaded again. Other currency/locale formats need to
be converted in the source file. Numeric spreadsheet date serials are not
guessed. Dates support ISO dates/timestamps, YYYY/MM/DD, and D/M/YYYY or
M/D/YYYY (slashes or hyphens); the caller selects the day/month order.
"""

from datetime import date, datetime
from decimal import Decimal
import math
from numbers import Number
import re
from typing import Any, Optional, Tuple

import pandas as pd


STATUS_ALIASES = {
    "open": "Open",
    "active": "Open",
    "in progress": "Open",
    "won": "Won",
    "closed won": "Won",
    "lost": "Lost",
    "closed lost": "Lost",
}


def is_missing(value: Any) -> bool:
    """Recognize real nulls and blank strings without treating 'NA' as null."""
    if isinstance(value, str):
        return not value.strip()
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def normalize_text(value: Any) -> Optional[str]:
    """Trim and collapse whitespace while preserving string identifiers."""
    if is_missing(value):
        return None
    return " ".join(str(value).split())


def normalize_status(value: Any) -> Optional[str]:
    text = normalize_text(value)
    if text is None:
        return None
    return STATUS_ALIASES.get(text.casefold(), text)


def parse_amount(value: Any) -> Tuple[Optional[float], Optional[str]]:
    """Return a finite numeric amount or one clear parsing issue.

    Negative amounts are parsed so the validator can report their specific
    problem. A missing amount is handled separately by required-field checks.
    """
    if is_missing(value):
        return None, None
    error = (
        "Use a number such as 12500 or 12,500.00, optionally prefixed by $, "
        "USD, or CAD; other locale formats are not supported."
    )
    if isinstance(value, bool):
        return None, error
    if isinstance(value, (Number, Decimal)):
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return None, error
    else:
        text = str(value).strip()
        parenthetical = text.startswith("(") and text.endswith(")")
        if parenthetical:
            text = text[1:-1].strip()
        # Accept either -$100 or $-100, but never two signs.
        leading_sign = ""
        if text[:1] in ("+", "-"):
            leading_sign, text = text[0], text[1:].strip()
        text = re.sub(r"^(?:USD|CAD)\s*\$?\s*|^\$\s*", "", text, flags=re.I)
        if leading_sign:
            if text[:1] in ("+", "-"):
                return None, error
            text = leading_sign + text
        if parenthetical and text[:1] in ("+", "-"):
            return None, error
        if not re.fullmatch(
            r"[+-]?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?(?:[eE][+-]?\d+)?", text
        ):
            return None, error
        try:
            number = float(text.replace(",", ""))
        except (ValueError, OverflowError):
            return None, error
        if parenthetical:
            number = -number
    if not math.isfinite(number):
        return None, "Deal value must be a finite number."
    return number, None


def parse_follow_ups(value: Any) -> Tuple[Optional[int], Optional[str]]:
    """Parse optional counts, accepting whole-number cells such as 3.0."""
    if is_missing(value):
        return None, None
    error = "Follow ups must be a nonnegative whole number."
    if isinstance(value, bool):
        return None, error
    text = str(value).strip()
    if not re.fullmatch(r"\+?\d+(?:\.0+)?", text):
        return None, error
    try:
        number = Decimal(text)
        # Keep values representable in pandas' nullable integer column.
        if number > 9223372036854775807:
            return None, "Follow ups is too large; use a smaller whole number."
        return int(number), None
    except (ValueError, OverflowError):
        return None, error


def parse_date(value: Any, day_first: bool = False) -> Tuple[Any, Optional[str]]:
    """Parse a calendar date; time and timezone are not used for day analysis."""
    if is_missing(value):
        return pd.NaT, None
    numeric_error = (
        "Numeric date serials are not supported. Format the source cell as a "
        "date or use YYYY-MM-DD."
    )
    if isinstance(value, (Number, Decimal, bool)):
        return pd.NaT, numeric_error
    error = (
        "Invalid date. Use YYYY-MM-DD or "
        + ("DD/MM/YYYY" if day_first else "MM/DD/YYYY")
        + "."
    )
    try:
        if isinstance(value, (datetime, date, pd.Timestamp)):
            parsed = pd.Timestamp(value)
        else:
            text = str(value).strip()
            if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text):
                return pd.NaT, numeric_error
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:[T ].+)?", text):
                parsed = pd.Timestamp(datetime.fromisoformat(text.replace("Z", "+00:00")))
            elif re.fullmatch(r"\d{4}/\d{1,2}/\d{1,2}", text):
                parsed = pd.Timestamp(datetime.strptime(text, "%Y/%m/%d"))
            elif re.fullmatch(r"\d{1,2}([/-])\d{1,2}\1\d{4}", text):
                date_format = "%d/%m/%Y" if day_first else "%m/%d/%Y"
                parsed = pd.Timestamp(datetime.strptime(text.replace("-", "/"), date_format))
            else:
                return pd.NaT, error
        # Rebuild midnight from the calendar date before conversion. pandas'
        # normalize() can wrap a Timestamp near its minimum into the far future.
        parsed = pd.Timestamp(parsed.date()).as_unit("ns")
        return parsed, None
    except (ValueError, TypeError, OverflowError):
        return pd.NaT, error
