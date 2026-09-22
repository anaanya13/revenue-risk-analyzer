"""Evidence rules, independent SQL parity, and end-to-end action/check controls."""

from datetime import date
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.filters import filter_deals
from src.insight_engine import generate_insights
from src.risk_engine import assess_deals
from src.sql_engine import compare_analysis, sql_analysis
from test_analytics import example, AS_OF

ROOT = Path(__file__).resolve().parents[1]


class InsightTests(unittest.TestCase):
    def setUp(self):
        self.data = assess_deals(example(), AS_OF)

    def test_actions_reconcile_to_exact_evidence_rows(self):
        plan = generate_insights(self.data).set_index("rule")
        self.assertEqual(plan.index.tolist(), ["critical", "stage_exposure", "missing_owner", "missing_reason", "medium"])
        for rule, ids, value in (("critical", ["006"], 600), ("stage_exposure", ["005", "006"], 1100),
                                  ("missing_owner", ["006"], 600), ("missing_reason", ["005"], 500),
                                  ("medium", ["003", "004"], 700)):
            self.assertEqual(json.loads(plan.at[rule, "deal_ids"]), ids)
            self.assertEqual(plan.at[rule, "deal_count"], len(ids))
            self.assertEqual(plan.at[rule, "deal_value"], value)
        self.assertIn("not included", plan.at["medium", "evidence"])

    def test_no_stalled_and_no_open_are_distinct(self):
        recent = generate_insights(assess_deals(example(), AS_OF, 1000))
        self.assertEqual(recent.rule.tolist(), ["no_stalled"])
        self.assertEqual(recent.deal_count.tolist(), [6])
        closed = generate_insights(filter_deals(self.data, {"status": ["Won", "Lost"]}))
        self.assertEqual(closed.rule.tolist(), ["no_open"])
        self.assertEqual(closed.deal_value.tolist(), [0])
        self.assertTrue(generate_insights(self.data.iloc[:0]).empty)

    def test_unmapped_optional_fields_do_not_claim_source_is_blank(self):
        minimal = self.data.drop(columns=["sales_rep", "delay_reason"])
        plan = generate_insights(minimal).set_index("rule")
        for rule in ("missing_owner", "missing_reason"):
            self.assertEqual(plan.at[rule, "deal_count"], 2)
            self.assertIn("not mapped", plan.at[rule, "evidence"])
        self.assertIn("no value recorded", generate_insights(self.data).set_index("rule").at["missing_owner", "evidence"])

    def test_tied_stages_and_zero_values_keep_all_matching_deals(self):
        frame = example().iloc[4:6].copy()
        frame["stage"] = ["B", "A"]
        frame["deal_value"] = 0
        plan = generate_insights(assess_deals(frame, AS_OF)).set_index("rule")
        self.assertIn("A, B", plan.at["stage_exposure", "evidence"])
        self.assertEqual(plan.at["stage_exposure", "deal_count"], 2)
        self.assertEqual(plan.at["stage_exposure", "deal_value"], 0)

    def test_filter_and_threshold_changes_rebuild_evidence(self):
        one = filter_deals(self.data, {"sales_rep": ["Alex"], "risk_severity": ["High"]})
        plan = generate_insights(one)
        self.assertNotIn("critical", plan.rule.tolist())
        self.assertTrue(plan.deal_ids.eq('["005"]').all())
        changed = generate_insights(assess_deals(example(), AS_OF, 61))
        self.assertNotIn("stage_exposure", changed.rule.tolist())

    def test_source_unchanged_and_order_is_deterministic(self):
        before = self.data.copy(deep=True)
        expected = generate_insights(self.data)
        pd.testing.assert_frame_equal(expected, generate_insights(self.data.sample(frac=1, random_state=7)))
        pd.testing.assert_frame_equal(before, self.data)


