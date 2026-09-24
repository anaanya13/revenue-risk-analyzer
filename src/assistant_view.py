"""Session-only AI chat, with explicit disclosure and no shared billing key."""
import streamlit as st
from src.ai_assistant import ask_openai, build_context, context_id

SUGGESTIONS = ["Explain my KPIs in simple words.", "Which stages need attention first?",
               "Explain the largest recorded delay reasons and suggest next steps.",
               "How should I use this dashboard for a weekly review?"]


def reset_assistant():
    for name in ("ai_key", "ai_history", "ai_consent", "ai_question", "ai_context"):
        st.session_state.pop(name, None)


def render_assistant(data, analysis_date, threshold, selection_key):
    st.subheader("Ask your dashboard")
    st.caption("Ask about this selection's KPIs, bottlenecks, recorded delays or how to use the app. AI can make mistakes; check its figures against the dashboard.")
    context = build_context(data, analysis_date, threshold)
    signature = context_id(context, selection_key)
    if st.session_state.get("ai_context") != signature:
        for name in ("ai_history", "ai_consent", "ai_question"):
            st.session_state.pop(name, None)
        st.session_state.ai_context = signature
    st.caption("Changing data, filters or the threshold starts a fresh conversation and resets sharing consent.")
    with st.expander("Connect AI — simple setup", expanded=not bool(st.session_state.get("ai_key"))):
        st.markdown("1. Create an API key in your [OpenAI API account](https://platform.openai.com/api-keys). API usage is billed separately from ChatGPT.\n2. Check billing and usage limits in that account.\n3. Paste the key below, review what is shared, and tick the sharing box.")
        st.text_input("Your OpenAI API key", type="password", key="ai_key", max_chars=512)
        st.caption("Your key is handled by this Streamlit server and OpenAI for requests. It stays in this browser session's server memory, is not written to project files, and is not shared with other visitors. Use Disconnect when finished. Never paste keys into chat.")
        st.button("Disconnect and clear conversation", on_click=reset_assistant)
    with st.expander("Preview exactly which analysis summary is shared"):
        st.json(context)
    st.info("Asking sends your question, up to three recent question/answer pairs, and the summary above to OpenAI. This includes financial totals and stage/delay labels; it excludes raw rows, deal IDs and owner names. Labels or your question may still contain sensitive text—review them first.")
    st.caption("Responses are requested with storage disabled; provider security/abuse retention may still apply. See OpenAI's data policy: https://developers.openai.com/api/docs/guides/your-data")
    consent = st.checkbox("I agree to send this analysis summary and my questions to OpenAI using my API account.", key="ai_consent")
    suggestion = st.selectbox("Ideas for your first question", ["Write my own question"] + SUGGESTIONS)
    history = st.session_state.setdefault("ai_history", [])
    for message in history:
        with st.chat_message(message["role"]):
            st.text(message["content"])
    with st.form("ask_ai_form", clear_on_submit=False):
        question = st.text_area("Your question", key="ai_question", max_chars=1200,
                                placeholder="Type a question, or leave this blank to use your selected idea.")
        submitted = st.form_submit_button("Ask AI", disabled=not (st.session_state.get("ai_key") and consent))
    if not st.session_state.get("ai_key"):
        st.info("Connect your own API key above to enable answers. All other dashboard features remain available without it.")
    if submitted:
        question = question.strip() or (suggestion if suggestion != "Write my own question" else "")
        if st.session_state.get("ai_attempts", 0) >= 20:
            st.warning("This session has reached its 20-request allowance. Start a new session to continue. Your API account limits still apply.")
            return
        if not question:
            st.warning("Type a question or choose one of the suggested ideas.")
            return
        st.session_state.ai_attempts = st.session_state.get("ai_attempts", 0) + 1
        try:
            with st.spinner("Reading your analysis…"):
                answer = ask_openai(st.session_state.ai_key, question, context, history)
        except ValueError as error:
            st.error(str(error))
            return
        history.extend([{"role": "user", "content": question}, {"role": "assistant", "content": answer}])
        st.session_state.ai_history = history[-12:]
        st.rerun()
