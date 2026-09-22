"""Hand-calculated examples, rule boundaries, reconciliation and dashboard state."""

from datetime import date
from pathlib import Path
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.bottleneck_engine import summarize_bottlenecks
from src.filters import filter_deals, filter_options
from src.kpi_engine import calculate_kpis
from src.risk_engine import assess_deals, aging_distribution, risk_distribution

AS_OF = date(2026, 9, 21)
ROOT = Path(__file__).resolve().parents[1]


def example():
    rows = []
    for i, inactive in enumerate([0, 14, 15, 29, 30, 60, 90, 90]):
        rows.append({
            "deal_id": str(i + 1).zfill(3), "deal_value": (i + 1) * 100,
            "created_date": pd.Timestamp(AS_OF) - pd.Timedelta(days=inactive + 10),
            "last_activity_date": pd.Timestamp(AS_OF) - pd.Timedelta(days=inactive),
            "stage": "Qualification" if i < 3 else "Proposal",
            "status": "Open" if i < 6 else ("Won" if i == 6 else "Lost"),
            "sales_rep": "Alex" if i % 2 == 0 else None,
            "delay_reason": ["Docs", None, "Docs", "Approval", None, "Approval", None, None][i],
            "follow_ups": [0, None, 2, 4, None, 6, 1, 1][i],
        })
    return pd.DataFrame(rows)


