"""User-facing learning aids, with source text rendered as plain text."""

import json

import pandas as pd
import streamlit as st

from src.explanations import delay_explanations, kpi_explanations
from src.exports import csv_bytes


def render_kpi_analysis(data):
    st.markdown("### Understand your KPIs")
    st.caption("An interpretation of your current selection, with the arithmetic behind it. No performance target or historical comparison has been supplied, so these results are not graded as good or bad.")
    explanations = kpi_explanations(data)
    for name in ("Revenue at risk", "Win rate", "Open value at risk"):
        row = explanations.loc[explanations.KPI.eq(name)].iloc[0]
        with st.expander(name + " · " + row["Result"]):
            st.text(row["What it means"])
            st.markdown("**How we calculated it**")
            st.text(row["How calculated"])
            st.markdown("**What to do next**")
            st.text(row["Suggested review"])
    with st.expander("Explain every KPI"):
        name = st.selectbox("Which KPI would you like explained?", explanations.KPI.tolist())
        row = explanations.loc[explanations.KPI.eq(name)].iloc[0]
        st.text("Current result: " + row["Result"])
        st.text("Calculation: " + row["How calculated"])
        st.text("Meaning: " + row["What it means"])
        st.text("Next step: " + row["Suggested review"])


def render_delay_analysis(data, analysis_date, threshold, settings):
    st.markdown("### Understand delays and plan a response")
    st.caption("Recorded reasons describe what is written in your file. They are not causes inferred from inactivity, and a suggested mitigation is not a promise that a deal will close.")
    with st.expander("How did we reach this delay analysis?"):
        st.markdown(
            "1. Start with the fully validated file and apply your sidebar filters.\n"
            "2. Keep **Open** deals and group them by their recorded **Delay Reason**. Blank reasons remain a separate group.\n"
            "3. Calculate inactivity from **analysis date − Last Activity Date**. A deal is stalled at or above your threshold.\n"
            "4. Count each group's Open and stalled deals, then add the full value of its stalled deals.\n"
            "5. Divide that group’s stalled count by its Open count for **stalled share**, and its stalled value by all selected stalled value for **share of exposure**.\n"
            "6. Order groups by stalled value, then Open value. Each record is grouped by its entire recorded label; combined or unfamiliar labels are not split or guessed."
        )
        st.caption("Playbooks use exact label matching after trimming spaces and ignoring letter case. Unknown labels get a general owner-review checklist. Missing reasons are not filled in automatically.")
    table = delay_explanations(data)
    if table is None:
        st.info("Map Delay Reason in Data setup to see recorded-delay analysis. The app cannot infer missing reasons from deal age or stage.")
        return
    if table.empty:
        st.info("No Open deals match these filters, so there are no current delay groups to analyze.")
        return
    st.caption("Choose a reason to see its evidence and suggested response. All groups are available, including ones with no stalled deals.")
    selected = st.selectbox("Recorded delay reason to explore", list(range(len(table))),
                            format_func=lambda i: "Not recorded (blank)" if pd.isna(table.iloc[i].delay_reason) else str(table.iloc[i].delay_reason) + " (recorded label)")
    row = table.iloc[selected]
    with st.container(border=True):
        st.text("Recorded reason: " + ("Not recorded (blank)" if pd.isna(row.delay_reason) else str(row.delay_reason)))
        st.text(f"{row.open_deals} Open deals; {row.stalled_deals} stalled; {row.revenue_at_risk:,.2f} in exposed value (file currency).")
        share = "N/A because total selected exposure is zero" if pd.isna(row.share_of_exposure) else f"{row.share_of_exposure:.1%}"
        st.text(f"Stalled share within this group: {row.stalled_share:.1%}. Share of all selected exposed value: {share}.")
        st.text(f"Average inactivity among this group's Open deals: {row.average_inactivity:.1f} days. Stalled threshold: {threshold} days.")
        if not row.stalled_deals:
            st.info("No deals in this group meet the stalled rule. The recorded reason may still deserve routine follow-up; it does not create inactivity-based exposure here.")
        st.markdown("**Suggested mitigation — confirm with the owner**")
        st.text("Guidance used: " + row.playbook)
        st.text(row.suggested_mitigation)
        st.markdown("**How to check progress**")
        st.text(row.how_to_review)
        st.caption("Record the agreed task, responsible person and review date in your source system. Re-upload its updated snapshot to reassess; the app does not track completed tasks or send messages.")
        with st.expander("Supporting stalled deal IDs"):
            ids = json.loads(row.stalled_deal_ids)
            st.text(", ".join(ids) if ids else "No stalled deal IDs in this group.")
    export = table.assign(analysis_date=analysis_date, stalled_threshold_days=int(threshold),
                          filters=json.dumps(settings, default=str, ensure_ascii=False))
    st.download_button("Download delay analysis and guidance", csv_bytes(export), "delay_analysis.csv", "text/csv", on_click="ignore",
                       help="All recorded-reason groups in this selection, with counts, exposed values, suggested responses, supporting IDs and calculation settings. Share columns are fractions from 0 to 1.")


def render_user_guide():
    with st.expander("Your dashboard guide — start here"):
        st.markdown("""
**First visit — about five minutes**

1. In **Data setup**, choose **Try sample data**, keep the **Deals** sheet and review the suggested column matches. For a repeatable example, set the analysis date to **September 22, 2026**.
2. Click **Check data**. If issues appear, download the issue report, correct the original file, and upload it again. Analytics unlock only when every row passes.
3. Open **Dashboard**. Start with Open pipeline value, Revenue at risk and Win rate. Expand **Understand your KPIs** for the arithmetic, meaning and next step.
4. Use the **sidebar** to change the stalled threshold or select a stage, owner or other filter. If hidden, reopen it with the sidebar arrow. All result tabs use the same selection; **Reset filters** restores all records but does not change the threshold.
5. Open **Action plan** for review priorities. Under **Understand delays and plan a response**, choose a recorded reason, read how it was calculated, and agree a task with the owner.
6. Open **Verification** and click **Run calculation check** to compare two implementations of the same rules. Agreement checks arithmetic, not whether your source data is true.
7. Download reports you want to keep. Update the original file after taking action, then upload the new snapshot. Nothing is sent to deal owners automatically.

**Reading the results**

- **Age** is time since creation; **inactivity** is time since last recorded activity. Current stage does not tell us time in that stage.
- **Revenue at risk** is the full value of stalled Open opportunities, not expected loss. At 30 days: Low 0–14, Medium 15–29, High 30–59, Critical 60+.
- **N/A** means a denominator or suitable population is missing, not a zero result. No closed deals means no win rate; no Open value means no exposed-value percentage.
- Clearing a filter selects no records. Status and severity filters can change win rate. Use Reset filters if an expected group disappears.
- Changing the analysis date or column mapping requires **Check data** again. Dates do not reconstruct historical statuses.

**Which download should I use?**

| Download | Where | Includes |
| --- | --- | --- |
| Standardized data / issue report | Data setup | Full mapped file after it passes, or rows needing correction |
| Stage summary | Dashboard | Current filtered Open-stage groups |
| Filtered analysis | Action plan | All matching deals, even if the review list shows only stalled ones |
| Action plan | Action plan | Suggestions and supporting IDs; suggestion amounts can overlap |
| Delay analysis and guidance | Action plan | All selected reason groups, suggested mitigations and evidence |
| Calculation check | Verification | Comparison results for the current settings |

**A practical review routine:** confirm filters → read exposure → inspect the recorded blocker → agree an owner and date → update the source record → reassess. A lower exposed value alone does not prove a mitigation worked; the rule, filters, statuses or values may have changed.
""")
