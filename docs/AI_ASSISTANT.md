# Ask your dashboard

The **Ask AI** tab answers flexible questions about your selected KPIs, stage bottlenecks, recorded delay reasons and how to use the app. Validate your data first, then open that tab.

## Connect without using Terminal

1. Open [your OpenAI API account](https://platform.openai.com/api-keys) and create an API key. Do not send the key in this project chat or commit it to GitHub.
2. Check API billing and usage limits in your OpenAI account. API usage is billed separately from ChatGPT.
3. In **Ask AI → Connect AI — simple setup**, paste the key into the password field.
4. Open the summary preview. It contains selected financial totals and stage/delay labels, but no raw rows, deal IDs or owner names. Your question can also contain sensitive information, so review it before sending.
5. Tick the sharing agreement. Choose a suggested question or type your own, then click **Ask AI**.
6. Ask follow-up questions. Click **Disconnect and clear conversation** when finished.

Examples: “Explain my KPIs”; “Which stage has the most exposed value?”; “What might we do about the recorded Missing Documents delays?”; “How do these filters affect win rate?”

## What to expect

- GPT-4.1 mini receives precomputed results for the current filters, date and threshold. It does not calculate the dashboard itself, access the full workbook, browse the web, contact owners or change records.
- Up to 30 highest-exposure groups each for stage and reason are included; the preview shows total and included group counts. It cannot identify individual deals or owners. Use the Action plan deal table for that.
- Suggestions are possible next steps, not verified causes or guaranteed recovery. Check AI answers against the visible figures.
- Data/filter/threshold changes clear the conversation and sharing consent. Up to three recent question/answer pairs are sent for context; six pairs remain visible.
- No request occurs without a key, consent and pressing Ask AI. Responses are limited to 900 output tokens, questions to 1,200 characters and attempts to 20 per browser session. These limits are not an account-wide spending cap; use your API account controls.
- The key and chat live in Streamlit session memory, never project files. This hosted server handles the key to make requests; only enter a key if you trust the host. Other visitors must use their own keys. There is no shared project billing credential.
- The API request uses `store: false`. This does not eliminate all provider retention; see [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data). Connection errors are sanitized and never automatically retried.

## Verification and remaining activation

Automated tests mock the API rather than spend money or send real data. They cover context totals and exclusions, missing/empty data, reset behavior, consent gating, request limits, errors and successful conversation rendering. An actual provider response still needs a valid API key and funded/permitted API account; no live paid request has been made during implementation.

Implementation follows the official [Responses API documentation](https://developers.openai.com/api/docs/guides/migrate-to-responses) and [GPT-4.1 mini model reference](https://developers.openai.com/api/docs/models/gpt-4.1-mini).
