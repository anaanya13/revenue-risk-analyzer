import unittest
from datetime import date
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
from src.column_mapper import suggest_mapping, mapping_errors, mapping_basis
from src.import_profiles import column_profiles, value_candidates


def conversational_export():
    return pd.DataFrame({'Ref #':['EX-01','EX-02','EX-03'], 'Company':['Example A','Example B','Example C'],
        'Rep':['Rep A','Rep B','Rep A'], 'What they want':['Service']*3,
        'Rough value (CAD)':[100,None,300], "Where it's at":['Quote','Live','Quote'],
        "How it's going":['In progress','Signed',None], 'Added on':['2026-01-01']*3,
        'Last spoke':['2026-09-01']*3, 'Follow up by':['2026-10-01','',''],
        'Closed on':['','2026-09-02',''], 'Stuck on':['Price being discussed','',''],
        'How they found us':['Referral']*3, 'Pulled on':['2026-09-29']*3,
        'Swag sent?':['Y','N','N']})


class ConversationalImportTests(unittest.TestCase):
    def test_actual_header_vocabulary_maps_without_export_metadata(self):
        raw=conversational_export();m=suggest_mapping(raw.columns)
        self.assertFalse(mapping_errors(raw.columns,m))
        self.assertEqual(m['deal_id'],'Ref #')
        self.assertEqual(m['deal_value'],'Rough value (CAD)')
        self.assertEqual(m['status'],"How it's going")
        self.assertEqual(m['stage'],"Where it's at")
        self.assertEqual(m['last_activity_date'],'Last spoke')
        self.assertEqual(m['next_contact_date'],'Follow up by')
        self.assertNotIn('Pulled on',m.values());self.assertNotIn('Closed on',m.values())

    def test_word_combinations_preserve_ambiguity_and_date_roles(self):
        self.assertEqual(suggest_mapping(['Estimated deal amount CAD'])['deal_value'],'Estimated deal amount CAD')
        self.assertEqual(suggest_mapping(['Opportunity added date'])['created_date'],'Opportunity added date')
        self.assertIsNone(suggest_mapping(['Last planned contact'])['last_activity_date'])
        self.assertIsNone(suggest_mapping(['Weighted opportunity amount'])['deal_value'])
        self.assertIsNone(suggest_mapping(['Rough value','Estimated deal amount'])['deal_value'])
        m=suggest_mapping(['Deal stage status'])
        self.assertIsNone(m['stage']);self.assertIsNone(m['status'])
        self.assertIn('combination',mapping_basis('Estimated deal amount CAD','deal_value'))

    def test_value_evidence_is_review_only_and_explains_samples(self):
        frame=pd.DataFrame({'A':[100,200,None], 'B':['Open','Signed','Lost'],
                            'C':['2026-01-01']*3, 'D':['2026-09-29']*3})
        profiles=column_profiles(frame)
        self.assertEqual(value_candidates(profiles,'deal_value'),['A'])
        self.assertEqual(value_candidates(profiles,'status'),['B'])
        self.assertEqual(value_candidates(profiles,'created_date'),['C','D'])
        self.assertTrue(all(v is None for v in suggest_mapping(frame.columns).values()))
        self.assertEqual(profiles.loc[0,'Sampled nonblank cells'],2)

    def test_ui_interpretation_analysis_and_restoring_suggestions(self):
        with patch('src.data_loader.load_pipeline',return_value=conversational_export()):
            a=AppTest.from_file('app.py',default_timeout=30).run()
            a.radio[0].set_value('Try sample data').run()
            self.assertIn('6 of 6 core fields recognized', ' '.join(c.value for c in a.caption))
            next(c for c in a.checkbox if c.label=='Use these suggested outcome meanings for this file').check().run()
            a.date_input[0].set_value(date(2026,9,29)).run()
            next(b for b in a.button if b.label=='Check data').click().run()
            self.assertFalse(a.exception)
            self.assertIn('Revenue at risk',[m.label for m in a.tabs[1].metric])
            self.assertTrue(a.tabs[2].get('download_button'))
            self.assertTrue(any('Included with missing details: 2' in w.value for w in a.tabs[1].warning))
            next(s for s in a.selectbox if s.label=='Deal Value *').set_value('Company').run()
            self.assertEqual(next(s for s in a.selectbox if s.label=='Deal Value *').value,'Company')
            next(b for b in a.button if b.label=='Use suggested column matches').click().run()
            self.assertEqual(next(s for s in a.selectbox if s.label=='Deal Value *').value,'Rough value (CAD)')
            self.assertEqual(len(a.tabs[1].metric),0)
            next(b for b in a.button if b.label=='Check data').click().run()
            self.assertFalse(a.exception)
            next(b for b in a.button if b.label=='Run calculation check').click().run()
            self.assertTrue(any('comparisons agree' in s.value for s in a.success))
