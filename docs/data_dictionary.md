# Data dictionary

Each row should describe one deal. Your file can use different column names; match them to the fields below in the application.

## Required fields

| Field | Meaning | Example |
| --- | --- | --- |
| Deal ID | Unique identifier for one deal; keep the same ID throughout its life | `D001` |
| Deal Value | Potential value of that deal, in a single shared currency for the file | `12500` |
| Created Date | Date the deal first entered the pipeline | `2026-08-01` |
| Last Activity Date | Most recent recorded activity associated with the deal | `2026-09-10` |
| Current Stage | Current step in the team's workflow | `Documentation` |
| Status | Whether the deal remains open, has been won, or has been lost | `Open`, `Won`, `Lost` |

Deal Value is not necessarily money already received. Current Stage and Status have different purposes: a deal might be in `Credit Review` with Status `Open`.

The checker recognizes these status labels without requiring matching capitalization:

| Your status label | Standard status |
| --- | --- |
| Open, Active, In Progress | Open |
| Won, Closed Won | Won |
| Lost, Closed Lost | Lost |

Other labels need correction or an explicit future mapping rule. The app does not guess whether an unfamiliar status means a deal is won or lost.

The original sample's dictionary calls Last Activity Date “Recommended.” In the current application it is **required**, because the next analytics stage will need it to calculate inactivity.

## Optional fields

| Field | Meaning | Example |
| --- | --- | --- |
| Delay Reason | Recorded explanation for a delay, if known | `Missing documents` |
| Follow Ups | Number of follow-ups recorded for the deal | `3` |
| Sales Representative | Person responsible for the deal | `Alex` |
| Lead Source | Channel through which the opportunity originated | `Referral` |
| Industry | Customer's industry or business category | `Retail` |
| Product | Product or service associated with the deal | `Equipment finance` |

Leave optional fields unmapped when your file does not contain them. A blank optional value means the information is unavailable; it should not be assumed to mean zero follow-ups or no delay.

## Extra columns in the original workbook

The preserved sample also includes **Customer** and **Close Date**. They remain in that original file, but are not mapped in the current milestone. A future version can use Close Date to support time-to-close and dated won-deal analysis.

The workbook has two sheets: choose **Deals** for checking records. **Data Dictionary** is explanatory text.

## Dates and numbers

- Prefer dates written as `YYYY-MM-DD`, for example `2026-09-18`.
- If your file uses dates such as `04/05/2026`, choose whether the day or month comes first before checking the file.
- Created Date should be on or before Last Activity Date. Neither should be later than the selected validation date.
- Keep all Deal Values in one currency. A currency symbol is formatting, not proof that mixed currencies have been converted.
- Amounts may use formatting such as `$12,500.00`, `USD 12500`, or `CAD 12500`. The current parser expects a dot for decimals; negative or nonnumeric values are reported as errors.
- Deal IDs are identifiers rather than quantities. Store them as text in the source spreadsheet when leading zeros matter; digits already lost by the spreadsheet cannot be recovered reliably.
- Follow Ups, when supplied, should be a non-negative whole number.

## Understanding the results

The issue report identifies the affected source row and field. Row 1 is the header; row 2 is the first deal. For CSV files, this means the record number: a quoted cell containing a line break can occupy more than one physical text line. More than one issue can affect a row, so the number of issues can exceed the number of records needing attention.

Every occurrence of a duplicate Deal ID is flagged for review. The checker does not choose a “correct” copy, delete duplicates, or fill in missing required information. Optional fields can be absent, but a supplied Follow Ups value must still be valid.

The standardized preview and download become available only after **all records pass**. The preview shows the first 50 rows; use **Download standardized data** for every deal row. The cleaned file contains the mapped columns and standardized values; unmapped columns remain in the original file. Keep that original as your source of truth, use the report to correct it, and run the checks again. A clean file establishes that these checks passed; it does not prove the underlying business records are factually correct.

CSV downloads protect text beginning with spreadsheet formula characters by adding a leading apostrophe. This applies to text fields such as IDs, not numeric amounts. Dates export as `YYYY-MM-DD`.

The app checks a pipeline snapshot. It cannot reconstruct activity history or calculate how long a deal has been in its current stage from the required fields alone.
