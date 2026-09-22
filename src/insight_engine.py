"""Deterministic review suggestions backed by the selected deal records."""

import json

import pandas as pd

from src.kpi_engine import sum_value

COLUMNS = ["rule", "priority", "title", "evidence", "next_step", "deal_count", "deal_value", "deal_ids"]


def generate_insights(data):
    """Consume assessed, filtered rows; suggestions never alter records or predict loss."""
    rows = []

    def add(rule, priority, title, deals, explanation, action):
        count, value = len(deals), sum_value(deals.deal_value)
        rows.append(dict(rule=rule, priority=priority, title=title,
                         evidence=f"{count:,} deals · {value:,.2f} in file currency. {explanation}",
                         next_step=action, deal_count=count, deal_value=value,
                         deal_ids=json.dumps(sorted(deals.deal_id.astype(str)), ensure_ascii=False)))

    if data.empty:
        return pd.DataFrame(columns=COLUMNS)
    opened = data.loc[data.status.eq("Open")]
    stalled = opened.loc[opened.is_stalled]
    if opened.empty:
        add("no_open", "Information", "No Open deals in this selection", opened,
            "The selected records are closed, so current inactivity risk is not assessed.",
            "Include Open in the Status filter to review current opportunities.")
    elif stalled.empty:
        add("no_stalled", "Information", "No deals meet the stalled rule", opened,
            "None of these Open deals reaches the selected inactivity threshold. This does not guarantee a sale.",
            "Continue the normal review schedule and keep activity dates current.")
    else:
        critical = stalled.loc[stalled.risk_severity.eq("Critical")]
        if not critical.empty:
            add("critical", "Review first", "Review the longest-inactive opportunities", critical,
                "Each has been inactive for at least twice the selected stalled threshold.",
                "Ask the owner to confirm whether the opportunity is still active and record a next step and date.")
        totals = stalled.groupby("stage").deal_value.agg(sum_value)
        leaders = sorted(totals.index[totals.eq(totals.max())].tolist())
        selected = stalled.loc[stalled.stage.isin(leaders)]
        add("stage_exposure", "Review first", "Review the stages with the most stalled value", selected,
            "Highest stalled value per stage: " + ", ".join(leaders) + ". Ties are included; the amount above is their combined stalled value.",
            "Review these stalled opportunities with their owners and confirm the actual blockers. Current stage does not measure time in stage.")
        for field, rule, title, action in (
            ("sales_rep", "missing_owner", "Confirm ownership of stalled deals", "Assign or confirm a responsible owner in the source file before arranging follow-up."),
            ("delay_reason", "missing_reason", "Record the blockers for stalled deals", "Ask the owner to record the actual blocker, or confirm that no blocker is known. Do not infer a cause from inactivity alone."),
        ):
            missing = stalled if field not in stalled else stalled.loc[stalled[field].isna()]
            if not missing.empty:
                explanation = ("This optional column was not mapped; the app cannot determine whether these details exist in the source."
                               if field not in stalled else "These stalled records have no value recorded in this field.")
                add(rule, "Complete details", title, missing, explanation, action)
    medium = opened.loc[opened.risk_severity.eq("Medium")]
    if not medium.empty:
        add("medium", "Watch", "Review deals approaching the stalled threshold", medium,
            "Inactivity is at least half the threshold (rounded up), but below the stalled threshold. Their value is not included in revenue at risk.",
            "Check planned next-contact dates with the owners before these opportunities become stalled.")
    return pd.DataFrame(rows, columns=COLUMNS)