class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.raw = example()
        self.data = assess_deals(self.raw, AS_OF)

    def test_hand_calculated_kpis(self):
        k = calculate_kpis(self.data)
        expected = {"deal_count": 8, "open_deals": 6, "won_deals": 1, "lost_deals": 1,
                    "total_deal_value": 3600, "open_pipeline_value": 2100, "won_deal_value": 700,
                    "lost_deal_value": 800, "average_deal_value": 450, "win_rate": .5,
                    "stalled_deals": 2, "revenue_at_risk": 1100}
        for name, value in expected.items():
            self.assertEqual(k[name], value, name)
        self.assertAlmostEqual(k["revenue_at_risk_share"], 1100 / 2100)
        self.assertAlmostEqual(k["average_open_age"], 208 / 6)
        self.assertAlmostEqual(k["average_inactivity"], 148 / 6)

    def test_severity_and_stalled_boundaries(self):
        self.assertEqual(self.data.risk_severity.tolist(), ["Low", "Low", "Medium", "Medium", "High", "Critical", "Closed", "Closed"])
        self.assertEqual(self.data.is_stalled.tolist(), [False, False, False, False, True, True, False, False])
        self.assertEqual(self.data.days_inactive.iloc[:6].tolist(), [0, 14, 15, 29, 30, 60])
        self.assertTrue(self.data.days_inactive.iloc[6:].isna().all())
        self.assertTrue(self.data.deal_age_days.iloc[6:].isna().all())

    def test_threshold_change_recalculates_exposure(self):
        changed = assess_deals(self.raw, AS_OF, 60)
        self.assertEqual(changed.risk_severity.iloc[4:6].tolist(), ["Medium", "High"])
        self.assertEqual(calculate_kpis(changed)["revenue_at_risk"], 600)
        self.assertEqual(calculate_kpis(assess_deals(self.raw, AS_OF, 61))["revenue_at_risk"], 0)

    def test_odd_and_one_day_thresholds_have_no_overlaps(self):
        for threshold, days, expected in [(3, [0, 1, 2, 3, 5, 6], ["Low", "Low", "Medium", "High", "High", "Critical"]),
                                           (1, [0, 1, 2], ["Low", "High", "Critical"])]:
            frame = self.raw.iloc[:len(days)].copy()
            frame["created_date"] = pd.Timestamp(AS_OF) - pd.Timedelta(days=100)
            frame["last_activity_date"] = [pd.Timestamp(AS_OF) - pd.Timedelta(days=n) for n in days]
            self.assertEqual(assess_deals(frame, AS_OF, threshold).risk_severity.tolist(), expected)

    def test_analysis_date_changes_age_and_exact_threshold(self):
        later = assess_deals(self.raw, date(2026, 9, 22))
        self.assertEqual(later.days_inactive.iloc[3], 30)
        self.assertTrue(later.is_stalled.iloc[3])
        self.assertEqual(calculate_kpis(later)["revenue_at_risk"], 1500)
        self.assertEqual(later.deal_age_days.iloc[0], 11)

    def test_recent_activity_does_not_make_old_deal_stalled(self):
        row = self.raw.iloc[:1].copy()
        row["created_date"] = pd.Timestamp(AS_OF) - pd.Timedelta(days=200)
        result = assess_deals(row, AS_OF)
        self.assertEqual(result.deal_age_days.iloc[0], 200)
        self.assertFalse(result.is_stalled.iloc[0])
        self.assertEqual(result.risk_severity.iloc[0], "Low")

    def test_aging_bucket_boundaries_and_closed_exclusion(self):
        frame = self.raw.copy()
        ages = [0, 30, 31, 60, 61, 90, 91, 100]
        frame["status"] = ["Open"] * 7 + ["Won"]
        frame["created_date"] = [pd.Timestamp(AS_OF) - pd.Timedelta(days=n) for n in ages]
        frame["last_activity_date"] = pd.Timestamp(AS_OF)
        data = assess_deals(frame, AS_OF)
        self.assertEqual(aging_distribution(data).deals.tolist(), [2, 2, 2, 1])
        self.assertEqual(data.age_bucket.iloc[6], "91+ days")
        self.assertTrue(pd.isna(data.age_bucket.iloc[7]))

    def test_distributions_reconcile_to_open_population(self):
        for summary in (risk_distribution(self.data), aging_distribution(self.data)):
            self.assertEqual(summary.deals.sum(), 6)
            self.assertEqual(summary.deal_value.sum(), 2100)
        self.assertEqual(risk_distribution(self.data).deals.tolist(), [2, 2, 1, 1])

    def test_open_only_and_closed_only_undefined_metrics(self):
        opened = calculate_kpis(filter_deals(self.data, {"status": ["Open"]}))
        self.assertIsNone(opened["win_rate"])
        closed = calculate_kpis(filter_deals(self.data, {"status": ["Won", "Lost"]}))
        self.assertEqual(closed["win_rate"], .5)
        self.assertEqual(closed["revenue_at_risk"], 0)
        self.assertIsNone(closed["average_open_age"])
        self.assertIsNone(closed["average_inactivity"])
        self.assertIsNone(closed["revenue_at_risk_share"])

    def test_zero_value_is_different_from_missing(self):
        frame = self.raw.iloc[4:6].copy()
        frame["deal_value"] = 0
        k = calculate_kpis(assess_deals(frame, AS_OF))
        self.assertEqual(k["stalled_deals"], 2)
        self.assertEqual(k["average_deal_value"], 0)
        self.assertEqual(k["revenue_at_risk"], 0)
        self.assertIsNone(k["revenue_at_risk_share"])

    def test_empty_filter_keeps_zero_counts_and_undefined_rates(self):
        empty = filter_deals(self.data, {"status": []})
        k = calculate_kpis(empty)
        self.assertEqual(k["deal_count"], 0)
        self.assertEqual(k["open_pipeline_value"], 0)
        self.assertIsNone(k["win_rate"])
        self.assertIsNone(k["average_deal_value"])
        self.assertTrue(summarize_bottlenecks(empty).empty)
        self.assertEqual(risk_distribution(empty).deals.sum(), 0)
        self.assertEqual(aging_distribution(empty).deals.sum(), 0)

    def test_stage_reconciliation_and_followup_coverage(self):
        stages = summarize_bottlenecks(self.data)
        self.assertEqual(stages.stage.tolist(), ["Proposal", "Qualification"])
        self.assertEqual(stages.open_deals.tolist(), [3, 3])
        self.assertEqual(stages.stalled_deals.tolist(), [2, 0])
        self.assertEqual(stages.revenue_at_risk.tolist(), [1100, 0])
        self.assertAlmostEqual(stages.iloc[0].stalled_share, 2 / 3)
        self.assertEqual(stages.follow_ups_recorded.tolist(), [2, 2])
        self.assertEqual(stages.average_follow_ups.tolist(), [5, 1])
        self.assertAlmostEqual(stages.iloc[0].average_open_age, 149 / 3)
        self.assertAlmostEqual(stages.iloc[0].average_inactivity, 119 / 3)
        self.assertEqual(stages.open_value.sum(), 2100)

    def test_optional_grouping_retains_missing_labels(self):
        for field in ("sales_rep", "delay_reason"):
            summary = summarize_bottlenecks(self.data, field)
            self.assertEqual(summary.open_deals.sum(), 6)
            self.assertEqual(summary.revenue_at_risk.sum(), 1100)
            self.assertEqual(summary[field].isna().sum(), 1)
        minimal = self.data.drop(columns=["sales_rep", "delay_reason", "follow_ups"])
        self.assertIsNone(summarize_bottlenecks(minimal, "sales_rep"))
        self.assertIsNone(summarize_bottlenecks(minimal, "delay_reason"))
        self.assertTrue(summarize_bottlenecks(minimal).average_follow_ups.isna().all())

    def test_missing_group_does_not_merge_with_literal_label(self):
        frame = self.raw.copy()
        frame.loc[0, "delay_reason"] = "Not recorded (blank)"
        groups = summarize_bottlenecks(assess_deals(frame, AS_OF), "delay_reason")
        self.assertEqual(groups.delay_reason.isna().sum(), 1)
        self.assertEqual(groups.delay_reason.eq("Not recorded (blank)").sum(), 1)

    def test_filters_intersect_include_blanks_and_preserve_input(self):
        before = self.data.copy(deep=True)
        self.assertEqual(filter_options(self.data, "sales_rep"), ["Alex", None])
        chosen = filter_deals(self.data, {"status": ["Open"], "sales_rep": [None], "stage": ["Proposal"]})
        self.assertEqual(chosen.deal_id.tolist(), ["004", "006"])
        self.assertEqual(calculate_kpis(chosen)["revenue_at_risk"], 600)
        pd.testing.assert_frame_equal(before, self.data)

    def test_created_date_filter_is_inclusive_and_not_activity_date(self):
        exact = self.data.created_date.iloc[4]
        chosen = filter_deals(self.data, created_from=exact, created_to=exact)
        self.assertEqual(chosen.deal_id.tolist(), ["005"])
        self.assertTrue(filter_deals(self.data, created_from=date(2027, 1, 1)).empty)
        with self.assertRaises(ValueError):
            filter_deals(self.data, created_from=AS_OF, created_to=date(2020, 1, 1))

    def test_analysis_preserves_source_and_exports_provenance(self):
        before = self.raw.copy(deep=True)
        assessed = assess_deals(self.raw, AS_OF, 45)
        pd.testing.assert_frame_equal(before, self.raw)
        self.assertEqual(len(assessed), len(self.raw))
        self.assertTrue(assessed.analysis_date.eq(pd.Timestamp(AS_OF)).all())
        self.assertTrue(assessed.stalled_threshold_days.eq(45).all())

    def test_invalid_settings_and_data_cannot_be_analyzed(self):
        for invalid in (0, -1, 1.5, True, "30"):
            with self.subTest(threshold=invalid), self.assertRaises(ValueError):
                assess_deals(self.raw, AS_OF, invalid)
        for invalid_date in (None, "bad", 45000):
            with self.subTest(date=invalid_date), self.assertRaises(ValueError):
                assess_deals(self.raw, invalid_date)
        with self.assertRaises(ValueError):
            assess_deals(self.raw.drop(columns="status"), AS_OF)
        for column, value in (("deal_value", -1), ("status", "Maybe"), ("last_activity_date", "2099-01-01")):
            bad = self.raw.copy()
            bad.loc[0, column] = value
            with self.assertRaises(ValueError):
                assess_deals(bad, AS_OF)
        duplicate = pd.concat([self.raw, self.raw.iloc[:1]], ignore_index=True)
        with self.assertRaises(ValueError):
            assess_deals(duplicate, AS_OF)


class AnalyticsInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.app.radio[0].set_value("Try sample data").run()
        self.app.date_input[0].set_value(AS_OF).run()
        self.app.button[0].click().run()
        self.assertEqual(len(self.app.exception), 0)

    def metric(self, name):
        return next(m.value for m in self.app.metric if m.label == name)

    def select(self, name, values):
        next(w for w in self.app.multiselect if w.label == name).set_value(values).run()
        self.assertEqual(len(self.app.exception), 0)

    def test_sample_has_pipeline_cards_and_charts(self):
        self.assertEqual(self.metric("Matching deals"), "120")
        self.assertEqual(self.metric("Open deals"), "70")
        self.assertEqual(self.metric("Won deals"), "27")
        self.assertEqual(self.metric("Lost deals"), "23")
        self.assertEqual(self.metric("Win rate"), "54.0%")
        self.assertEqual(len(self.app.get("plotly_chart")), 3)
        labels = [b.label for b in self.app.get("download_button")]
        self.assertIn("Download filtered analysis", labels)
        self.assertIn("Download standardized data", labels)

    def test_closed_only_empty_and_reset_filters(self):
        self.select("Status", ["Won"])
        self.assertEqual(self.metric("Matching deals"), "27")
        self.assertEqual(self.metric("Win rate"), "100.0%")
        self.assertEqual(self.metric("Revenue at risk"), "0.00")
        self.assertEqual(self.metric("Average open age (days)"), "N/A")
        self.select("Status", [])
        self.assertTrue(any("No deals match" in info.value for info in self.app.info))
        self.assertEqual(len(self.app.metric), 3)  # Validation remains visible.
        next(b for b in self.app.button if b.label == "Reset filters").click().run()
        self.assertEqual(self.metric("Matching deals"), "120")

    def test_threshold_recomputes_and_date_change_requires_validation(self):
        initial = float(self.metric("Revenue at risk").replace(",", ""))
        self.app.number_input[0].set_value(3650).run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.metric("Revenue at risk"), "0.00")
        self.assertGreater(initial, 0)
        self.assertEqual(self.metric("Matching deals"), "120")
        self.app.date_input[0].set_value(date(2026, 9, 22)).run()
        self.assertEqual(len(self.app.metric), 0)
        self.app.button[0].click().run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.metric("Matching deals"), "120")

    def test_alternate_file_missing_optional_fields_and_invalid_file(self):
        self.app.radio[0].set_value("Try alternate column names").run()
        self.app.button[0].click().run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(self.metric("Matching deals"), "12")
        self.assertTrue(any("Map Delay Reason" in info.value for info in self.app.info))
        self.app.radio[0].set_value("Try messy test data").run()
        self.app.button[0].click().run()
        self.assertEqual(len(self.app.number_input), 0)
        self.assertEqual(len(self.app.multiselect), 0)
        self.assertEqual(len(self.app.get("plotly_chart")), 0)

    def test_date_filter_excludes_every_deal_without_crashing(self):
        next(w for w in self.app.checkbox if w.label == "Filter by created date").check().run()
        self.app.date_input[1].set_value(date(2027, 1, 1)).run()
        self.assertTrue(any("start must" in w.value for w in self.app.warning))
        self.app.date_input[2].set_value(date(2027, 2, 1)).run()
        self.assertTrue(any("No deals match" in w.value for w in self.app.info))
        self.assertEqual(len(self.app.exception), 0)


if __name__ == "__main__":
    unittest.main()
