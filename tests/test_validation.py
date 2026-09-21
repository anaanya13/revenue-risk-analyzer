"""Boundary-focused tests for pipeline cleaning and validation."""

from datetime import datetime
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from src.data_validator import validate_data


class ValidationTests(unittest.TestCase):
    def data(self, **changes):
        row = {
            "deal_id": "0007", "deal_value": "$12,500.25", "created_date": "2025-01-02",
            "last_activity_date": "2025-02-03", "stage": "  Proposal  sent  ",
            "status": " Active ",
        }
        row.update(changes)
        return pd.DataFrame([row])

    def validate(self, frame, **kwargs):
        return validate_data(frame, as_of_date="2025-06-30", **kwargs)

    def test_cleaning_keeps_leading_zeros_and_does_not_change_input(self):
        frame = self.data(follow_ups="3.0", sales_rep="  Alex   Li  ")
        before = frame.copy(deep=True)
        result = self.validate(frame)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.invalid_row_count, 0)
        self.assertEqual(result.cleaned_data.at[0, "deal_id"], "0007")
        self.assertEqual(result.cleaned_data.at[0, "deal_value"], 12500.25)
        self.assertEqual(result.cleaned_data.at[0, "stage"], "Proposal sent")
        self.assertEqual(result.cleaned_data.at[0, "status"], "Open")
        self.assertEqual(result.cleaned_data.at[0, "sales_rep"], "Alex Li")
        self.assertEqual(result.cleaned_data.at[0, "follow_ups"], 3)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result.cleaned_data.created_date))
        assert_frame_equal(frame, before)

    def test_status_aliases_and_unknown_value(self):
        for source, expected in [
            ("Open", "Open"), ("in  progress", "Open"), (" won ", "Won"),
            ("CLOSED WON", "Won"), ("lost", "Lost"), ("Closed Lost", "Lost"),
        ]:
            with self.subTest(source=source):
                result = self.validate(self.data(status=source))
                self.assertTrue(result.is_valid)
                self.assertEqual(result.cleaned_data.at[0, "status"], expected)
        result = self.validate(self.data(status=" Pending review "))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.issues.iloc[0]["value"], " Pending review ")

    def test_missing_is_not_also_reported_as_invalid(self):
        for field in ("deal_value", "created_date", "last_activity_date", "status"):
            for blank in (None, " \t ", pd.NA, float("nan")):
                with self.subTest(field=field, blank=blank):
                    result = self.validate(self.data(**{field: blank}))
                    self.assertEqual(len(result.issues), 1)
                    self.assertEqual(result.issues.iloc[0]["issue"], "Required value is missing.")

    def test_amount_boundaries_and_conservative_formats(self):
        for value, expected in [("CAD 12,500", 12500), ("USD 12.50", 12.5), (0, 0)]:
            with self.subTest(value=value):
                result = self.validate(self.data(deal_value=value))
                self.assertTrue(result.is_valid)
                self.assertEqual(result.cleaned_data.at[0, "deal_value"], expected)
        for value in ("($100.50)", -5, float("inf"), "12,50", "1.234,56", "garbage", True):
            with self.subTest(value=value):
                result = self.validate(self.data(deal_value=value))
                self.assertFalse(result.is_valid)
                self.assertEqual(len(result.issues), 1)
                self.assertEqual(result.invalid_row_count, 1)

    def test_day_month_preference_does_not_change_iso_dates(self):
        for day_first, expected in [(False, "2025-03-04"), (True, "2025-04-03")]:
            with self.subTest(day_first=day_first):
                result = self.validate(
                    self.data(created_date="03/04/2025", last_activity_date="2025-05-01"),
                    day_first=day_first,
                )
                self.assertTrue(result.is_valid)
                self.assertEqual(result.cleaned_data.at[0, "created_date"], pd.Timestamp(expected))
                self.assertEqual(result.cleaned_data.at[0, "last_activity_date"], pd.Timestamp("2025-05-01"))

    def test_scientific_notation_from_numeric_exports_remains_valid(self):
        for value, expected in [("1e-05", 0.00001), ("1.25E+20", 1.25e20)]:
            with self.subTest(value=value):
                result = self.validate(self.data(deal_value=value))
                self.assertTrue(result.is_valid)
                self.assertEqual(result.cleaned_data.at[0, "deal_value"], expected)
        overflow = self.validate(self.data(deal_value="1e999"))
        self.assertFalse(overflow.is_valid)
        self.assertIn("finite", overflow.issues.iloc[0]["issue"])

    def test_impossible_dates_and_numeric_serials_are_rejected(self):
        for value in ("02/30/2025", "not a date", "2025-13-04", "9999-01-01", 45678, "45678"):
            with self.subTest(value=value):
                result = self.validate(self.data(created_date=value))
                self.assertFalse(result.is_valid)
                self.assertEqual(len(result.issues), 1)
                self.assertTrue(pd.isna(result.cleaned_data.at[0, "created_date"]))
                if value in (45678, "45678"):
                    self.assertIn("Numeric date serials", result.issues.iloc[0]["issue"])

    def test_typed_dates_and_same_day_timestamps(self):
        result = self.validate(self.data(
            created_date=datetime(2025, 6, 30, 15), last_activity_date="2025-06-30T10:00:00Z"
        ))
        self.assertTrue(result.is_valid)
        self.assertEqual(result.cleaned_data.at[0, "created_date"], pd.Timestamp("2025-06-30"))

    def test_typed_date_boundary_does_not_wrap_to_another_year(self):
        result = self.validate(self.data(created_date=pd.Timestamp.min))
        self.assertFalse(result.is_valid)
        self.assertTrue(pd.isna(result.cleaned_data.at[0, "created_date"]))
        self.assertIn("Invalid date", result.issues.iloc[0]["issue"])

    def test_future_and_reversed_dates(self):
        reversed_result = self.validate(self.data(last_activity_date="2025-01-01"))
        self.assertIn("before the created date", reversed_result.issues.iloc[0]["issue"])
        future_result = self.validate(self.data(last_activity_date="2025-07-01"))
        self.assertIn("after the analysis date", future_result.issues.iloc[0]["issue"])

    def test_duplicates_flag_every_occurrence_and_use_source_positions(self):
        frame = pd.concat([self.data(), self.data(deal_id=" 0007 "), self.data(deal_id="8")])
        frame.index = [90, 90, 400]
        result = self.validate(frame)
        self.assertEqual(len(result.cleaned_data), 3)
        self.assertEqual(result.invalid_row_count, 2)
        self.assertEqual(result.issues["source_row"].tolist(), [2, 3])
        self.assertTrue(result.issues["issue"].str.startswith("Duplicate").all())

    def test_optional_counts_are_never_filled_or_rounded(self):
        for value in (None, "", pd.NA):
            with self.subTest(value=value):
                result = self.validate(self.data(follow_ups=value))
                self.assertTrue(result.is_valid)
                self.assertTrue(pd.isna(result.cleaned_data.at[0, "follow_ups"]))
        for value in (-1, 1.5, "none", float("inf"), True, "9223372036854775808"):
            with self.subTest(value=value):
                result = self.validate(self.data(follow_ups=value))
                self.assertFalse(result.is_valid)
                self.assertEqual(len(result.issues), 1)

    def test_row_count_counts_rows_not_issues(self):
        result = self.validate(self.data(deal_value=-10, status="Pending", stage=""))
        self.assertEqual(len(result.issues), 3)
        self.assertEqual(result.invalid_row_count, 1)

    def test_empty_file_and_missing_required_columns_are_blocked(self):
        empty = self.validate(pd.DataFrame())
        self.assertFalse(empty.is_valid)
        self.assertEqual(empty.invalid_row_count, 0)
        self.assertEqual(empty.issues.iloc[0]["field"], "dataset")
        result = self.validate(self.data().drop(columns=["status"]))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.invalid_row_count, 1)
        self.assertEqual(result.issues.iloc[0]["field"], "status")

    def test_invalid_analysis_date_is_an_explicit_configuration_error(self):
        with self.assertRaisesRegex(ValueError, "analysis date"):
            validate_data(self.data(), as_of_date="not a date")


if __name__ == "__main__":
    unittest.main()
