# Start here

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

If issues appear, use the row-level report to locate them in your original file. Correct the source file and upload it again. The cleaned download becomes available only when **every row passes**. The checker does not remove any records.

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
