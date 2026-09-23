import json
import unittest
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.explanations import delay_explanations, kpi_explanations, mitigation_for
from src.risk_engine import assess_deals
from test_analytics import example, AS_OF


class ExplanationTests(unittest.TestCase):
    def setUp(self):
        self.data = assess_deals(example(), AS_OF)

    def test_kpi_explanations_use_current_denominators(self):
        table = kpi_explanations(self.data).set_index("KPI")
        self.assertEqual(table.at["Win rate", "Result"], "50.0%")
        self.assertIn("2 closed deals", table.at["Win rate", "How calculated"])
        self.assertEqual(table.at["Revenue at risk", "Result"], "1,100.00")
        self.assertEqual(table.at["Open value at risk", "Result"], "52.4%")
        self.assertEqual(len(table), 10)

    def test_undefined_and_filtered_interpretations(self):
        opened = kpi_explanations(self.data.loc[self.data.status.eq("Open")]).set_index("KPI")
        self.assertEqual(opened.at["Win rate", "Result"], "N/A")
        closed = kpi_explanations(self.data.loc[self.data.status.eq("Won")]).set_index("KPI")
        self.assertEqual(closed.at["Win rate", "Result"], "100.0%")
        self.assertEqual(closed.at["Open value at risk", "Result"], "N/A")
        self.assertEqual(closed.at["Average open age (days)", "Result"], "N/A")

    def test_delay_groups_reconcile_and_explain_stalled_evidence(self):
        table = delay_explanations(self.data)
        self.assertEqual(table.open_deals.sum(), 6)
        self.assertEqual(table.stalled_deals.sum(), 2)
        self.assertEqual(table.revenue_at_risk.sum(), 1100)
        self.assertAlmostEqual(table.share_of_exposure.sum(), 1)
        approval = table.loc[table.delay_reason.eq("Approval")].iloc[0]
        self.assertEqual(approval.stalled_share, .5)
        self.assertEqual(json.loads(approval.stalled_deal_ids), ["006"])
        self.assertAlmostEqual(approval.share_of_exposure, 600 / 1100)
        missing = table.loc[table.delay_reason.isna()].iloc[0]
        self.assertEqual(missing.playbook, "Missing reason")

    def test_optional_absent_closed_empty_and_zero_value(self):
        self.assertIsNone(delay_explanations(self.data.drop(columns="delay_reason")))
        self.assertTrue(delay_explanations(self.data.loc[self.data.status.eq("Won")]).empty)
        table = delay_explanations(self.data.assign(deal_value=0))
        self.assertTrue(table.share_of_exposure.isna().all())
        self.assertEqual(table.stalled_deals.sum(), 2)

    def test_playbooks_are_exact_and_have_generic_fallback(self):
        self.assertEqual(mitigation_for("  MISSING   documents ")[0], "Document checklist")
        self.assertEqual(mitigation_for("Missing Documents / Pricing")[0], "General owner review")
        self.assertEqual(mitigation_for("Not recorded (blank)")[0], "General owner review")
        self.assertEqual(mitigation_for(None)[0], "Missing reason")
        for label in ("Incorrect Information", "Customer Unresponsive", "Pricing / Terms", "Credit Review Pending", "Internal Processing"):
            self.assertNotEqual(mitigation_for(label)[0], "General owner review")
            self.assertTrue(all(mitigation_for(label)))

    def test_changed_threshold_and_filters_recompute_evidence(self):
        changed = assess_deals(example(), AS_OF, 61)
        table = delay_explanations(changed)
        self.assertEqual(table.stalled_deals.sum(), 0)
        self.assertTrue(table.share_of_exposure.isna().all())
        single = delay_explanations(self.data.loc[self.data.deal_id.eq("006")])
        self.assertEqual(single.share_of_exposure.iloc[0], 1)
        self.assertEqual(single.stalled_deals.iloc[0], 1)

    def test_blank_and_literal_label_remain_distinct_without_mutation(self):
        data = self.data.copy()
        data.loc[0, "delay_reason"] = "Not recorded (blank)"
        before = data.copy(deep=True)
        table = delay_explanations(data)
        self.assertEqual(table.delay_reason.isna().sum(), 1)
        self.assertEqual(table.delay_reason.eq("Not recorded (blank)").sum(), 1)
        pd.testing.assert_frame_equal(data, before)


class GuidanceInterfaceTests(unittest.TestCase):
    def test_guide_available_before_upload_and_analysis_after_validation(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
        self.assertIn("Your dashboard guide — start here", [x.label for x in app.expander])
        app.radio[0].set_value("Try sample data").run()
        app.date_input[0].set_value(AS_OF).run()
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any(x.value == "### Understand your KPIs" for x in app.tabs[1].markdown))
        self.assertIn("Download delay analysis and guidance", [b.label for b in app.tabs[2].get("download_button")])
        next(x for x in app.selectbox if x.label == "Recorded delay reason to explore").set_value(1).run()
        self.assertEqual(len(app.exception), 0)
        app.radio[0].set_value("Try alternate column names").run()
        app.button[0].click().run()
        self.assertTrue(any("cannot infer missing reasons" in x.value for x in app.info))
        app.radio[0].set_value("Try messy test data").run()
        app.button[0].click().run()
        self.assertNotIn("Download delay analysis and guidance", [b.label for b in app.get("download_button")])
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
