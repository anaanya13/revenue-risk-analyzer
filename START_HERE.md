# Start here

## New: help while you use the app

- Open **Your dashboard guide — start here** above the tabs at any time. It walks through setup, filters, results, downloads and common questions.
- In **Dashboard**, use **Understand your KPIs** to see the current formula, interpretation and suggested review. Expand **Explain every KPI** for the full list.
- In **Action plan**, open **Understand delays and plan a response**. Select a recorded reason to see Open/stalled counts, exposed value, supporting deal IDs, a suggested mitigation and how to check progress.
- **Download delay analysis and guidance** keeps all reason groups and settings, not just the reason currently displayed.

The delay reason comes from your file. The app does not infer a cause from the stage or inactivity. Actions are suggestions to confirm with the owner; no messages are sent and no tasks are marked complete automatically. See [the explanation guide](docs/KPI_AND_DELAY_GUIDE.md).

## The new layout

The Midnight & Teal design separates the workflow into four tabs:

- **Data setup:** upload or select a sample, map columns, check quality, and download the full standardized file.
- **Dashboard:** KPI cards, aging/risk charts and bottleneck summaries.
- **Action plan:** prioritized suggestions, deals to review and analysis downloads.
- **Verification:** calculation definitions, the independent SQL check and its report.

After Check data succeeds, select **Dashboard**. The left sidebar holds the stalled threshold and filters shared by all result tabs. If the sidebar is collapsed, use Streamlit's sidebar arrow to reopen it. All calculations and file formats are unchanged.

## Use the online app

