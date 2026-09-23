"""Traceable KPI explanations and recorded-delay review guidance."""

import json

import pandas as pd

from src.bottleneck_engine import summarize_bottlenecks
from src.kpi_engine import calculate_kpis


def kpi_explanations(data):
    k = calculate_kpis(data)
    number = lambda value: "N/A" if value is None else f"{value:,.2f}"
    percentage = lambda value: "N/A" if value is None else f"{value:.1%}"
    closed = k["won_deals"] + k["lost_deals"]
    return pd.DataFrame([
        {"KPI": "Open pipeline value", "Result": number(k["open_pipeline_value"]),
         "How calculated": f"Sum of Deal Value for {k['open_deals']} matching Open deals.",
         "What it means": "Potential value still in the selected pipeline; it is not booked revenue.",
         "Suggested review": "Use stage filters to see where this value is concentrated."},
        {"KPI": "Won deal value", "Result": number(k["won_deal_value"]),
         "How calculated": f"Sum of Deal Value for {k['won_deals']} matching Won deals.",
         "What it means": "The spreadsheet's recorded Won value, not accounting-recognized revenue or a monthly total.",
         "Suggested review": "Confirm the selected snapshot and filters before comparing this value with another report."},
        {"KPI": "Win rate", "Result": percentage(k["win_rate"]),
         "How calculated": f"{k['won_deals']} Won ÷ ({k['won_deals']} Won + {k['lost_deals']} Lost) = {closed} closed deals in the denominator.",
         "What it means": ("No closed outcomes are selected, so a win rate cannot be calculated." if not closed else
                           f"Of {closed} selected completed outcomes, {k['won_deals']} were Won. Open deals are excluded."),
         "Suggested review": "Compare like-for-like populations. Selecting only Won makes this 100%; no target or historical trend is supplied."},
        {"KPI": "Average deal value", "Result": number(k["average_deal_value"]),
         "How calculated": f"Total selected value {number(k['total_deal_value'])} ÷ {k['deal_count']} matching deals across all statuses.",
         "What it means": "The mean opportunity size in this selection; it can be influenced by a few large deals.",
         "Suggested review": "Inspect individual amounts in Action plan before treating the average as a typical deal."},
        {"KPI": "Deal counts", "Result": f"{k['deal_count']} total · {k['open_deals']} Open · {k['won_deals']} Won · {k['lost_deals']} Lost",
         "How calculated": "Count unique validated deal rows within the current filters, grouped by normalized status.",
         "What it means": "Counts describe the selected snapshot; they do not show growth over time.",
         "Suggested review": "Check Status filters if counts look unexpectedly small; Reset filters restores all validated records."},
        {"KPI": "Revenue at risk", "Result": number(k["revenue_at_risk"]),
         "How calculated": f"Sum of Deal Value for {k['stalled_deals']} matching Open deals whose inactivity meets or exceeds the selected threshold.",
         "What it means": "Full value attached to stalled opportunities, not predicted loss. High and Critical deals contribute.",
         "Suggested review": "Open Action plan, confirm the blockers with deal owners, and prioritize a concrete next step."},
        {"KPI": "Stalled open deals", "Result": str(k["stalled_deals"]),
         "How calculated": "Count Open deals where analysis date minus Last Activity Date is at least the stalled threshold.",
         "What it means": f"{k['stalled_deals']} of {k['open_deals']} selected Open deals meet the rule, including any zero-value deals.",
         "Suggested review": "Validate activity dates and whether each opportunity is still active before following up."},
        {"KPI": "Open value at risk", "Result": percentage(k["revenue_at_risk_share"]),
         "How calculated": f"{number(k['revenue_at_risk'])} exposed value ÷ {number(k['open_pipeline_value'])} Open pipeline value.",
         "What it means": ("Open pipeline value is zero, so this percentage is undefined." if k["revenue_at_risk_share"] is None else
                           f"{percentage(k['revenue_at_risk_share'])} of selected Open value is attached to stalled deals. This is a value share, not a loss probability."),
         "Suggested review": "Use this alongside the stalled count: a few large opportunities can account for much of the exposure."},
        {"KPI": "Average open age (days)", "Result": number(k["average_open_age"]),
         "How calculated": "Mean of analysis date minus Created Date, for matching Open deals only.",
         "What it means": "How long the selected Open opportunities have existed; it is not time in their current stage.",
         "Suggested review": "Compare with inactivity. An old opportunity may still be actively progressing."},
        {"KPI": "Average inactivity (days)", "Result": number(k["average_inactivity"]),
         "How calculated": "Mean of analysis date minus Last Activity Date, for matching Open deals only.",
         "What it means": "Average time since recorded contact/activity. N/A means there are no selected Open deals.",
         "Suggested review": "Check the deal-level list because averages can hide especially inactive opportunities."},
    ])


