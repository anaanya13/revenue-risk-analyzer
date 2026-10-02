"""Fictional records; no uploaded customer data is committed."""
import unittest
from datetime import date
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
from src.column_mapper import draft_mapping, suggest_mapping


def export():
    return pd.DataFrame({
        'Opp ref': ['DEMO-1','DEMO-2','DEMO-3'], 'Client name': ['Example A','Example B','Example C'],
        'Owner (rep)': ['Person A']*3, 'Deal about': ['Service A']*3,
        'Ballpark $ CAD': [100,None,300], "Step we're on": ['Quote','Live','Initial chat'],
        'Verdict so far': ['In progress','Signed',None], 'First logged': ['2026-01-01']*3,
        'Last chat': ['2026-09-01']*3, 'Circle back on': ['2026-10-30','',''],
        'Wrapped up': ['', '2026-09-02',''], "What's holding it up": ['Price being discussed','',''],
        'Heard about us via': ['Referral']*3, 'Quote #': ['Q1','Q2','Q3'],
        'Discount given %': [5,10,15], 'Touches so far': [1,2,0],
        'Sales area': ['West']*3, 'Export run date': ['2026-09-29']*3})


class SemanticMappingTests(unittest.TestCase):
    def test_composed_draft_and_decoys(self):
        m,e=draft_mapping(export())
        expected={'deal_id':'Opp ref','deal_value':'Ballpark $ CAD','created_date':'First logged',
                  'last_activity_date':'Last chat','next_contact_date':'Circle back on',
                  'stage':"Step we're on",'status':'Verdict so far','sales_rep':'Owner (rep)',
                  'product':'Deal about','lead_source':'Heard about us via','follow_ups':'Touches so far',
                  'delay_reason':"What's holding it up",'industry':None}
        self.assertEqual(m,expected)
        self.assertTrue(any('value evidence' in r['Confidence'] for r in e))
        self.assertEqual(m,suggest_mapping(export().columns,frame=export()))

    def test_unseen_combinations_and_camel_case(self):
        f=pd.DataFrame({'OpportunityReferenceCode':['X1','X2','X3'],
            'Approx contract worth CAD':[100,200,300], 'Most recent customer chat':['2026-09-01']*3,
            'Next scheduled conversation':['2026-10-01']*3, 'Current sales milestone':['Quote']*3,
            'Opportunity disposition':['Open']*3, 'Assigned opportunity owner':['Person A']*3})
        m,_=draft_mapping(f)
        for field,column in zip(['deal_id','deal_value','last_activity_date','next_contact_date','stage','status','sales_rep'],f.columns):
            self.assertEqual(m[field],column)

    def test_ties_and_cross_field_collisions_stay_manual(self):
        f=export(); f['Estimated contract worth']=[100,200,300]
        m,e=draft_mapping(f)
        self.assertIsNone(m['deal_value'])
        self.assertTrue(any('Ambiguous' in r['Confidence'] for r in e))
        m,_=draft_mapping(pd.DataFrame({'Deal stage status':['Open']*3}))
        self.assertIsNone(m['stage']);self.assertIsNone(m['status'])

    def test_contents_reject_contradiction_without_losing_missing_rows(self):
        f=export(); f['Ballpark $ CAD']=['nonsense']*3
        m,e=draft_mapping(f);self.assertIsNone(m['deal_value'])
        self.assertTrue(any('conflict' in r['Confidence'] for r in e))
        f['Ballpark $ CAD']=[None,None,None]
        self.assertEqual(draft_mapping(f)[0]['deal_value'],'Ballpark $ CAD')

    def test_values_alone_never_assign_business_date_or_numeric_roles(self):
        f=pd.DataFrame({'A':[100,200,300], 'B':['2026-01-01']*3,
                        'Quote number':['Q1','Q2','Q3'], 'Payment status':['Open']*3,
                        'Discount amount':[10,20,30], 'Export run date':['2026-09-01']*3})
        self.assertTrue(all(v is None for v in draft_mapping(f)[0].values()))

    def test_interface_full_analysis_and_manual_override(self):
        with patch('src.data_loader.load_pipeline',return_value=export()):
            a=AppTest.from_file('app.py',default_timeout=30).run()
            a.radio[0].set_value('Try sample data').run()
            self.assertIn('6 of 6 core fields drafted',' '.join(c.value for c in a.caption))
            self.assertEqual(next(s for s in a.selectbox if s.label=='Deal Value *').value,'Ballpark $ CAD')
            next(c for c in a.checkbox if c.label=='Use these suggested outcome meanings for this file').check().run()
            a.date_input[0].set_value(date(2026,9,29)).run()
            next(b for b in a.button if b.label=='Check data').click().run()
            self.assertFalse(a.exception)
            self.assertIn('Revenue at risk',[m.label for m in a.tabs[1].metric])
            self.assertTrue(a.tabs[2].get('download_button'))
            next(b for b in a.button if b.label=='Run calculation check').click().run()
            self.assertTrue(any('comparisons agree' in s.value for s in a.success))
            next(s for s in a.selectbox if s.label=='Deal Value *').set_value('Discount given %').run()
            a.date_input[0].set_value(date(2026,9,28)).run()
            self.assertEqual(next(s for s in a.selectbox if s.label=='Deal Value *').value,'Discount given %')
            next(b for b in a.button if b.label=='Use suggested column matches').click().run()
            self.assertEqual(next(s for s in a.selectbox if s.label=='Deal Value *').value,'Ballpark $ CAD')
