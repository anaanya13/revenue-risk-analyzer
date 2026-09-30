import unittest
from unittest.mock import patch
from datetime import date
from streamlit.testing.v1 import AppTest
from src.data_validator import validate_data
from src.column_mapper import standardize_columns,suggest_mapping
from src.import_choices import apply_choices
from src.partial_analysis import partition_validated
from src.risk_engine import assess_deals
from src.kpi_engine import calculate_kpis
from test_import_choices import records


class PartialTests(unittest.TestCase):
    def test_quarantine_duplicates_and_reconcile(self):
        raw=records();raw.loc[1,'Opportunity Ref']='A';raw.loc[2,'Expected Contract Amount (CAD)']='bad'
        mapped=apply_choices(standardize_columns(raw,suggest_mapping(raw.columns)),{'Signed':'Won','Not proceeding':'Lost'})
        result=validate_data(mapped,as_of_date=date(2026,9,29))
        included,excluded,coverage=partition_validated(result,5)
        self.assertEqual(included.source_row.tolist(),[5,6])
        self.assertEqual(excluded.source_row.tolist(),[2,3,4])
        self.assertIn('Duplicate deal ID', excluded.iloc[0].exclusion_reason)
        self.assertIn('bad', excluded.iloc[2].original_flagged_values)
        self.assertEqual(coverage['included_rows']+coverage['excluded_rows'],5)
        self.assertEqual(calculate_kpis(assess_deals(included,date(2026,9,29)))['open_pipeline_value'],900)

    def test_all_bad_and_all_good(self):
        raw=records();mapped=standardize_columns(raw,suggest_mapping(raw.columns))
        mapped['deal_value']='bad'
        result=validate_data(mapped,as_of_date=date(2026,9,29))
        included,excluded,coverage=partition_validated(result,5)
        self.assertTrue(included.empty);self.assertEqual(len(excluded),5)
        mapped=apply_choices(standardize_columns(raw,suggest_mapping(raw.columns)),{'Signed':'Won','Not proceeding':'Lost'})
        included,excluded,coverage=partition_validated(validate_data(mapped,as_of_date=date(2026,9,29)),5)
        self.assertTrue(excluded.empty);self.assertEqual(coverage['analysis_scope'],'Complete validated file')

    def test_ui_default_partial_and_opt_in_strict(self):
        with patch('src.data_loader.load_pipeline',return_value=records()):
            a=AppTest.from_file('app.py',default_timeout=30).run()
            a.radio[0].set_value('Try sample data').run()
            a.date_input[0].set_value(date(2026,9,29)).run()
            next(b for b in a.button if b.label=='Check data').click().run()
            self.assertIn('Revenue at risk',[m.label for m in a.tabs[1].metric])
            for index in [1,2,3,4]:
                self.assertTrue(any('3 of 5' in x.value for x in a.tabs[index].warning))
                self.assertTrue(any('Reason excluded' in d.value.columns for d in a.tabs[index].dataframe))
            self.assertIn('Download excluded records',[b.label for b in a.get('download_button')])
            next(c for c in a.checkbox if c.label=='Require every row to pass before analysis').check().run()
            next(b for b in a.button if b.label=='Check data').click().run()
            self.assertEqual(len(a.tabs[1].metric),0)
            next(c for c in a.checkbox if c.label=='Use these suggested outcome meanings for this file').check().run()
            next(b for b in a.button if b.label=='Check data').click().run()
            self.assertIn('Revenue at risk',[m.label for m in a.tabs[1].metric])
            self.assertFalse(any('PARTIAL ANALYSIS' in x.value for x in a.tabs[1].warning))
            self.assertFalse(a.exception)
