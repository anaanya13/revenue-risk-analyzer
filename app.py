"""The user interface. File handling and business rules live in src/."""

from datetime import date
from hashlib import sha256
from pathlib import Path

import streamlit as st

from src.column_mapper import (
    OPTIONAL_FIELDS, REQUIRED_FIELDS, mapping_errors, standardize_columns, suggest_mapping,
)
from src.data_loader import DataLoadError, excel_sheet_names, load_pipeline
from src.data_validator import validate_data
from src.exports import csv_bytes
from src.dashboard import render_dashboard
from src.presentation import apply_theme, render_hero
from src.explanation_views import render_user_guide

ROOT = Path(__file__).resolve().parent
DEMO_FILES = {
    "Try sample data": ROOT / "data/sample/revenue_risk_sample_data.xlsx",
    "Try messy test data": ROOT / "data/test/messy_pipeline_data.csv",
    "Try alternate column names": ROOT / "data/test/alternate_company_data.csv",
}


def main():
    st.set_page_config(page_title="Revenue Risk Analyzer", page_icon="📊", layout="wide")
    apply_theme()
    render_hero()
    render_user_guide()
    setup, dashboard, actions, verification, assistant = st.tabs(["Data setup", "Dashboard", "Action plan", "Verification", "Ask AI"])
    st.session_state["import_notice"] = "Choose a file or sample in Data setup, then click Check data."
    with setup:
        prepared = prepare_data()
    if prepared is None:
        from src.assistant_view import reset_assistant
        reset_assistant()
        with assistant:
            st.subheader("Ask your dashboard")
            st.info(st.session_state["import_notice"])
        for panel, heading, message in (
            (dashboard, "Your pipeline, at a glance", "Choose a file or sample in Data setup, then click Check data to unlock your dashboard."),
            (actions, "A focused plan for your next review", "Your evidence-backed action plan will appear after the entire file passes its data checks."),
            (verification, "Confidence in every calculation", "Once your data is ready, compare the dashboard calculations with an independent SQL check here."),
        ):
            with panel:
                st.subheader(heading)
                st.info(st.session_state["import_notice"])
        with st.sidebar:
            st.markdown("### Your workspace")
            st.caption("Filters become available after your data passes its checks.")
        return
    cleaned, as_of, analytics_key = prepared
    coverage = st.session_state.get('analysis_coverage', {})
    if coverage.get('excluded_rows', 0):
        for panel in (dashboard, actions, verification, assistant):
            with panel:
                st.warning("PARTIAL ANALYSIS — {} of {} uploaded rows included; {} excluded. All figures and recommendations describe the included rows only. Review the issue list in Data setup. Filters may reduce this further.".format(coverage['included_rows'], coverage['uploaded_rows'], coverage['excluded_rows']))
    render_dashboard(cleaned, as_of, analytics_key, dashboard, actions, verification, assistant)


