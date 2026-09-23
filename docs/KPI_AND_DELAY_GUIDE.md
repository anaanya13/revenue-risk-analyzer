# Understand the results and decide what to review

The app now includes **Your dashboard guide — start here** above the tabs. It is available before any upload and stays accessible while you explore results.

## KPI interpretation

In Dashboard, open **Understand your KPIs**. Revenue at risk, Win rate and Open value at risk have quick explanations. **Explain every KPI** covers the other cards, the four status counts together, and average inactivity.

Each explanation shows the current selected result, how it was calculated, what it means, and a suggested review. It uses the same filtered records as the cards. It does not label performance good or bad without a supplied benchmark or claim growth without historical data.

Example: 27 Won and 23 Lost gives 27 / 50 = 54% win rate. Open deals are excluded. If you filter to Won only, the denominator changes and the result becomes 100%; this does not mean the original pipeline improved. No closed outcomes gives N/A.

## How the delay analysis is derived

In Action plan, choose a reason under **Understand delays and plan a response**. The app:

1. Starts from your validated file and current filters.
2. Keeps Open deals and groups them by the entire recorded Delay Reason label.
3. Measures days from Last Activity Date to the analysis date.
4. Flags inactivity at or above the selected stalled threshold.
5. Counts the Open/stalled records and sums the stalled records' full values.
6. Displays supporting stalled deal IDs so you can trace the result.

**Stalled share** means stalled count / Open count within this reason. **Share of exposure** means this reason's stalled value / all selected stalled value. These are different denominators. If the total stalled value is zero, share of exposure is N/A even if zero-value deals are stalled.

Reasons are recorded source fields, not causes discovered by an AI model. Blank reasons remain unknown; optional reasons that were not mapped cannot be inferred. Combined or unfamiliar labels are not split automatically. A recorded reason can appear on a recent, non-stalled deal; that record does not contribute to inactivity-based exposure.

## Suggested mitigations

| Recorded reason | Review suggestion |
| --- | --- |
| Missing Documents | Confirm missing items; agree a consolidated checklist, owner and due date. |
| Incorrect Information | Identify the incorrect field, verify it and confirm the correction was accepted. |
| Customer Unresponsive | Verify contact details and preferred channel; agree an appropriate contact plan with the owner. |
| Pricing / Terms | Clarify the specific unresolved issue and involve the authorized commercial owner. |
| Credit Review Pending | Confirm completeness and expected next update with the responsible review team. |
| Internal Processing | Identify the pending task, dependency, owner and expected completion date. |
| Blank | Ask what the actual blocker is; do not invent one. |
| Any other label | Clarify the meaning, then agree a task, owner and review date. |

Matching ignores case and extra whitespace but otherwise requires the known label. The interface identifies which playbook was used. Suggestions do not authorize discounts, bypass credit checks, predict a win or automatically contact anyone.

## Make the analysis useful

Confirm the record with its owner, agree a specific task and date, and update the source system after taking action. Re-upload the revised snapshot to reassess. A lower exposure number alone does not prove mitigation worked: changed filters, thresholds, values or statuses can also change the result.

Download **delay analysis and guidance** for all current reason groups, evidence IDs, suggestions and calculation settings. Fraction columns in the CSV run from 0 to 1; the interface presents them as percentages. This app does not maintain a task-completion history.
