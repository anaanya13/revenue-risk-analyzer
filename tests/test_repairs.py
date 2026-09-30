import unittest
from unittest.mock import patch
from datetime import date
import pandas as pd
from streamlit.testing.v1 import AppTest
from src.repair_view import apply_repairs
from src.import_choices import suggest_outcome
from src.data_cleaner import normalize_status
from src.data_validator import validate_data
from test_import_choices import records


class RepairTests(unittest.TestCase):
    def test_suggestions_are_not_global_rules(self):
        self.assertEqual(suggest_outcome('  SIGNED '),'Won')
        self.assertEqual(suggest_outcome('Not proceeding'),'Lost')
        self.assertEqual(normalize_status('Signed'),'Signed')
        self.assertIsNone(suggest_outcome('Maybe later'))

    def test_corrections_are_bounded_and_nonmutating(self):
        frame=pd.DataFrame({'deal_id':['A','A'],'deal_value':[10,None]})
        fixed=apply_repairs(frame,{1:{'deal_id':'B','deal_value':'25'}})
        self.assertEqual(fixed.iloc[1].deal_id,'B')
        self.assertEqual(frame.iloc[1].deal_id,'A')
        self.assertTrue(pd.isna(frame.iloc[1].deal_value))
        for patches in [{4:{'deal_id':'X'}},{0:{'not_a_field':'X'}}]:
            with self.assertRaises(ValueError):apply_repairs(frame,patches)

    def test_uploaded_blocked_and_synonym_approval(self):
        with patch('src.data_loader.load_pipeline',return_value=records()):
            app=AppTest.from_file('app.py',default_timeout=30).run()
            app.radio[0].set_value('Try sample data').run()
            app.date_input[0].set_value(date(2026,9,29)).run()
            self.assertTrue(any('File uploaded' in x.value for x in app.success))
            next(b for b in app.button if b.label=='Check data').click().run()
            self.assertTrue(any('analysis is blocked by 2 issues' in x.value for x in app.tabs[1].info))
            next(c for c in app.checkbox if c.label=='Use these suggested outcome meanings for this file').check().run()
            next(b for b in app.button if b.label=='Check data').click().run()
            self.assertTrue(any('Ready for analysis' in x.value for x in app.success))
            self.assertIn('Revenue at risk',[x.label for x in app.tabs[1].metric])
            self.assertFalse(app.exception)

    def test_repaired_values_revalidate_before_unlock(self):
        raw=records();raw.loc[0,'Expected Contract Amount (CAD)']=''
        with patch('src.data_loader.load_pipeline',return_value=raw):
            app=AppTest.from_file('app.py',default_timeout=30).run()
            app.radio[0].set_value('Try sample data').run()
            app.date_input[0].set_value(date(2026,9,29)).run()
            next(c for c in app.checkbox if c.label=='Use these suggested outcome meanings for this file').check().run()
            next(b for b in app.button if b.label=='Check data').click().run()
            self.assertEqual(len(app.tabs[1].metric),0)
            # Drive the editor's documented session delta because AppTest has no editor mutation API.
            editor_key=next(k for k in app.session_state.filtered_state if k.startswith('repair_editor_'))
            app.session_state[editor_key]={'edited_rows':{0:{'deal_value':'100'}},'added_rows':[],'deleted_rows':[]}
            next(b for b in app.button if b.label=='Apply corrections and recheck').click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any('Ready for analysis' in x.value for x in app.success))
            next(b for b in app.button if b.label=='Discard these corrections').click().run()
            self.assertEqual(len(app.tabs[1].metric),0)
