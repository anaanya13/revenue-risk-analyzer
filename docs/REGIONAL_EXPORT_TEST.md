# Regional sales export test — September 29, 2026

**Historical baseline:** The limitations below describe the app before the September 29 import upgrade. Outcome mapping, header suggestions, owner-variant review, planned-contact analysis and coverage explanations are now implemented. See [DEPLOYMENT.md](DEPLOYMENT.md) for the passing live retest.

## Result

The app loads both unfamiliar workbooks and supports manual column mapping, but neither original file reaches analytics today. The corrected file is blocked only because Signed and Not proceeding are not recognized status labels. This is an app compatibility limitation, not 49 incorrect business records.

No original spreadsheet, application code or production calculation rule was changed during this test. No data was sent to the AI provider. Files were uploaded to the existing Streamlit app for validation. Additional calculation checks used a local in-memory copy with the documented outcome meanings translated explicitly.

## Live website results

| Test | Raw workbook | Corrected workbook |
| --- | --- | --- |
| Workbook opens | 100 rows, 15 columns | 100 rows, 15 columns |
| Worksheet | September Pipeline | September Pipeline |
| Automatic matches | None of the 12 supported fields | None of the 12 supported fields |
| Manual column mapping | All 12 fields can be selected | All 12 fields can be selected |
| Issues after mapping, before changing statuses | 55 across 54 rows | 49 across 49 rows |
| Analysis allowed | No | No |

The raw issue report downloaded successfully. The Dashboard correctly stayed locked for the raw upload. Ask AI stayed locked for the corrected upload while validation failed. The report date was September 29, 2026.

The app currently handles only known status aliases. In progress becomes Open automatically. Signed and Not proceeding remain unknown. My earlier suggested test prompt assumed an outcome-mapping capability that the current interface does not yet have.

## Column selections used

| Dashboard field | Source column |
| --- | --- |
| Deal ID | Opportunity Ref |
| Deal Value | Expected Contract Amount (CAD) |
| Created Date | First Entered |
| Last Activity Date | Latest Touchpoint |
| Current Stage | Where Things Stand |
| Status | Outcome So Far |
| Sales Representative | Account Handler |
| Delay Reason | What's Holding It Up? |
| Follow Ups | Chases So Far |
| Lead Source | Came From |
| Industry | Business Type |
| Product | Package Interested In |

Client / Business, Next Contact and Internal Comments have no supported destination and are excluded from the standardized analysis. They remain in the original files. Next Contact must not be mapped to Last Activity Date: planned contact and completed activity mean different things.

## Planted problem coverage

All ten changed cells and their row numbers agree with the supplied testing notes.

| Source row | Planted issue | Current behavior |
| --- | --- | --- |
| 15 | lowercase signed | Both signed and Signed are unknown; capitalization alone does not explain the rejection |
| 24 | missing amount | Blocking error |
| 34 | February 30 | Blocking invalid-date error |
| 45 | text amount 22,000 | Safely parsed to numeric 22000; no error needed |
| 53 | leading stage spaces | Trimmed to Quote sent |
| 60 | duplicate reference | Both rows 59 and 60 flagged; neither is guessed to be the correct one |
| 67 | missing outcome | Blocking error; no status inferred from other fields |
| 78 | Next Contact before entry | Not checked because this field is unsupported |
| 84 | uppercase owner with trailing space | Space removed, capitalization retained; could split this owner into two groups if the file otherwise passed |
| 92 | activity in 2027 | Blocking future-date error |

After translating only known nonblank outcome labels in memory, the raw file still has six blocking issues across six rows: 24, 34, 59, 60, 67 and 92. This accounts for both sides of the duplicate. A zero-issue result would not establish that ignored columns or case variants were correct.

## Calculations after explicit status translation — local test only

The corrected file passed validation after translating Signed to Won and Not proceeding to Lost, with In progress as Open. The supplied workbooks were not overwritten. The following values are NOT results unlocked by the unchanged hosted upload.

| Metric | Verified result |
| --- | ---: |
| Deals | 100 |
| Open / Won / Lost | 51 / 28 / 21 |
| Total deal value | CAD 2,194,070 |
| Open pipeline | CAD 1,434,650 |
| Won value | CAD 427,370 |
| Lost value | CAD 332,050 |
| Win rate by closed-deal count | 57.1% |
| Stalled Open deals, 30-day threshold | 12 |
| Revenue at risk | CAD 292,450 |
| Share of Open value at risk | 20.4% |
| Low / Medium / High / Critical Open deals | 30 / 9 / 2 / 10 |

All 465 independent SQL comparisons agreed. A local Streamlit integration check also confirmed these cards render, changing the threshold to 60 gives 10 stalled deals and CAD 286,050 exposure, and selecting Manager review at 30 days gives 8 Open deals and CAD 118,000 exposure.

The notes' status, stage and owner counts and status-value totals agree with the workbook. Independently confirmed 9 Open deals inactive for over 90 days, 8 with overdue Next Contact dates and 3 with no Next Contact. The last two measures are source-data checks only; the current app does not offer them. Amount-based win rate from the notes is not the app's count-based win-rate KPI.

## Improvements identified

1. Add explicit outcome mapping so users can confirm Signed → Won and Not proceeding → Lost without editing their workbook. Do not globally guess that Signed always means Won for every business.
2. Improve transparent column suggestions while preserving manual choices and ambiguity checks.
3. Add optional next-contact mapping, date-order validation and overdue-follow-up analysis. Future planned contacts are legitimate; they must not trigger the last-activity rule.
4. Offer a reviewable way to merge owner-name variants instead of silently changing names.
5. Clarify in the validation result which source columns were ignored and what a passed check does and does not cover.

These are findings and proposed improvements, not changes already implemented by this test.

## Saved evidence

Local evidence is in `exports/regional_test/`: original-file issue reports, calculation results and a derived analysis CSV explicitly labeled as after status translation. This folder is ignored for publishing. The original Downloads files were read without modification.
