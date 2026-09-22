# Start here

## Use the online app

Open [Revenue Risk Analyzer](https://anaanya-revenue-risk-analyzer.streamlit.app/) and bookmark it. **No Terminal commands are needed for the online version.**

1. Select **Try sample data**.
2. Keep the **Deals** worksheet and suggested column matches.
3. Click **Check data**. The sample should show **120 deals and 0 issues** with a validation date on or after September 18, 2026.
4. Scroll to **Explore your pipeline** to see KPIs, aging, risk, bottlenecks, and deals to review.
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
3. Expand **What do the numbers and risk levels mean?** for definitions. With 30 days selected: Low = 0–14 inactive days, Medium = 15–29, High = 30–59, Critical = 60+. High and Critical are stalled.
4. Use **Filter the dashboard** to select status, stage, risk, and any supplied representative, lead source, industry or product. You can also filter by creation date. All dashboard results use these filters. Clearing a selection returns no deals; **Reset filters** brings them back.
5. Read **Aging and risk** and **Where are open deals getting stuck?**. Optional delay reasons and representative summaries appear when those fields are mapped.
6. Review the stalled deals under **Deals to review**. Download **filtered analysis** to keep all matching rows with their age, risk, analysis date and threshold, or download the **stage summary**. The earlier standardized download still contains the full validated file.

**Revenue at risk means the full value of stalled Open deals. It is exposure to review, not a forecast that this money will be lost.** Deal age counts days since creation; inactivity counts days since last activity. Current stage alone cannot tell us time spent in that stage. Won value is the amount in the spreadsheet, not accounting-recognized revenue.

The **Analysis / validation date** above Check data controls both validation and aging. Changing it requires checking the file again. Use a snapshot from the date you want to analyze; changing this date cannot reconstruct historical statuses. No closed deals means win rate is N/A, and no Open value means the percentage at risk is N/A.

## Your next project step

Try the sample with 30 days, then 60 days, and compare the stalled deals and value. Try a stage filter and download the analysis. No Terminal commands are needed online. The next development work is broader explainable recommendations, followed by SQL and portfolio/interview material. See [the progress record](docs/PROGRESS.md).
