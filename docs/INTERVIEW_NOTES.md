# Explain your project confidently

Use these notes to understand and practice the work. They are not claims that you personally wrote every line of code.

## A 30-second introduction

“I developed a sales-pipeline analytics project with AI coding assistance. The user can upload Excel or CSV data, match their columns, and resolve quality issues before viewing a dashboard. It highlights inactive Open deals, quantifies their pipeline exposure and suggests traceable review actions. I focused on making the definitions clear and the workflow usable for a non-technical person. The project includes automated tests and an independent SQL comparison.”

## Be clear about your role

Describe the business problem and requirements you selected, the workflow decisions you made, and the parts you personally reviewed or tested. Say that implementation was AI-assisted. Before stating that you validated the user experience, complete the walkthrough yourself. Do not present tools used by the project as skills you can independently demonstrate unless that is true.

## Questions and plain-language answers

**What is revenue at risk?** The full value of stalled Open opportunities under the selected inactivity rule. At a 30-day threshold, an Open deal with 30 or more inactive days is stalled. This is exposure for review, not expected financial loss.

**How do the risk levels work?** With 30 days selected: Low is 0–14 inactive days, Medium 15–29, High 30–59, and Critical 60 or more. High and Critical are stalled. With a different threshold, Medium starts at half rounded up, High at the threshold, and Critical at twice it.

**What is the difference between age and inactivity?** Age starts on Created Date; inactivity starts on Last Activity Date. An opportunity created 100 days ago but contacted yesterday has age 100 and inactivity 1. It need not be stalled.

**Why exclude Open deals from win rate?** Their outcomes are not known. Won / (Won + Lost) compares completed outcomes. The sample has 27 Won and 23 Lost, so 27 / 50 = 54%. Filters can change this denominator.

**Why not remove bad rows?** That could hide problems and distort totals. The app reports the source row and issue, then asks for corrections before showing analytics. Duplicate IDs flag every occurrence rather than selecting a favorite copy.

**How are missing values handled?** Required values must pass validation. Optional missing fields disable or qualify the corresponding analysis. Missing follow-up counts are excluded from averages; a recorded zero remains a real observation. Undefined ratios display N/A, not zero.

**What makes a bottleneck?** The app groups stalled Open value and counts by the current stage, plus optional owner/reason. This shows where review is concentrated; it does not measure time in that stage or establish causation.

**How are recommendations generated?** Fixed explainable rules identify Critical deals, highest-exposure stages (including ties), missing owner/reason details and Medium-risk watch items. Every card has supporting counts and value, and its download lists IDs. Several suggestions can include the same deal, so their values overlap.

**Why add SQL if Python already works?** A second implementation checks the same definitions independently and provides demonstrable SQL work. SQL recomputes age, inactivity and risk from the selected base dates, then calculates KPIs and grouped summaries. It does not establish that the input data is true and is not claimed to be faster.

**Which SQL concepts did the project use?** CASE for categories, date differences for aging, filtered aggregates for Open/Won/Lost subsets, GROUP BY for stages, common table expressions for readable steps, and NULLIF for zero denominators. Review the three saved queries in `sql/` before discussing them in detail.

**What happens when you change filters?** The same filtered population drives all dashboard results and action plans. Clearing a selection yields no matches. The full standardized download remains unfiltered. A previous calculation check disappears and must be rerun.

**Where is the data stored?** The application processes the active file and does not create a persistent upload/analysis database. DuckDB uses a temporary in-memory connection for each check. The user must download outputs to keep them. GitHub holds the code and synthetic examples.

**How was it tested?** The 69-test suite covers inputs, cleaning, mappings, rules, boundaries, filters, exports, recommendation evidence and app interactions. A deliberately incorrect Python-derived assessment is caught by the SQL comparison test. The live sample check produced 555 agreeing comparisons.

**What is the main limitation?** It is a snapshot tool tested with synthetic examples. Without mapped close dates or stage-entry history, it cannot support time-to-close, monthly outcome trends or historical conversion claims. There is no predictive model.

## A small example to practice by hand

Suppose the analysis date is September 22. An Open opportunity worth 10,000 was created August 1 and last contacted August 23. Its age is 52 days and its inactivity is 30 days. At threshold 30 it is High, stalled, and contributes 10,000 to revenue at risk. At threshold 60 it is Medium, not stalled, and contributes zero to revenue at risk. Its recorded value remains 10,000 in Open pipeline value in both cases.

## Before an interview

Open the live link once, set the saved demonstration date/threshold, practice changing a filter, download the action plan and run the calculation check. Keep the screenshot gallery as a backup demonstration. If you do not know an implementation detail, explain the part you understand and point to the saved code rather than guessing.
