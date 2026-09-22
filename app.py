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

ROOT = Path(__file__).resolve().parent
DEMO_FILES = {
    "Try sample data": ROOT / "data/sample/revenue_risk_sample_data.xlsx",
    "Try messy test data": ROOT / "data/test/messy_pipeline_data.csv",
    "Try alternate column names": ROOT / "data/test/alternate_company_data.csv",
}


def main():
    st.set_page_config(page_title="Revenue Risk Analyzer", page_icon="📊", layout="wide")
    st.title("Revenue Risk & Deal Bottleneck Analyzer")
    st.write("Check your sales pipeline, identify stalled deals and explore revenue exposure.")
    st.caption("Upload → match columns → check quality → explore your dashboard.")
    with st.expander("Start here: quick guide and project notes"):
        st.markdown(
            "1. Choose **Try sample data** below, keep the Deals worksheet and suggested column matches.\n"
            "2. Click **Check data**, then scroll to **Explore your pipeline**.\n"
            "3. Review the KPIs and **Suggested next steps**. Change the stalled threshold or filters to explore.\n"
            "4. Download the action plan. Under **Check these calculations**, run the independent check.\n\n"
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
    st.success("{} loaded: {:,} rows and {} columns.".format(filename, len(raw), len(raw.columns)))
    with st.expander("Preview original data", expanded=True):
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

    errors = mapping_errors(raw.columns, mapping)
    for error in errors:
        st.warning(error)

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
        "Known Open, Won and Lost status variations are standardized. Unknown statuses need correction."
    )
    signature = (source_key, tuple(mapping.items()), date_order, str(as_of))
    if as_of is None:
        st.warning("Choose a validation date before checking the file.")
    if st.button("Check data", type="primary", disabled=bool(errors) or as_of is None):
        st.session_state["checked_signature"] = signature
    if errors or as_of is None or st.session_state.get("checked_signature") != signature:
        return

    mapped = standardize_columns(raw, mapping)
    result = validate_data(mapped, day_first=date_order.startswith("Day"), as_of_date=as_of)
    st.divider()
    st.subheader("Your data-quality results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Deals checked", len(raw))
    col2.metric("Rows needing attention", result.invalid_row_count)
    col3.metric("Issues found", len(result.issues))
    if result.is_valid:
        st.success("Your data passed all current checks. Your dashboard is ready below.")
    else:
        st.error("Some records need correction. Fix the listed issues in your source file, then upload it again.")
        st.caption("Source row counts the header as row 1. One row may have several different issues.")
        st.dataframe(result.issues, hide_index=True, width="stretch")
        st.download_button(
            "Download issues to fix", csv_bytes(result.issues), "data_quality_issues.csv", "text/csv",
            on_click="ignore",
        )

    if result.is_valid:
        with st.expander("Review standardized data", expanded=False):
            st.caption(
                "The first 50 rows are shown below. Use Download standardized data for the full dataset. "
                "This contains your mapped fields; extra source columns remain in your original file. "
                "No deal rows are removed."
            )
            st.dataframe(result.cleaned_data.head(50), hide_index=True, width="stretch")
        st.download_button(
            "Download standardized data", csv_bytes(result.cleaned_data), "standardized_pipeline.csv", "text/csv",
            on_click="ignore", type="primary",
        )
        analytics_key = sha256(repr(signature).encode()).hexdigest()[:16]
        render_dashboard(result.cleaned_data, as_of, analytics_key)


if __name__ == "__main__":
    main()