def prepare_data():
    with st.expander("Start here: quick guide and project notes"):
        st.markdown(
            "1. Choose **Try sample data** below, keep the Deals worksheet and suggested column matches.\n"
            "2. Click **Check data**, then open the **Dashboard** tab.\n"
            "3. Review the KPIs and **Suggested next steps**. Change the stalled threshold or filters to explore.\n"
            "4. Download the action plan. Open **Verification** to run the independent check.\n\n"
            "For the saved portfolio example, use **September 22, 2026** as the analysis date and **30 days** as the threshold. "
            "Risk here means pipeline exposure to review, not a forecast of lost revenue."
        )
        st.markdown(
            "[Beginner guide](https://github.com/anaanya13/revenue-risk-analyzer/blob/main/START_HERE.md) · "
            "[Five-minute demo](https://github.com/anaanya13/revenue-risk-analyzer/blob/main/docs/DEMO_WALKTHROUGH.md) · "
            "[Project handover](https://github.com/anaanya13/revenue-risk-analyzer/blob/main/docs/PROJECT_HANDOVER.md)"
        )
        st.caption("The app does not save an analysis history. Download any results you want to keep before closing or refreshing the session.")

    st.subheader("1. Choose your data")
    source = st.radio("Data source", ["Upload a file"] + list(DEMO_FILES), horizontal=True)
    if source == "Upload a file":
        upload = st.file_uploader("Upload your sales pipeline file", type=["csv", "xlsx"])
        if upload is None:
            st.info("Choose an Excel or CSV file, or select Try sample data to explore the app.")
            return
        content, filename = upload.getvalue(), upload.name
    else:
        path = DEMO_FILES[source]
        try:
            content, filename = path.read_bytes(), path.name
        except OSError:
            st.error("The example file is missing. See START_HERE.md in your project folder.")
            return
        st.caption("Synthetic practice data. This does not represent a real company's performance.")

    fingerprint = sha256(content + filename.encode()).hexdigest()[:16]
    sheet = None
    try:
        if filename.lower().endswith(".xlsx"):
            sheets = excel_sheet_names(content)
            sheet = st.selectbox("Worksheet containing deals", sheets, key="sheet_" + fingerprint)
        raw = load_pipeline(content, filename, sheet)
    except DataLoadError as error:
        st.error(str(error))
        return

    source_key = fingerprint + str(sheet)
    st.success("✅ File uploaded: {} — {:,} rows and {} columns.".format(filename, len(raw), len(raw.columns)))
    st.session_state["import_notice"] = "Your file is uploaded. Review its column and outcome choices in Data setup, then click Check data to validate it."
    with st.expander("Preview original data", expanded=False):
        st.dataframe(raw.head(10).astype("string"), hide_index=True, width="stretch")
    st.subheader("2. Match your columns")
    st.write("Check the suggestions below. Each field must use a different column from your file.")
    options = [None] + list(raw.columns)
    suggestions = suggest_mapping(raw.columns)
    mapping = {}
    for group, title in ((REQUIRED_FIELDS, "Required fields"), (OPTIONAL_FIELDS, "Optional fields")):
        st.markdown("**{}**".format(title))
        columns = st.columns(3)
        for index, (field, label) in enumerate(group.items()):
            with columns[index % 3]:
                mapping[field] = st.selectbox(
                    label + (" *" if field in REQUIRED_FIELDS else ""), options,
                    index=options.index(suggestions[field]),
                    format_func=lambda value: "— Not selected —" if value is None else value,
                    key="map_{}_{}".format(source_key, field),
                )

    from src.import_views import review_import, show_coverage
    from src.import_choices import apply_choices
    outcomes, owners, choice_audit, ignored = review_import(raw, mapping, source_key)
    errors = mapping_errors(raw.columns, mapping)
    for error in errors:
        st.warning(error)
    if errors:
        st.session_state["import_notice"] = "Your file is uploaded, but column mapping needs attention in Data setup. " + " ".join(errors)

    st.subheader("3. Check data quality")
    col1, col2 = st.columns(2)
    with col1:
        date_order = st.selectbox(
            "How are text dates written?", ["Month / Day / Year", "Day / Month / Year"],
            help="For example, 04/06/2026 means April 6 or June 4. Dates written as 2026-06-04 stay the same.",
            key="date_order_" + source_key,
        )
    with col2:
        as_of = st.date_input(
            "Analysis / validation date", value=date.today(), key="as_of_" + source_key,
            help="Used for both date validation and deal aging. For a historical file, use its snapshot date. This does not reconstruct past statuses.",
        )
    st.caption(
        "Amounts use a dot for decimals and commas for thousands (12,500.50). Use one currency per file. "
        "Confirm outcome meanings above. Blank outcomes still need correction in the source."
    )
    strict = st.checkbox("Require every row to pass before analysis", value=False, key="strict_" + source_key, help="Off: analyze valid rows now and keep unresolved rows in the issue list. On: block all analysis until every row passes.")
    signature = (strict, source_key, tuple(mapping.items()), date_order, str(as_of), tuple(outcomes.items()), tuple(owners.items()))
    if as_of is None:
        st.warning("Choose a validation date before checking the file.")
    if st.button("Check data", type="primary", disabled=bool(errors) or as_of is None):
        st.session_state["checked_signature"] = signature
    if errors or as_of is None or st.session_state.get("checked_signature") != signature:
        return

    mapped = apply_choices(standardize_columns(raw, mapping), outcomes, owners)
    from src.repair_view import repair_and_validate
    repair_key = sha256(repr(signature).encode()).hexdigest()[:16]
    result = repair_and_validate(mapped, repair_key, date_order.startswith("Day"), as_of)
    st.divider()
    st.subheader("Your data-quality results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Deals checked", len(raw))
    col2.metric("Rows needing attention", result.invalid_row_count)
    col3.metric("Issues found", len(result.issues))
    show_coverage(mapping, ignored)
    if choice_audit:
        with st.expander("Review applied outcome and owner choices"):
            st.dataframe(choice_audit, hide_index=True, width="stretch")
    if result.is_valid:
        st.success("✅ Ready for analysis: your data passed all current checks. Dashboard, Action plan and Verification are unlocked.")
    else:
        st.session_state["import_notice"] = "Your file is uploaded, but analysis is blocked by {} issues across {} rows. In Data setup, approve or adjust outcome meanings and use Fix flagged records here, then apply corrections and recheck. No records have been dropped.".format(len(result.issues), result.invalid_row_count)
        st.error("Some records need correction. Review outcome choices above, then use Fix flagged records here and Apply corrections and recheck.")
        st.caption("Source row counts the header as row 1. One row may have several different issues.")
        st.dataframe(result.issues, hide_index=True, width="stretch")
        st.download_button(
            "Download issues to fix", csv_bytes(result.issues), "data_quality_issues.csv", "text/csv",
            on_click="ignore",
        )

    from src.partial_analysis import partition_validated
    usable, quarantined, coverage = partition_validated(result, len(raw))
    st.session_state['analysis_coverage'] = coverage
    if not result.is_valid and not strict:
        if usable.empty:
            st.session_state["import_notice"] = "Your file is uploaded, but no rows currently meet the analysis requirements. Approve outcome meanings or correct flagged records in Data setup."
            st.warning(st.session_state["import_notice"])
        else:
            st.warning("Partial analysis is ready: {} of {} rows included; {} unresolved rows excluded. Totals and win rate describe only included rows, not the whole file.".format(len(usable), len(raw), len(quarantined)))
            st.caption("Every row with a blocking issue is quarantined, including both copies of a duplicate ID. Fixing a row brings it back into analysis after revalidation. No values are guessed. Unknown outcomes still need a confirmed meaning.")
            st.caption('Excluded-record downloads contain standardized values; the issue report preserves the original problematic values and source-row references.')
            st.download_button('Download excluded records', csv_bytes(quarantined), 'excluded_records.csv', 'text/csv', on_click='ignore')
    if result.is_valid or (not strict and not usable.empty):
        with st.expander("Review standardized data", expanded=False):
            st.caption(
                "The first 50 rows are shown below. Use Download standardized data for the full dataset. "
                "This contains your mapped fields; extra source columns remain in your original file. "
                "This download contains the included analysis rows, with original source-row numbers and coverage. Unresolved records remain in the issue list."
            )
            st.dataframe(usable.head(50), hide_index=True, width="stretch")
        st.download_button(
            "Download standardized data", csv_bytes(usable), "standardized_pipeline.csv", "text/csv",
            on_click="ignore", type="primary",
        )
        analytics_key = sha256((repr(signature) + repr(st.session_state.get("repairs_" + repair_key, {}))).encode()).hexdigest()[:16]
        return usable, as_of, analytics_key


if __name__ == "__main__":
    main()
