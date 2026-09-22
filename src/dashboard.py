"""Beginner-friendly Streamlit presentation for the analytics milestone."""

from math import ceil

import pandas as pd
import plotly.express as px
import streamlit as st

from src.bottleneck_engine import summarize_bottlenecks
from src.action_dashboard import render_actions
from src.column_mapper import FIELD_LABELS
from src.exports import csv_bytes
from src.filters import FILTER_FIELDS, filter_deals, filter_options
from src.kpi_engine import calculate_kpis
from src.risk_engine import RISK_LEVELS, aging_distribution, assess_deals, risk_distribution

LABELS = {
    **FIELD_LABELS, "risk_severity": "Risk severity", "deal_age_days": "Open deal age (days)",
    "days_inactive": "Days inactive", "is_stalled": "Stalled", "age_bucket": "Open deal age",
    "analysis_date": "Analysis date", "stalled_threshold_days": "Stalled threshold (days)",
    "open_deals": "Open deals", "open_value": "Open pipeline value", "stalled_deals": "Stalled deals",
    "revenue_at_risk": "Revenue at risk", "stalled_share": "Stalled deals (%)",
    "average_open_age": "Average open age (days)", "average_inactivity": "Average inactivity (days)",
    "follow_ups_recorded": "Deals with follow-up counts", "average_follow_ups": "Average follow-ups",
}
COLORS = {"Low": "#15803d", "Medium": "#b45309", "High": "#dc2626", "Critical": "#7e22ce"}


def _number(value, decimals=0):
    return "N/A" if value is None else format(value, ",.{}f".format(decimals))


def _percent(value):
    return "N/A" if value is None else "{:.1%}".format(value)


def _table(data):
    display = data.copy()
    if "stalled_share" in display:
        display["stalled_share"] *= 100
    return display.rename(columns=LABELS)


