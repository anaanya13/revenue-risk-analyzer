# Practice files

Both CSV files contain 12 synthetic records derived from the first 12 deals in the preserved sample workbook. They are practice data, not records from another real company.

Use a validation date of **September 19, 2026** to reproduce these results:

| File | Expected result |
| --- | --- |
| `alternate_company_data.csv` | All 12 rows pass. Different headers are suggested automatically; IDs retain their leading zeros; currency formatting and status aliases are standardized. |
| `messy_pipeline_data.csv` | 11 issues across 11 rows. Source row 2 passes after normalizing whitespace, currency formatting, and status. |

The messy file deliberately includes these problems:

| Source row | Problem |
| --- | --- |
| 3 | Missing deal value |
| 4 | Nonnumeric deal value |
| 5, 6 | Duplicate deal ID; both occurrences flagged |
| 7 | Invalid created date |
| 8 | Last activity before creation |
| 9 | Unrecognized status |
| 10 | Negative follow-up count |
| 11 | Missing deal ID |
| 12 | Negative deal value |
| 13 | Future last activity date |

The saved `scripts/build_test_data.py` script reproduces these files. Run it from the project folder with `.venv/bin/python scripts/build_test_data.py` only when you want to restore the practice files; it replaces these two CSVs. It does not change the original workbook.