Open [Revenue Risk Analyzer](https://anaanya-revenue-risk-analyzer.streamlit.app/) and bookmark it. **No Terminal commands are needed for the online version.**

1. Select **Try sample data**.
2. Keep the **Deals** worksheet and suggested column matches.
3. Click **Check data**. The sample should show **120 deals and 0 issues** with a validation date on or after September 18, 2026.
4. Open the **Dashboard** tab to see KPIs, aging, risk, bottlenecks, and deals to review.
5. Try **Try messy test data** to see the issue report, or **Try alternate column names** to see another header format.

Close the browser tab when finished. To request improvements, continue the project task where the app was built. The saved code is on [GitHub](https://github.com/anaanya13/revenue-risk-analyzer); code updates must be published there to update the online app.

The rest of this guide is for the optional local version on your computer. You do not need to edit Python code to use either version.

## Optional local use: 1. Open Terminal

Press **Command + Space**, type **Terminal**, and open it.

## 2. Start the application

Copy the first line below, paste it into Terminal, and press Enter. Then do the same with the second line:

```bash
cd ~/Desktop/revenue-risk-analyzer
bash scripts/start.sh
```

The first command opens the project folder in Terminal. The second starts the app with the project's existing Python environment. You do not need to type `app.py` by itself or open Python separately.

Leave Terminal open. If no browser window appears, open [http://localhost:8501](http://localhost:8501).

## 3. Try the original sample

1. Choose **Try sample data**.
2. If a worksheet selector appears, choose **Deals**. The `Data Dictionary` worksheet explains the fields; it is not a list of deals.
3. Review the preview. The original sample contains **120 deals**.
4. Review the suggested column matches. Each required field should point to its matching column.
5. Review the date settings. The sample includes activity through **September 18, 2026**, so a validation date before then would flag later dates.
6. Click **Check data**.
7. Read the results and try downloading the cleaned data or the issue report.

Next, choose **Try messy test data** to see how problems are reported. Choose **Try alternate column names** to see how mapping supports another company's headers.

## 4. Try your own file

Choose **Upload a file** and select a `.csv` or `.xlsx` sales-pipeline spreadsheet. For an Excel file, select the sheet containing the deal rows.

Match your headers to the app's fields. For example, your `Opportunity Amount` column may mean **Deal Value**. Required fields need a match. Optional fields can be left unmapped when the file does not have them.

Use one row per deal and one currency per file. Choose the correct date order for dates such as `04/05/2026`: this can mean April 5 or May 4. Then click **Check data**.

If issues appear, the default mode analyzes usable rows and keeps unresolved rows in the issue list. The standardized download contains included rows and coverage columns. Correct flagged cells inside the app, or upload a corrected workbook. Turn on **Require every row to pass before analysis** for strict validation.

## 5. Stop or restart

To stop the app, click the Terminal window running it and press **Control + C**. Use Control, not Command.

To start again, repeat the two commands in Step 2. If an older copy of the app is still running in another Terminal window, stop that copy first.

## If something does not work

**The browser does not open:** leave Terminal running and open [http://localhost:8501](http://localhost:8501) yourself.

**Terminal says the address or port is already in use:** an app may already be running. Check your existing Terminal windows and stop the older app with Control + C before starting again.

### If setup is missing

If the start script says the environment is missing, run these commands from the project folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
bash scripts/start.sh
```

**The environment exists but a required package is missing:** run:

```bash
.venv/bin/python -m pip install -r requirements.txt
bash scripts/start.sh
```

The installation command needs an internet connection. These recovery steps are not needed for a normal start; the current folder already has its Python environment.

For another error, copy the message from Terminal and share it in this project task. Keep the project files so the problem can be reproduced and fixed.

## Explore the new analytics dashboard

After **Check data** succeeds:

1. Review **Pipeline overview** for open pipeline value, won value, win rate, deal counts, and revenue at risk.
2. Start with **30 days** in **Stalled after this many days without activity**. Change it to suit the workflow; the dashboard updates immediately.
3. In **Verification**, expand **What do the numbers and risk levels mean?** for definitions. With 30 days selected: Low = 0–14 inactive days, Medium = 15–29, High = 30–59, Critical = 60+. High and Critical are stalled.
4. Use **Filter the dashboard** in the sidebar to select status, stage, risk, and any supplied representative, lead source, industry or product. You can also filter by creation date. All dashboard results use these filters. Clearing a selection returns no deals; **Reset filters** brings them back.
5. Read **Aging and risk** and **Where are open deals getting stuck?**. Optional delay reasons and representative summaries appear when those fields are mapped.
6. Review the stalled deals under **Deals to review** in **Action plan**. Download **filtered analysis** to keep all matching rows with their age, risk, analysis date and threshold, or download the **stage summary**. The earlier standardized download still contains the full validated file.

**Revenue at risk means the full value of stalled Open deals. It is exposure to review, not a forecast that this money will be lost.** Deal age counts days since creation; inactivity counts days since last activity. Current stage alone cannot tell us time spent in that stage. Won value is the amount in the spreadsheet, not accounting-recognized revenue.

The **Analysis / validation date** above Check data controls both validation and aging. Changing it requires checking the file again. Use a snapshot from the date you want to analyze; changing this date cannot reconstruct historical statuses. No closed deals means win rate is N/A, and no Open value means the percentage at risk is N/A.

## Use the suggested next steps

In the **Action plan** tab, **Suggested next steps** explains what needs attention, the supporting deal count and value, and a practical follow-up. These are suggestions for your review; the app does not contact anyone or change the original file.

- **Review first:** Critical opportunities and stages with the most stalled value.
- **Complete details:** stalled deals with missing or unmapped owners or delay reasons.
- **Watch:** Medium-risk deals approaching the stalled threshold.

The same deal can appear in several suggestions. **Do not add these suggestion values together.** Revenue at risk remains the separate total of stalled Open deals. Missing optional columns are described as unavailable, not as proof that the original company record is incomplete.

Select **Download action plan** to keep the evidence, suggested actions, supporting deal IDs, filters, date and threshold in a spreadsheet-friendly file. It includes all current suggestions.

## Check the calculations without using Terminal

1. Open the **Verification** tab.
2. Click **Run calculation check**.
3. A successful check says that all comparisons agree. You can download the comparison report.
4. If you change filters or the stalled threshold, run the check again; previous results disappear so they cannot be mistaken for current results.

Behind the scenes, a second method called SQL independently calculates the KPI totals, stage summaries, and each selected deal's age and risk. You do not need to learn SQL to use this button. Agreement checks the math against the same selected records; it cannot verify whether a spreadsheet reflects reality. If results disagree, keep the report and share it in this project task before relying on those results.

## Your part now

The portfolio version is complete. You do not need to run commands, install packages, or provide real company data to finish it.

1. Spend 5–10 minutes trying the sample and changing the threshold from 30 to 60 days.
2. Download the action plan and run the independent calculation check.
3. Practice the [five-minute demo](docs/DEMO_WALKTHROUGH.md).
4. Review the [case study and resume wording](docs/PORTFOLIO_CASE_STUDY.md) so it accurately describes your participation.

The [project handover](docs/PROJECT_HANDOVER.md) is your complete checklist. [Interview notes](docs/INTERVIEW_NOTES.md), [screenshots](docs/screenshots/README.md) and the [release record](docs/RELEASE_CHECKLIST.md) are saved. Additional historical analytics would be a future extension with additional date/history inputs, not unfinished work in this version.

## Ask questions with AI

Open **Ask AI** after checking your data. Connect your own OpenAI API key in the private field, preview the analysis summary, agree to sharing, then ask a question. No Terminal commands are needed. API use has separate charges; never share your key in chat. See [the simple setup and privacy guide](docs/AI_ASSISTANT.md).

## Import a workbook with your own business labels

1. Upload your file. Review **Match your columns**; recognized headers are suggestions you can change. **Review column suggestions and coverage** explains each suggestion and lists ignored columns.
2. Under **Confirm outcome meanings**, choose what each unfamiliar label means. For the regional example, choose **Signed → Won** and **Not proceeding → Lost**. These are your choices for this file, not global rules.
3. Open **Review owner-name variants**. Keep names separate, or explicitly choose a common spelling for capitalization variants. No deals are combined.
4. Map **Next Contact** if you want planned follow-up analysis. Future dates are allowed. Dates before creation must be corrected; overdue dates remain valid.
5. Click **Check data** again after any mapping or name change. Read the coverage explanation beside the results. Ignored columns are not validated.
6. Open **Action plan → Planned follow-ups** for Open deals that are overdue, due today, upcoming or not scheduled. Download the follow-up plan to keep it.

Overdue means the planned date is before the analysis date. A date today is due today. This measure does not change inactivity risk and does not prove a contact was missed. The SQL check continues to cover original KPIs, stage summaries and inactivity risk; planned follow-ups have separate automated tests.

## Uploaded, blocked or ready?

- **✅ File uploaded** confirms the file has loaded. It does not mean its records have passed validation.
- **Use these suggested outcome meanings for this file** approves the displayed synonym table, such as Signed → Won and Not proceeding → Lost. Check the business meanings first; individual dropdowns can override suggestions. There is no global rule that Signed always means Won.
- For other owner aliases, open **Review owner-name variants**, select the aliases and choose the shared name. These choices do not combine deal rows.
- Click **Check data**. If blocked, each result tab states how many issues remain and points you to the correction step.
- Open **Fix flagged records here — no workbook editing needed**. Enter verified corrections, then click **Apply corrections and recheck**. Missing money, real identifiers and impossible dates must be supplied accurately; the app cannot recover their true values by guessing.
- **✅ Ready for analysis** means the Dashboard, Action plan and Verification are unlocked. Download standardized data and any correction history you want to keep.

Whitespace and parseable numeric formats are cleaned automatically. Business synonyms and owner aliases need your approval. Corrections are stored for the current file/settings in session memory only. Changing column/outcome/owner choices or the analysis date starts a fresh correction set; your original workbook is never overwritten. Discard corrections returns to the original mapped records and revalidates them.


## Messy files: analyze what is usable now

Partial analysis is now the default. Upload, review mappings, and click **Check data**. If some rows pass, Dashboard, Action plan and Verification open for that subset. Every result tab shows the included and excluded row counts. Filters can narrow the included subset further.

Approve the proposed status synonyms to include more records; uncertain outcomes are not guessed. Missing fields alone no longer exclude records. Invalid values and duplicate IDs remain excluded, including both occurrences of a duplicate ID. Download the issue report and excluded records to review them. The excluded-record download uses standardized values; original problematic values are in the issue report. Missing amounts are never filled with zero to make a row pass.

The partial totals and win rate are not whole-file results. If no rows are usable, the app explains what to resolve first. Choose **Require every row to pass before analysis** to restore strict behavior. Corrections are revalidated before records can rejoin the analysis.


### Missing details no longer remove a deal

Leave the strict check off (the default). A deal with blank fields stays in analysis. It contributes to every calculation for which the necessary information is available:

- Missing amount: the deal is counted, but its value is unknown. Monetary cards show recorded-amount subtotals. A displayed zero with no recorded amounts is not a claim that the business value is zero.
- Missing outcome: included in total records and known total value, but not Open/Won/Lost counts or win rate.
- Missing activity date: an Open deal has **Unknown** risk, never automatically Low risk.
- Missing creation date: no age can be calculated; other available details still count. Applying a created-date filter omits records without that date.
- Missing stage or ID: a visible “Not recorded” stage or a source-row reference identifies the record; these are not guessed business values.

Each result tab has a missing-details note, field counts and a review table. Downloads retain the missing-field notes. Average value uses recorded amounts, including genuine zeros. Blank optional fields remain not recorded and do not exclude deals. Duplicate IDs, impossible dates and invalid numbers still need review. The original file is unchanged.

When new details become available, upload your **full updated file** and click **Check data** again. This replaces the current analysis; it does not append or duplicate the earlier upload. You can also use the existing in-app correction table.


### Why a record is excluded

Below the partial-analysis notice, each results tab now lists the excluded source rows, deal IDs, original flagged values and reasons. The excluded-record CSV also carries `exclusion_reason` and `original_flagged_values`. This matters for invalid dates: the standardized date can be blank, but the original invalid text is retained in the reason columns. Missing values alone are still included in default analysis. Use Data setup → Fix flagged records here to enter verified corrections, or reupload a corrected full workbook.


### Importing a company export with different headings

1. Upload the file. CSV can use commas, semicolons, tabs or pipes; Excel can contain multiple worksheets. Keep headings in the first row.
2. Review **Match your columns**. Common synonyms such as CRM ID, Contract Value, Opened On, Funnel Stage and Assigned To are recognized. Currency codes in an amount heading do not prevent a match, but the file must still use one currency; this does not convert currencies.
3. If a field is unrecognized, expand **Review column suggestions and coverage**. Spelling-based alternatives and sample values help you choose manually. A similar spelling is not proof of meaning. Your selections are preserved and ambiguous matches are not automatically chosen.
4. If the file genuinely lacks a whole core field, leave it unselected and confirm **My file does not contain some core fields — keep them unknown**. At least two core fields, including Status or Deal Value, must be mapped. Available details still contribute; missing dates or outcomes do not become invented facts.
5. Confirm the outcome suggestions. Under **Combine equivalent delay reason labels**, approve proposed delay groups when appropriate for your company. This lets matching guidance recognize terms such as “price negotiation”. Stage and delay labels can also be combined manually. Owner-name merging remains separate and optional.
6. Click **Check data**. Review the included/excluded counts, missing-detail notes and reasons beside the results. Changing an interpretation requires a fresh check and resets the corresponding analysis.

Try `data/test/flexible_business_export.csv` for a six-record fictional example with business synonyms, a semicolon separator, missing details and outcomes needing approval. All six records are included once outcome meanings are confirmed. This is still a sales-pipeline analyzer: unrelated sheets, unsupported numeric formats and unknown business meanings need user review.
