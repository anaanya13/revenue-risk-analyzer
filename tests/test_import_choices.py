import unittest
from datetime import date
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
from src.column_mapper import suggest_mapping, mapping_candidates, standardize_columns
from src.import_choices import apply_choices, owner_variant_groups
from src.data_validator import validate_data
from src.followup_engine import followup_analysis
from src.risk_engine import assess_deals

ASOF = date(2026,9,29)


def records():
    return pd.DataFrame({'Opportunity Ref':['A','B','C','D','E'],
        'Expected Contract Amount (CAD)':[100,200,300,400,500],
        'Where Things Stand':['Quote sent']*5,
        'Outcome So Far':['Signed','Not proceeding','In progress','In progress','In progress'],
        'First Entered':['2026-01-01']*5, 'Latest Touchpoint':['2026-09-01']*5,
        'Next Contact':['2027-01-01','2026-01-02','2026-09-28','2026-09-29',''],
        'Account Handler':['Alex Smith','ALEX SMITH','Alex Smith','ALEX SMITH','Alex Smith'],
        'Internal Comments':['ignored']*5})


class ImportTests(unittest.TestCase):
    def mapped(self):
        raw=records()
        return standardize_columns(raw,suggest_mapping(raw.columns))

    def test_transparent_suggestions_and_ambiguity(self):
        mapping=suggest_mapping(records().columns)
        self.assertEqual(mapping['next_contact_date'],'Next Contact')
        self.assertEqual(mapping['deal_value'],'Expected Contract Amount (CAD)')
        self.assertEqual(mapping_candidates(['Amount','Expected Contract Amount (CAD)'],'deal_value'),['Amount','Expected Contract Amount (CAD)'])
        self.assertIsNone(suggest_mapping(['Amount','Expected Contract Amount (CAD)'])['deal_value'])
        self.assertIsNone(suggest_mapping(['Next Contact'])['last_activity_date'])

    def test_no_global_outcome_guess_or_mutation(self):
        frame=self.mapped();before=frame.copy(deep=True)
        self.assertFalse(validate_data(frame,as_of_date=ASOF).is_valid)
        translated=apply_choices(frame,{'Signed':'Won','Not proceeding':'Lost'})
        self.assertTrue(validate_data(translated,as_of_date=ASOF).is_valid)
        alternate=apply_choices(frame,{'Signed':'Open','Not proceeding':'Lost'})
        self.assertEqual(alternate.iloc[0].status,'Open')
        pd.testing.assert_frame_equal(frame,before)
        with self.assertRaises(ValueError):apply_choices(frame,{'Signed':'Maybe'})

    def test_missing_outcome_not_filled(self):
        frame=self.mapped();frame.loc[0,'status']=''
        result=validate_data(apply_choices(frame,{'Signed':'Won','Not proceeding':'Lost'}),as_of_date=ASOF)
        self.assertTrue(any(result.issues.field.eq('status')))

    def test_reviewable_owner_merge(self):
        frame=self.mapped()
        self.assertEqual(owner_variant_groups(frame.sales_rep),[['ALEX SMITH','Alex Smith']])
        self.assertEqual(apply_choices(frame).sales_rep.nunique(),2)
        merged=apply_choices(frame,owners={'ALEX SMITH':'Alex Smith','Alex Smith':'Alex Smith'})
        self.assertEqual(merged.sales_rep.nunique(),1)
        self.assertEqual(len(merged),len(frame))
        self.assertEqual(owner_variant_groups(['Alex Smith','Alex Smyth']),[])

    def test_planned_date_rules_and_date_order(self):
        frame=apply_choices(self.mapped(),{'Signed':'Won','Not proceeding':'Lost'})
        self.assertTrue(validate_data(frame,as_of_date=ASOF).is_valid)
        frame.loc[0,'next_contact_date']='2025-12-31'
        self.assertIn('before the created',validate_data(frame,as_of_date=ASOF).issues.iloc[0].issue)
        frame.loc[0,'next_contact_date']='2026-02-30'
        self.assertFalse(validate_data(frame,as_of_date=ASOF).is_valid)
        frame.loc[0,'next_contact_date']='04/06/2026'
        self.assertEqual(validate_data(frame,True,ASOF).cleaned_data.iloc[0].next_contact_date,pd.Timestamp('2026-06-04'))
        self.assertEqual(validate_data(frame,False,ASOF).cleaned_data.iloc[0].next_contact_date,pd.Timestamp('2026-04-06'))

    def test_followup_scope_boundaries_and_inactivity_independence(self):
        frame=apply_choices(self.mapped(),{'Signed':'Won','Not proceeding':'Lost'})
        clean=validate_data(frame,as_of_date=ASOF).cleaned_data
        assessed=assess_deals(clean,ASOF,30)
        table=followup_analysis(assessed,ASOF)
        self.assertEqual(table.followup_status.tolist(),['Overdue','Due today','Not scheduled'])
        self.assertEqual(table.iloc[0].days_overdue,1)
        self.assertEqual(table.iloc[1].days_overdue,0)
        self.assertTrue(pd.isna(table.iloc[2].days_overdue))
        self.assertFalse(assessed.is_stalled.any())
        self.assertEqual(len(followup_analysis(assessed.loc[assessed.status.eq('Won')],ASOF)),0)
        self.assertIsNone(followup_analysis(assessed.drop(columns='next_contact_date'),ASOF))

    def test_interface_confirmation_changes_invalidate_results(self):
        with patch('src.data_loader.load_pipeline',return_value=records()):
            a=AppTest.from_file('app.py',default_timeout=30).run()
            a.radio[0].set_value('Try sample data').run()
            a.date_input[0].set_value(ASOF).run()
            next(b for b in a.button if b.label=='Check data').click().run()
            self.assertEqual([m.value for m in a.metric],['5','2','2'])
            next(x for x in a.selectbox if x.label=='Outcome: Signed').set_value('Won').run()
            next(x for x in a.selectbox if x.label=='Outcome: Not proceeding').set_value('Lost').run()
            self.assertEqual(len(a.metric),0)
            next(b for b in a.button if b.label=='Check data').click().run()
            self.assertEqual([m.value for m in a.metric][:3],['5','0','0'])
            self.assertIn('Overdue follow-ups',[m.label for m in a.metric])
            merge=next(x for x in a.selectbox if x.label.startswith('Use one name'))
            merge.set_value('Alex Smith').run()
            self.assertEqual(len(a.metric),0)
            next(b for b in a.button if b.label=='Check data').click().run()
            owners=next(x for x in a.multiselect if x.label=='Sales Representative')
            self.assertEqual(owners.options,['Alex Smith'])
            self.assertTrue(any('Internal Comments' in x.value for x in a.markdown))
            self.assertFalse(a.exception)
