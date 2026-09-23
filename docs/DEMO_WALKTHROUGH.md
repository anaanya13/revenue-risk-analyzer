# Demonstrate the project in five minutes

Open [Revenue Risk Analyzer](https://anaanya-revenue-risk-analyzer.streamlit.app/). Use the built-in synthetic data for a public demonstration.

## 1. Explain the problem

“This app turns a sales-pipeline spreadsheet into a review of inactive opportunities and potential revenue exposure. Different companies can match their own column names to the same analysis.”

Select **Try sample data**, keep the Deals worksheet, and show the suggested column mapping. Set **Analysis / validation date** to **September 22, 2026**, then click **Check data** so the demonstration is repeatable.

## 2. Explain the quality gate

The sample has 120 deals and zero issues. Explain that a file must pass every check before analytics are available. The app never removes failing rows to produce a cleaner result. The messy test file demonstrates issue reporting; if you switch to it, return to the original sample and check it again before continuing.

## 3. Explain the results

Open the **Dashboard** tab. Threshold and filter controls are in the left sidebar.

With all filters selected and a 30-day threshold, the sample shows:

| Measure | Expected result on September 22, 2026 |
| --- | --- |
| Open / Won / Lost deals | 70 / 27 / 23 |
| Open pipeline value | 3,102,500 |
| Won deal value | 1,046,000 |
| Win rate | 54% |
| Stalled Open deals | 14 |
| Revenue at risk | 647,000 |

Explain: “Revenue at risk is the full value of Open deals inactive for at least 30 days. It is exposure for review, not a prediction that the money will be lost. Win rate counts Won divided by Won plus Lost; Open deals are excluded.”

## 4. Demonstrate an action

Open **Action plan** and read one **Suggested next steps** card. Show its supporting count/value and practical next step. Download the action plan; its supporting IDs let someone trace the suggestion to actual rows. Explain that several cards can reference the same deal, so their values should not be added.

Change the stalled threshold to 60 days and observe the updated results. Apply a stage filter, then **Reset filters** and restore the threshold to 30. Explain that deal age and inactivity are different: an old deal with recent activity may have Low inactivity risk.

## 5. Demonstrate verification

Open **Verification**, select **Run calculation check**, and show that the independent calculations agree. Explain that SQL derives age/risk again from the selected base dates, then checks KPIs and stage summaries against Python. Download the comparison report if useful.

## Portfolio wording you can support

“Built and deployed a Streamlit sales-pipeline analyzer with configurable column mapping, validation, inactivity-based revenue-risk analysis, interactive filters, evidence-backed action plans, and independent DuckDB SQL verification; covered calculations and workflows with 79 automated tests.”

Describe your own role accurately, including the AI-assisted development process and how you reviewed requirements and tested the user experience. Do not claim commercial revenue recovery, predictive model accuracy, or time saved at a company: this version was demonstrated with synthetic data.

## Questions to be ready for

- Why 30 days? It is an adjustable starting rule, not a universally correct sales policy.
- Why not time in stage? Current stage is only a snapshot; stage-entry history is required.
- Why not monthly revenue trends? Close dates are not mapped yet, and won value is not accounting revenue.
- What does SQL verification prove? That two implementations agree for the same selected validated data and rules. It does not prove the source data is true.
- What would you improve next? Agree on close-date/history inputs, then add supported historical measures; assess real workflow needs before adding persistence or accounts. The version-1 screenshot gallery and handover are already saved.
