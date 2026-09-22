"""Plain-language action plan and an optional independent calculation check."""

import json
import logging

import pandas as pd
import streamlit as st

from src.exports import csv_bytes
from src.insight_engine import generate_insights
from src.presentation import priority_badge


def render_actions(data, analysis_date, threshold, filter_settings):
    st.markdown("### Suggested next steps")
    st.caption("Suggestions use the current filters and inactivity rule. They are review prompts, not predictions. The same deal can support several suggestions; do not add their values together.")
    insights = generate_insights(data)
    for item in insights.to_dict("records"):
        with st.container(border=True, key="action_" + item["rule"]):
            priority_badge(item["priority"])
            st.markdown("#### " + item["title"])
            st.text(item["evidence"])
            st.markdown("**Next step**")
            st.text(item["next_step"])
    metadata = dict(analysis_date=analysis_date, stalled_threshold_days=int(threshold),
                    matching_deals=len(data), filters=json.dumps(filter_settings, default=str, ensure_ascii=False))
    st.download_button("Download action plan", csv_bytes(insights.assign(**metadata)),
                       "pipeline_action_plan.csv", "text/csv", on_click="ignore",
                       help="Evidence, suggested actions, supporting deal IDs, filters and calculation settings. No actions are sent to deal owners.")


def render_verification(data, analysis_date, threshold, filter_settings):
    metadata = dict(analysis_date=analysis_date, stalled_threshold_days=int(threshold),
                    matching_deals=len(data), filters=json.dumps(filter_settings, default=str, ensure_ascii=False))
    st.markdown("### Check these calculations")
    st.write("Run a second calculation using SQL to compare all KPI totals, stage summaries, and each matching deal's age and risk. Both methods use the same validated rows and filters. Agreement checks the calculations, not whether the source data is true.")
    st.caption("This runs only when requested. If you change a filter or threshold, run the check again. It uses a temporary in-memory database and does not save uploaded data.")
    if st.button("Run calculation check"):
        try:
            from src.sql_engine import compare_analysis
            report = compare_analysis(data, analysis_date, int(threshold))
        except Exception:
            logging.getLogger(__name__).exception("Independent calculation check failed")
            st.warning("The independent calculation check could not finish. Your dashboard is still available. Share this message in the project task so the check can be investigated.")
            return
        if report.matches.all():
            st.success("All {:,} calculation comparisons agree.".format(len(report)))
        else:
            st.error("Some calculations disagree. Review the comparison report before relying on these results.")
        display = report.copy()
        for column in ("python_result", "sql_result"):
            display[column] = display[column].map(lambda value: "N/A" if pd.isna(value) else str(value))
        st.dataframe(display, hide_index=True, width="stretch")
        st.download_button("Download calculation check", csv_bytes(display.assign(**metadata)),
                           "calculation_check.csv", "text/csv", on_click="ignore")
