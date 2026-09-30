import unittest
from datetime import date
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
from src.data_validator import validate_data
from src.partial_analysis import partition_validated
from src.risk_engine import assess_deals, risk_distribution, aging_distribution
from src.kpi_engine import calculate_kpis
from src.sql_engine import compare_analysis
from src.ai_assistant import build_context
from src.insight_engine import generate_insights
from src.missing_values import missing_coverage

ASOF = date(2026, 9, 29)


def incomplete():
    return pd.DataFrame(dict(deal_id=['A', 'B', 'C', 'D', None],
        deal_value=[None, 200, 300, 0, 500], status=['Open', 'Won', None, 'Open', 'Open'],
        created_date=['2026-01-01', None, '2026-01-01', None, '2026-01-01'],
        last_activity_date=['2026-01-02', None, '2026-09-01', None, '2026-09-01'],
        stage=['Quote', 'Activated', 'Quote', None, 'Quote']))


def prepare(raw):
    usable, excluded, coverage = partition_validated(validate_data(raw, as_of_date=ASOF), len(raw))
    return assess_deals(usable, ASOF, allow_missing=True), excluded, coverage


class MissingValueTests(unittest.TestCase):
    def test_missing_fields_keep_records_and_known_calculations(self):
        raw = incomplete(); original = raw.copy(deep=True)
        data, excluded, coverage = prepare(raw)
        self.assertTrue(excluded.empty)
        self.assertEqual(coverage['incomplete_rows'], 5)
        k = calculate_kpis(data)
        self.assertEqual(k['deal_count'], 5)
        self.assertEqual(k['open_deals'], 3)
        self.assertEqual(k['won_deals'], 1)
        self.assertEqual(k['win_rate'], 1)
        self.assertEqual(k['average_deal_value'], 250)  # 1000 / 4 recorded, including zero
        self.assertEqual(k['open_pipeline_value'], 500)
        self.assertEqual(k['stalled_deals'], 1)  # missing amount does not remove stalled count
        self.assertEqual(k['revenue_at_risk'], 0)  # known-amount subtotal; coverage exposes missing amount
        self.assertEqual(data.risk_severity.tolist(), ['Critical','Closed','Unknown','Unknown','Medium'])
        self.assertEqual(data.loc[3, 'age_bucket'], 'Unknown')
        self.assertEqual(risk_distribution(data).deals.sum(), 3)
        self.assertEqual(aging_distribution(data).deals.sum(), 3)
        self.assertTrue(compare_analysis(data, ASOF, 30).matches.all())
        self.assertEqual(build_context(data, ASOF, 30)['field_coverage']['missing_amounts'], 1)
        pd.testing.assert_frame_equal(raw, original)

    def test_invalid_values_still_quarantined_and_strict_remains_available(self):
        raw = incomplete(); raw.loc[1, 'deal_value'] = -5
        raw.loc[2, 'deal_id'] = 'A'
        data, excluded, coverage = prepare(raw)
        self.assertEqual(excluded.source_row.tolist(), [2, 3, 4])
        self.assertEqual(len(data), 2)
        with self.assertRaises(ValueError):
            assess_deals(incomplete(), ASOF)
        self.assertFalse(validate_data(incomplete(), as_of_date=ASOF).is_valid)
        self.assertTrue(validate_data(incomplete(), as_of_date=ASOF, allow_missing=True).is_valid)

    def test_all_missing_amounts_and_dates_are_unknown_not_low(self):
        raw = incomplete(); raw['deal_value'] = None; raw['created_date'] = None; raw['last_activity_date'] = None
        data, _, _ = prepare(raw)
        self.assertIsNone(calculate_kpis(data)['average_deal_value'])
        self.assertIsNone(calculate_kpis(data)['average_open_age'])
        self.assertEqual(missing_coverage(data)['missing_amounts'], 5)
        self.assertTrue(compare_analysis(data, ASOF, 30).matches.all())
        self.assertIn('missing activity dates', generate_insights(data).evidence.str.lower().str.cat())

    def test_reupload_filled_values_updates_metrics(self):
        raw = incomplete(); before, _, _ = prepare(raw)
        raw.loc[0, 'deal_value'] = 900
        after, _, _ = prepare(raw)
        self.assertEqual(len(before), len(after))
        self.assertEqual(calculate_kpis(after)['revenue_at_risk'], 900)
        self.assertEqual(missing_coverage(after)['missing_amounts'], 0)

    def test_ui_keeps_missing_rows_and_date_filter_handles_all_blank(self):
        raw = incomplete(); raw['created_date'] = None
        with patch('src.data_loader.load_pipeline', return_value=raw):
            a = AppTest.from_file('app.py', default_timeout=30).run()
            a.radio[0].set_value('Try sample data').run()
            a.date_input[0].set_value(ASOF).run()
            next(b for b in a.button if b.label == 'Check data').click().run()
            self.assertFalse(a.exception)
            for tab in a.tabs[1:5]:
                self.assertTrue(any('Included with missing details' in w.value for w in tab.warning))
            next(b for b in a.button if b.label == 'Run calculation check').click().run()
            self.assertTrue(any('comparisons agree' in s.value for s in a.success))
            next(c for c in a.checkbox if c.label == 'Filter by created date').check().run()
            self.assertFalse(a.exception)
            self.assertIn('0 of 5 included deals', ' '.join(c.value for c in a.caption))
