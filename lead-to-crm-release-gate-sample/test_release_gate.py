import json
import unittest

from run_acceptance import ROOT, run_suite


class ReleaseGateFixtureTests(unittest.TestCase):
    def test_fixture_ids_are_complete_and_unique(self):
        cases = json.loads((ROOT / "fixture_cases.json").read_text(encoding="utf-8"))
        ids = [case["id"] for case in cases]
        self.assertEqual(ids, [f"LC-{index:02d}" for index in range(1, 13)])
        self.assertEqual(len(ids), len(set(ids)))

    def test_initial_fixture_reproduces_two_bounded_findings(self):
        report = run_suite("initial")
        failed = [result["id"] for result in report["results"] if not result["passed"]]
        self.assertEqual(report["passed"], 10)
        self.assertEqual(report["failed"], 2)
        self.assertEqual(report["release_recommendation"], "hold")
        self.assertEqual(failed, ["LC-06", "LC-07"])

    def test_corrected_fixture_passes_all_twelve_checks(self):
        report = run_suite("corrected")
        self.assertEqual(report["passed"], 12)
        self.assertEqual(report["failed"], 0)
        self.assertEqual(report["release_recommendation"], "conditional_release")

    def test_fixture_uses_only_reserved_example_addresses(self):
        cases = json.loads((ROOT / "fixture_cases.json").read_text(encoding="utf-8"))
        addresses = [case["input"].get("email", "") for case in cases]
        addresses.extend(
            address
            for case in cases
            for address in case["input"].get("existing_emails", [])
        )
        for address in addresses:
            if "@" in address:
                self.assertTrue(address.strip().lower().endswith("@example.test"))


if __name__ == "__main__":
    unittest.main()
