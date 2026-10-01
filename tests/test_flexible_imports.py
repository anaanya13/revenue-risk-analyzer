import unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
from src.column_mapper import suggest_mapping, mapping_candidates, suggested_alternatives, standardize_columns, mapping_errors
from src.import_choices import apply_choices, suggest_outcome, suggest_delay
from src.data_cleaner import normalize_status
from src.data_loader import load_pipeline, DataLoadError
from src.data_validator import validate_data
from src.partial_analysis import partition_validated
from src.risk_engine import assess_deals
from src.sql_engine import compare_analysis
from src.kpi_engine import calculate_kpis

class FlexibleImportTests(unittest.TestCase):
    def test_business_aliases_currency_and_planned_date_separation(self):
        fields = ['CRM ID','Contract Value (GBP)','Created on','Most recent contact','Funnel stage','Win / Loss','Next outreach date','Assigned to','Bottleneck']
        mapping = suggest_mapping(fields)
        self.assertFalse(mapping_errors(fields, mapping))
        self.assertEqual(mapping['deal_value'], 'Contract Value (GBP)')
        self.assertEqual(mapping['last_activity_date'], 'Most recent contact')
        self.assertEqual(mapping['next_contact_date'], 'Next outreach date')
        self.assertIsNone(suggest_mapping(['Next outreach date'])['last_activity_date'])
        self.assertIsNone(suggest_mapping(['Contract Value (GBP)','Estimated Revenue'])['deal_value'])

    def test_typo_suggestions_are_review_only(self):
        self.assertIsNone(suggest_mapping(['Opportunty amount'])['deal_value'])
        self.assertEqual(suggested_alternatives(['Opportunty amount','Client name'], 'deal_value')[0][0], 'Opportunty amount')
        self.assertEqual(suggested_alternatives(['Notes'], 'created_date'), [])

    def test_absent_columns_require_explicit_choice_and_minimum_pipeline(self):
        raw = pd.DataFrame({'CRM ID':['001','002'], 'Contract value':[100,200]})
        mapping = suggest_mapping(raw.columns)
        self.assertTrue(mapping_errors(raw.columns, mapping))
        self.assertFalse(mapping_errors(raw.columns, mapping, allow_absent=True))
        data = standardize_columns(raw,mapping,allow_absent=True)
        usable, excluded, coverage = partition_validated(validate_data(data,as_of_date=date(2026,9,29)),2)
        self.assertTrue(excluded.empty)
        assessed=assess_deals(usable,date(2026,9,29),allow_missing=True)
        self.assertEqual(calculate_kpis(assessed)['total_deal_value'],300)
        self.assertIsNone(calculate_kpis(assessed)['win_rate'])
        self.assertTrue(compare_analysis(assessed,date(2026,9,29),30).matches.all())
        self.assertTrue(mapping_errors(['Notes'],{},allow_absent=True))

    def test_category_choices_are_explicit_and_do_not_change_outcomes(self):
        raw=pd.DataFrame({'stage':['Quote','Quotation'],'delay_reason':['Docs','Paperwork'],'status':['Open','Open']})
        result=apply_choices(raw,categories={'stage':{'Quotation':'Quote'},'delay_reason':{'Paperwork':'Docs'}})
        self.assertEqual(result.stage.nunique(),1)
        self.assertEqual(result.delay_reason.nunique(),1)
        self.assertEqual(raw.stage.nunique(),2)
        self.assertEqual(result.status.tolist(),raw.status.tolist())
        self.assertEqual(suggest_outcome('Customer declined'),'Lost')
        self.assertEqual(suggest_delay('Price being discussed'), 'Pricing / Terms')
        self.assertIsNone(suggest_delay('unrecognized business reason'))
        self.assertEqual(normalize_status('Customer declined'),'Customer declined')
        with self.assertRaises(ValueError): apply_choices(raw,categories={'status':{'Open':'Lost'}})

    def test_csv_separators_and_quoted_values_preserve_ids(self):
        for separator in [',',';','\t','|']:
            content=('CRM ID'+separator+'Contract value\n0001'+separator+'"1,200"\n').encode()
            raw=load_pipeline(content,'pipeline.csv')
            self.assertEqual(raw.iloc[0].tolist(),['0001','1,200'])
        with self.assertRaises(DataLoadError):load_pipeline(b'id;amount\n1;2;3\n','bad.csv')

    def test_interface_absent_columns_and_manual_choice_persistence(self):
        raw=pd.DataFrame({'CRM ID':['001','002'],'Contract value':[100,200],'Funnel stage':['Quote','Quotation']})
        with patch('src.data_loader.load_pipeline',return_value=raw):
            a=AppTest.from_file('app.py',default_timeout=30).run()
            a.radio[0].set_value('Try sample data').run()
            self.assertTrue(next(b for b in a.button if b.label=='Check data').disabled)
            next(c for c in a.checkbox if c.label.startswith('My file does not contain')).check().run()
            next(m for m in a.multiselect if m.label=='Labels to combine: Current Stage').set_value(['Quote','Quotation']).run()
            next(s for s in a.selectbox if s.label=='Use this label: Current Stage').set_value('Quote').run()
            next(b for b in a.button if b.label=='Check data').click().run()
            self.assertFalse(a.exception)
            self.assertTrue(any('Included with missing details' in w.value for w in a.warning))
            next(s for s in a.selectbox if s.label=='Deal Value *').set_value('CRM ID').run()
            self.assertEqual(next(s for s in a.selectbox if s.label=='Deal Value *').value, 'CRM ID')
            self.assertEqual(len(a.tabs[1].metric),0)

    def test_saved_business_export_keeps_six_rows_with_explicit_meanings(self):
        path=Path(__file__).resolve().parents[1] / 'data/test/flexible_business_export.csv'
        raw=load_pipeline(path.read_bytes(),path.name)
        mapped=standardize_columns(raw,suggest_mapping(raw.columns))
        mapped=apply_choices(mapped,{'Awaiting decision':'Open','Converted':'Won','Closed - Lost':'Lost'})
        usable, excluded, coverage=partition_validated(validate_data(mapped,as_of_date=date(2026,9,29)),len(raw))
        assessed=assess_deals(usable,date(2026,9,29),allow_missing=True)
        self.assertTrue(excluded.empty)
        self.assertEqual(calculate_kpis(assessed)['deal_count'],6)
        self.assertEqual(calculate_kpis(assessed)['total_deal_value'],30000)
        self.assertEqual(calculate_kpis(assessed)['win_rate'],0.5)
        self.assertEqual(assessed.loc[assessed.deal_id.eq('TEST-005'),'risk_severity'].item(),'Unknown')
        self.assertTrue(compare_analysis(assessed,date(2026,9,29),30).matches.all())
