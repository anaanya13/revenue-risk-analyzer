"""Cross-module tests of real input files and the Streamlit user workflow."""

from datetime import date
from pathlib import Path
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.column_mapper import mapping_errors, standardize_columns, suggest_mapping
from src.data_loader import DataLoadError, excel_sheet_names, load_pipeline
from src.data_validator import validate_data
from src.exports import csv_bytes

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 9, 19)


def validate_file(relative):
    path = ROOT / relative
    frame = load_pipeline(path.read_bytes(), path.name)
    mapped = standardize_columns(frame, suggest_mapping(frame.columns))
    return frame, validate_data(mapped, as_of_date=AS_OF)


class FileWorkflowTests(unittest.TestCase):
    def test_original_sample_passes_without_losing_rows(self):
        raw, result = validate_file("data/sample/revenue_risk_sample_data.xlsx")
        self.assertEqual(raw.shape, (120, 14))
        self.assertTrue(result.is_valid, result.issues.to_string())
        self.assertEqual(len(result.cleaned_data), 120)
        self.assertEqual(result.cleaned_data.status.value_counts().to_dict(), {"Open": 70, "Won": 27, "Lost": 23})

    def test_alternate_company_headers_status_and_ids(self):
        raw, result = validate_file("data/test/alternate_company_data.csv")
        self.assertTrue(result.is_valid, result.issues.to_string())
        self.assertEqual(len(result.cleaned_data), 12)
        self.assertEqual(result.cleaned_data.iloc[0].deal_id, "0001")
        self.assertEqual(result.cleaned_data.iloc[0].deal_value, 19000)
        self.assertEqual(result.cleaned_data.iloc[0].status, "Won")
        self.assertNotIn("Deal ID", raw.columns)

    def test_messy_file_reports_expected_records_once_per_problem(self):
        _, result = validate_file("data/test/messy_pipeline_data.csv")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.invalid_row_count, 11)
        self.assertEqual(len(result.issues), 11)
        self.assertEqual(set(result.issues.source_row), set(range(3, 14)))
        self.assertEqual(len(result.cleaned_data), 12)

    def test_bad_files_have_actionable_errors(self):
        for content, filename in [
            (b"", "file.csv"), (b"id,id\n1,2", "file.csv"),
            (b"id,\n1,2", "file.csv"), (b"id,value\n1,2,3", "file.csv"),
            (b"id,value", "file.csv"), (b"bad excel", "file.xlsx"),
            (b"data", "file.txt"), (b"\xff", "file.csv"),
        ]:
            with self.subTest(filename=filename, content=content):
                with self.assertRaises(DataLoadError):
                    load_pipeline(content, filename)

    def test_blank_records_and_identifier_na_are_preserved(self):
        raw = load_pipeline(b"Deal ID,Deal Value\n0001,12\n\nNA,14\n", "FILE.CSV")
        self.assertEqual(raw["Deal ID"].tolist(), ["0001", "", "NA"])

    def test_excel_sheets_can_be_selected(self):
        path = ROOT / "data/sample/revenue_risk_sample_data.xlsx"
        content = path.read_bytes()
        self.assertEqual(excel_sheet_names(content), ["Deals", "Data Dictionary"])
        dictionary = load_pipeline(content, path.name, "Data Dictionary")
        self.assertIn("Meaning", dictionary.columns)
        self.assertTrue(mapping_errors(dictionary.columns, suggest_mapping(dictionary.columns)))

    def test_mapping_rejects_reused_columns_and_ambiguous_aliases(self):
        frame, _ = validate_file("data/sample/revenue_risk_sample_data.xlsx")
        mapping = suggest_mapping(frame.columns)
        mapping["status"] = "Deal ID"
        self.assertTrue(any("more than once" in error for error in mapping_errors(frame.columns, mapping)))
        with self.assertRaises(ValueError):
            standardize_columns(frame, mapping)
        self.assertIsNone(suggest_mapping(["Deal Value", "Amount"])["deal_value"])

    def test_csv_export_handles_dates_missing_cells_and_formula_text(self):
        frame = pd.DataFrame({"id": ["=1+1", "0001"], "date": [pd.Timestamp("2026-09-18"), pd.NaT]})
        content = csv_bytes(frame)
        raw = load_pipeline(content, "export.csv")
        self.assertEqual(raw.id.tolist(), ["'=1+1", "0001"])
        self.assertEqual(raw.date.tolist(), ["2026-09-18", ""])


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()

    def choose_source(self, source):
        self.app.radio[0].set_value(source).run()
        self.assertEqual(len(self.app.exception), 0)

    def check(self):
        self.app.date_input[0].set_value(AS_OF).run()
        self.app.button[0].click().run()
        self.assertEqual(len(self.app.exception), 0)

    def test_sample_and_mapping_change_require_fresh_validation(self):
        self.assertEqual(len(self.app.exception), 0)
        self.choose_source("Try sample data")
        self.check()
        self.assertEqual([m.value for m in self.app.metric], ["120", "0", "0"])
        self.assertTrue(any("passed" in message.value for message in self.app.success))
        status = next(widget for widget in self.app.selectbox if widget.label == "Status *")
        status.set_value("Deal ID").run()
        self.assertTrue(self.app.button[0].disabled)
        self.assertEqual(len(self.app.metric), 0)

    def test_messy_data_has_report_and_no_clean_export(self):
        self.choose_source("Try messy test data")
        self.check()
        self.assertEqual([m.value for m in self.app.metric], ["12", "11", "11"])
        self.assertEqual(len(self.app.error), 1)
        self.assertFalse(any(expander.label == "Review standardized data" for expander in self.app.expander))
        downloads = self.app.get("download_button")
        self.assertEqual([button.label for button in downloads], ["Download issues to fix"])

    def test_alternate_company_and_source_switch_clear_previous_results(self):
        self.choose_source("Try alternate column names")
        self.check()
        self.assertEqual([m.value for m in self.app.metric], ["12", "0", "0"])
        self.choose_source("Try messy test data")
        self.assertEqual(len(self.app.metric), 0)

    def test_dictionary_sheet_does_not_report_ready(self):
        self.choose_source("Try sample data")
        self.app.selectbox[0].set_value("Data Dictionary").run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertTrue(self.app.button[0].disabled)
        self.assertEqual(len(self.app.metric), 0)


if __name__ == "__main__":
    unittest.main()