def render_dashboard(cleaned, analysis_date, context_key):
    st.divider()
    st.subheader("4. Explore your pipeline")
    st.caption("Analytics milestone · All amounts use your file's currency. No currency conversion is applied.")
    threshold = st.number_input(
        "Stalled after this many days without activity", min_value=1, max_value=3650, value=30, step=1,
        key="threshold_" + context_key,
        help="An open deal becomes stalled on this exact day. Changes update the dashboard immediately.",
    )
    st.write("**Analysis date:** {} · **Stalled threshold:** {} days".format(analysis_date, threshold))
    st.caption("The analysis date is also used by the data-quality checker above. Changing that date requires Check data again.")
    with st.expander("What do the numbers and risk levels mean?"):
        medium = ceil(threshold / 2)
        st.markdown(
            "- **Open pipeline value:** value of Open deals.\n"
            "- **Won deal value:** recorded value of Won deals, not audited accounting revenue.\n"
            "- **Win rate:** Won ÷ (Won + Lost). Open deals are excluded; no closed deals means N/A.\n"
            "- **Revenue at risk:** full value of stalled Open deals (High + Critical). This is exposure for review, not predicted loss.\n"
            "- **Open deal age:** days since creation. **Days inactive:** days since last activity. Closed deals are not aged.\n"
            "- **Low:** fewer than {} inactive days. **Medium:** at least {} but fewer than {}.\n"
            "- **High:** at least {} but fewer than {} inactive days. **Critical:** at least {}.\n"
            "- All cards, charts, summaries and analysis downloads use the same filters. Status/severity filters can change the win-rate denominator."
            .format(medium, medium, threshold, threshold, 2 * threshold, 2 * threshold)
        )
        if threshold == 1:
            st.caption("At a one-day stalled threshold, the Medium interval is empty: 0 days is Low, 1 High, and 2+ Critical.")
        st.caption("A historical analysis date does not reconstruct past statuses. Use a file captured on the date you want to analyze.")
    try:
        assessed = assess_deals(cleaned, analysis_date, int(threshold))
    except ValueError as error:
        st.error(str(error))
        return

    prefix = "filter_" + context_key + "_"
    with st.expander("Filter the dashboard", expanded=True):
        if st.button("Reset filters", key="reset_" + context_key):
            for key in list(st.session_state):
                if key.startswith(prefix):
                    del st.session_state[key]
        selections = {}
        columns = st.columns(3)
        for index, field in enumerate(f for f in FILTER_FIELDS if f in assessed):
            with columns[index % 3]:
                options = filter_options(assessed, field)
                selections[field] = st.multiselect(
                    LABELS[field], options, default=options,
                    format_func=lambda v: "Not recorded (blank)" if v is None else v,
                    key=prefix + field,
                )
        st.caption("All values are selected initially. Clearing a selection means no matching deals. Reset filters restores all records.")
        use_dates = st.checkbox("Filter by created date", key=prefix + "use_dates")
        start = end = None
        if use_dates:
            left, right = st.columns(2)
            start = left.date_input("Created on or after", assessed.created_date.min().date(), key=prefix + "from")
            end = right.date_input("Created on or before", assessed.created_date.max().date(), key=prefix + "to")
            if start is None or end is None:
                st.warning("Choose both created dates.")
                return
    try:
        filtered = filter_deals(assessed, selections, start, end)
        kpis = calculate_kpis(filtered)
    except ValueError as error:
        st.warning(str(error))
        return
    st.caption("Showing {:,} of {:,} validated deals. Filters affect analytics only; the standardized-data download above keeps the full file.".format(len(filtered), len(assessed)))
    if filtered.empty:
        st.info("No deals match these filters. Change the selections or use Reset filters.")
        return

    st.markdown("### Pipeline overview")
    for row in (
        (("Open pipeline value", _number(kpis["open_pipeline_value"], 2), "Open deals only."),
         ("Won deal value", _number(kpis["won_deal_value"], 2), "Value recorded on Won deals."),
         ("Win rate", _percent(kpis["win_rate"]), "Won count divided by Won plus Lost count in these filters."),
         ("Average deal value", _number(kpis["average_deal_value"], 2), "All deals matching these filters.")),
        (("Matching deals", str(kpis["deal_count"]), "All matching statuses."),
         ("Open deals", str(kpis["open_deals"]), "Currently Open."),
         ("Won deals", str(kpis["won_deals"]), "Currently Won."),
         ("Lost deals", str(kpis["lost_deals"]), "Currently Lost.")),
        (("Revenue at risk", _number(kpis["revenue_at_risk"], 2), "Value of stalled Open deals. Exposure, not predicted loss."),
         ("Stalled open deals", str(kpis["stalled_deals"]), "Inactivity at or above the threshold."),
         ("Open value at risk", _percent(kpis["revenue_at_risk_share"]), "Revenue at risk divided by Open pipeline value. N/A when Open value is zero."),
         ("Average open age (days)", _number(kpis["average_open_age"], 1), "Days since creation, for Open deals only.")),
    ):
        for column, (label, value, help_text) in zip(st.columns(4), row):
            column.metric(label, value, help=help_text)
    st.caption("Average inactivity among matching Open deals: {} days.".format(_number(kpis["average_inactivity"], 1)))

    render_actions(filtered, analysis_date, threshold, {
        "selections": selections, "created_from": start, "created_to": end,
    })

    st.markdown("### Aging and risk")
    if not kpis["open_deals"]:
        st.info("There are no Open deals in this selection, so there is no current pipeline exposure or open-deal aging to assess.")
    else:
        left, right = st.columns(2)
        with left:
            st.write("**Open deals by inactivity risk**")
            risks = risk_distribution(filtered)
            chart = px.bar(risks, x="risk_severity", y="deals", color="risk_severity",
                           color_discrete_map=COLORS, category_orders={"risk_severity": list(RISK_LEVELS)},
                           hover_data=["deal_value"], labels={"risk_severity": "Risk severity", "deals": "Open deals", "deal_value": "Deal value"})
            chart.update_layout(showlegend=False)
            st.plotly_chart(chart, use_container_width=True)
        with right:
            st.write("**Open deals by age since creation**")
            ages = aging_distribution(filtered)
            chart = px.bar(ages, x="age_bucket", y="deals", hover_data=["deal_value"],
                           labels={"age_bucket": "Open deal age", "deals": "Open deals", "deal_value": "Deal value"},
                           color_discrete_sequence=["#0f766e"])
            st.plotly_chart(chart, use_container_width=True)
        st.caption("An old deal can have recent activity and Low risk. Age and inactivity answer different questions.")

    st.markdown("### Where are open deals getting stuck?")
    st.caption("These summaries show exposure grouped by the CURRENT stage, owner or recorded reason. They do not measure time spent in a stage or prove the cause of a delay.")
    stages = summarize_bottlenecks(filtered, "stage")
    if not stages.empty:
        if kpis["revenue_at_risk"] > 0:
            top_value = stages.iloc[0]["revenue_at_risk"]
            leaders = stages.loc[stages.revenue_at_risk.eq(top_value), "stage"].astype(str).tolist()
            st.info("Highest stalled value by stage: {} ({} each). Start by reviewing the stalled deals in these stages.".format(
                ", ".join(leaders), _number(top_value, 2)))
        else:
            st.success("No matching Open deals meet the current stalled threshold.")
        chart = px.bar(stages, x="revenue_at_risk", y="stage", orientation="h",
                       labels={"revenue_at_risk": "Revenue at risk (file currency)", "stage": "Current stage"},
                       color_discrete_sequence=["#b45309"])
        chart.update_layout(yaxis={"categoryorder": "array", "categoryarray": stages.stage.tolist(), "autorange": "reversed"})
        st.plotly_chart(chart, use_container_width=True)
        st.dataframe(_table(stages).round(2), hide_index=True, width="stretch")
        stage_export = stages.assign(analysis_date=analysis_date, stalled_threshold_days=int(threshold))
        st.download_button("Download stage summary", csv_bytes(stage_export), "stage_bottlenecks.csv", "text/csv", on_click="ignore")
    else:
        st.caption("Stage summaries are empty because there are no matching Open deals.")
    for field, title in (("delay_reason", "Recorded delay reasons"), ("sales_rep", "Sales representative workload")):
        with st.expander(title):
            summary = summarize_bottlenecks(filtered, field)
            if summary is None:
                st.info("Map {} in the optional fields to see this summary.".format(LABELS[field]))
            elif summary.empty:
                st.info("No matching Open deals to summarize.")
            else:
                st.caption("Blank values mean not recorded. Follow-up averages use only supplied counts, including zero; the count column shows coverage.")
                st.dataframe(_table(summary).round(2), hide_index=True, width="stretch")
                if field == "delay_reason" and filtered.loc[filtered.status.eq("Open"), field].isna().all():
                    st.info("No delay reasons are recorded for these Open deals; no cause can be identified from this file.")

    st.markdown("### Deals to review")
    show_all = st.checkbox("Show all matching deals, including closed deals", key="show_all_" + context_key)
    review = filtered.copy() if show_all else filtered.loc[filtered.is_stalled].copy()
    review["_priority"] = review.risk_severity.map({"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Closed": 4})
    review = review.sort_values(["_priority", "deal_value", "days_inactive"], ascending=[True, False, False], kind="stable").drop(columns="_priority")
    columns = [c for c in ("deal_id", "deal_value", "stage", "status", "sales_rep", "deal_age_days", "days_inactive", "risk_severity", "is_stalled", "delay_reason", "follow_ups") if c in review]
    st.caption("Default: stalled Open deals, ordered by severity, then deal value and inactivity. Closed deals have no inactivity assessment.")
    if review.empty:
        st.info("No stalled deals in this selection. Select Show all matching deals to inspect the other records.")
    else:
        st.dataframe(_table(review[columns]), hide_index=True, width="stretch")
    st.download_button(
        "Download filtered analysis", csv_bytes(filtered), "pipeline_analysis.csv", "text/csv", on_click="ignore",
        help="All matching deals with risk, age, analysis date and threshold. Independent of the deal-list checkbox.",
    )