PLAYBOOKS = {
    "missing documents": ("Document checklist", "Ask the owner to confirm the specific missing items, send one consolidated checklist through the approved channel, and agree who will supply each item and by when.", "Review whether the requested items were received and accepted; update the recorded blocker and next activity date."),
    "incorrect information": ("Information correction", "Identify the exact inconsistent field, verify it with the responsible source, and submit a corrected record for review.", "Confirm the correction was accepted before clearing the blocker; keep a dated record of the change."),
    "customer unresponsive": ("Contact-plan review", "Confirm contact details and the agreed communication channel. Ask the owner to schedule an appropriate follow-up and check whether the customer's priority has changed.", "Record the response or lack of response and an agreed next step. Do not assume inactivity means the customer has declined."),
    "pricing / terms": ("Commercial clarification", "Ask which specific price or term is unresolved and route it to the authorized commercial owner for clarification or negotiation.", "Record the customer's response and authorized next step; do not assume a discount is necessary or promise an unapproved change."),
    "credit review pending": ("Review-status follow-up", "Ask the responsible review team whether the application is complete, what information is outstanding, and the expected next update.", "Track the review milestone and outstanding requests. This app does not make credit decisions or recommend bypassing checks."),
    "internal processing": ("Handoff review", "Identify the pending internal task, accountable owner and dependency. Confirm its expected completion date and any handoff that needs attention.", "Check whether the task progressed by the agreed date, and escalate through the normal team process if it did not."),
}


def mitigation_for(reason):
    if pd.isna(reason):
        return ("Missing reason", "Ask the deal owner to record the actual blocker, or confirm that none is known. A blank field cannot identify a cause.", "Recheck the source record after the owner updates it.")
    key = " ".join(str(reason).strip().casefold().split())
    return PLAYBOOKS.get(key, ("General owner review", "Confirm what this recorded reason means with the deal owner. Agree a specific corrective task, responsible person and review date.", "Check whether the agreed task removed the blocker; update the source record. No reason-specific playbook is configured for this label."))


def delay_explanations(data):
    summary = summarize_bottlenecks(data, "delay_reason")
    if summary is None:
        return None
    columns = ["delay_reason", "open_deals", "stalled_deals", "revenue_at_risk", "stalled_share", "share_of_exposure", "average_inactivity", "playbook", "suggested_mitigation", "how_to_review", "stalled_deal_ids"]
    total_exposure = calculate_kpis(data)["revenue_at_risk"]
    opened = data.loc[data.status.eq("Open")]
    rows = []
    for item in summary.to_dict("records"):
        reason = item["delay_reason"]
        group = opened.loc[opened.delay_reason.isna() if pd.isna(reason) else opened.delay_reason.eq(reason)]
        stalled = group.loc[group.is_stalled]
        playbook, suggestion, review = mitigation_for(reason)
        rows.append({**{key: item[key] for key in ("delay_reason", "open_deals", "stalled_deals", "revenue_at_risk", "stalled_share", "average_inactivity")},
                     "share_of_exposure": item["revenue_at_risk"] / total_exposure if total_exposure else None,
                     "playbook": playbook, "suggested_mitigation": suggestion, "how_to_review": review,
                     "stalled_deal_ids": json.dumps(sorted(stalled.deal_id.astype(str)), ensure_ascii=False)})
    return pd.DataFrame(rows, columns=columns)
