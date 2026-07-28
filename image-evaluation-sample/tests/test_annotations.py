import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = ROOT / "annotations.json"


class AnnotationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))

    def test_sample_discloses_synthetic_origin_and_no_real_customer_data(self):
        self.assertIn("Synthetic", self.payload["asset_origin"])
        self.assertFalse(self.payload["contains_real_customer_data"])

    def test_asset_exists(self):
        asset = ROOT / self.payload["asset"]
        self.assertTrue(asset.is_file())

    def test_score_is_within_declared_range(self):
        scale = self.payload["score_scale"]
        self.assertGreaterEqual(self.payload["overall_score"], scale["minimum"])
        self.assertLessEqual(self.payload["overall_score"], scale["maximum"])

    def test_findings_have_unique_ids_and_required_fields(self):
        required = {
            "id",
            "category",
            "severity",
            "region",
            "evidence",
            "recommendation",
        }
        findings = self.payload["findings"]
        ids = [finding["id"] for finding in findings]
        self.assertEqual(len(ids), len(set(ids)))
        for finding in findings:
            self.assertTrue(required.issubset(finding))

    def test_severity_values_are_bounded(self):
        allowed = {"critical", "major", "minor"}
        for finding in self.payload["findings"]:
            self.assertIn(finding["severity"], allowed)

    def test_evidence_is_specific(self):
        for finding in self.payload["findings"]:
            self.assertGreaterEqual(len(finding["evidence"]), 60)
            self.assertNotIn("looks bad", finding["evidence"].lower())

    def test_critical_finding_requires_revision_label(self):
        has_critical = any(
            finding["severity"] == "critical"
            for finding in self.payload["findings"]
        )
        self.assertTrue(has_critical)
        self.assertEqual(self.payload["overall_label"], "needs_revision")

    def test_acceptance_checks_cover_each_finding(self):
        self.assertGreaterEqual(
            len(self.payload["acceptance_checks"]),
            len(self.payload["findings"]),
        )


if __name__ == "__main__":
    unittest.main()