class SQLTests(unittest.TestCase):
    def assertParity(self, frame, reference=AS_OF, threshold=30):
        assessed = assess_deals(frame, reference, threshold)
        report = compare_analysis(assessed, reference, threshold)
        self.assertTrue(report.matches.all(), report.loc[~report.matches].to_string())
        return sql_analysis(assessed, reference, threshold)

    def test_hand_calculated_kpis_and_stage_values(self):
        result = self.assertParity(example())
        self.assertEqual(result["kpis"]["revenue_at_risk"], 1100)
        self.assertEqual(result["kpis"]["win_rate"], .5)
        self.assertEqual(result["stages"].revenue_at_risk.tolist(), [1100, 0])
        self.assertEqual(result["deals"].risk_severity.tolist(), ["Low", "Low", "Medium", "Medium", "High", "Critical", "Closed", "Closed"])

    def test_threshold_boundaries_odd_and_one_day(self):
        for threshold in (1, 3, 30, 60, 61, 3650):
            with self.subTest(threshold=threshold):
                self.assertParity(example(), threshold=threshold)

    def test_analysis_date_recomputes_independently(self):
        result = self.assertParity(example(), date(2026, 9, 22))
        self.assertEqual(result["kpis"]["revenue_at_risk"], 1500)

    def test_closed_only_open_only_empty_and_zero_denominators(self):
        for indexes in ([], [0, 1], [6, 7], [4, 5]):
            frame = example().iloc[indexes].copy()
            frame["deal_value"] = 0
            with self.subTest(indexes=indexes):
                result = self.assertParity(frame)
                self.assertIsNone(result["kpis"]["revenue_at_risk_share"])
                if not indexes:
                    self.assertIsNone(result["kpis"]["average_deal_value"])
                    self.assertEqual(result["kpis"]["deal_count"], 0)

    def test_optional_followups_missing_all_null_and_zero(self):
        for variant in (example().drop(columns="follow_ups"), example().assign(follow_ups=None), example().assign(follow_ups=0)):
            self.assertParity(variant)

    def test_saved_sample_and_filtered_rows(self):
        sample = pd.read_excel(ROOT / "data/sample/revenue_risk_sample_data.xlsx", sheet_name="Deals")
        from src.column_mapper import suggest_mapping, standardize_columns
        mapped = standardize_columns(sample, suggest_mapping(sample.columns))
        assessed = assess_deals(mapped, date(2026, 9, 22))
        for selections in ({}, {"status": ["Won"]}, {"stage": [assessed.stage.iloc[0]], "risk_severity": ["High", "Critical"]}):
            report = compare_analysis(filter_deals(assessed, selections), date(2026, 9, 22), 30)
            self.assertTrue(report.matches.all())

    def test_tampered_python_derivations_are_detected(self):
        assessed = assess_deals(example(), AS_OF)
        assessed.loc[4, "is_stalled"] = False
        assessed.loc[4, "days_inactive"] = 999
        assessed.loc[4, "risk_severity"] = "Low"
        report = compare_analysis(assessed, AS_OF, 30)
        failures = report.loc[~report.matches]
        self.assertIn("revenue_at_risk", failures.item.tolist())
        self.assertIn("005: days_inactive", failures.item.tolist())
        self.assertIn("005: risk_severity", failures.item.tolist())

    def test_query_like_labels_are_data_and_inputs_unchanged(self):
        frame = example()
        frame.loc[0, "stage"] = "x'); DROP TABLE assessed; --"
        frame.loc[0, "deal_id"] = "'quoted id'"
        before = frame.copy(deep=True)
        self.assertParity(frame)
        pd.testing.assert_frame_equal(before, frame)

    def test_varied_decimal_amounts_and_stage_populations(self):
        import random
        generator = random.Random(13)
        rows = []
        for index in range(150):
            inactive = generator.randrange(150)
            rows.append(dict(deal_id=str(index), deal_value=generator.randrange(1000000) / 100,
                             created_date=pd.Timestamp(AS_OF) - pd.Timedelta(days=inactive + 12),
                             last_activity_date=pd.Timestamp(AS_OF) - pd.Timedelta(days=inactive),
                             status=generator.choice(["Open", "Open", "Won", "Lost"]),
                             stage=generator.choice(["A", "B", "C"]),
                             follow_ups=generator.choice([None, 0, 1, 4])))
        self.assertParity(pd.DataFrame(rows), threshold=31)

    def test_invalid_inputs_fail_explicitly(self):
        for threshold in (0, -1, True, 1.5, "30", 3651):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                sql_analysis(example(), AS_OF, threshold)
        for reference in (None, "bad", 123):
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                sql_analysis(example(), reference, 30)
        with self.assertRaises(ValueError):
            sql_analysis(example().assign(status="Unknown"), AS_OF, 30)


class ActionInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.app.radio[0].set_value("Try sample data").run()
        self.app.date_input[0].set_value(date(2026, 9, 22)).run()
        self.app.button[0].click().run()

    def test_action_plan_and_successful_independent_check(self):
        self.assertEqual(len(self.app.exception), 0)
        self.assertIn("Download action plan", [b.label for b in self.app.get("download_button")])
        next(b for b in self.app.button if b.label == "Run calculation check").click().run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertTrue(any("comparisons agree" in s.value for s in self.app.success))
        self.assertIn("Download calculation check", [b.label for b in self.app.get("download_button")])
        self.app.number_input[0].set_value(3650).run()
        self.assertFalse(any("comparisons agree" in s.value for s in self.app.success))
        self.assertNotIn("Download calculation check", [b.label for b in self.app.get("download_button")])
        self.assertTrue(any("No deals meet the stalled rule" in m.value for m in self.app.markdown))

    def test_check_failure_and_disagreement_are_never_success(self):
        with patch("src.sql_engine.compare_analysis", side_effect=RuntimeError("test")):
            next(b for b in self.app.button if b.label == "Run calculation check").click().run()
        self.assertTrue(any("could not finish" in w.value for w in self.app.warning))
        fake = pd.DataFrame([dict(scope="KPI", item="deal_count", python_result=120, sql_result=119, matches=False)])
        with patch("src.sql_engine.compare_analysis", return_value=fake):
            next(b for b in self.app.button if b.label == "Run calculation check").click().run()
        self.assertTrue(any("disagree" in w.value for w in self.app.error))
        self.assertEqual(len(self.app.exception), 0)

    def test_invalid_data_has_no_action_plan_or_check(self):
        self.app.radio[0].set_value("Try messy test data").run()
        self.app.button[0].click().run()
        self.assertNotIn("Run calculation check", [b.label for b in self.app.button])
        self.assertNotIn("Download action plan", [b.label for b in self.app.get("download_button")])


if __name__ == "__main__":
    unittest.main()
