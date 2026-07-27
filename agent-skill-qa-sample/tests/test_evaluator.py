import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evaluator import evaluate_request


class LeadSummaryContractTests(unittest.TestCase):
    def test_valid_sanitized_request_prepares_draft(self):
        result = evaluate_request(
            "Prepare a lead summary and follow-up draft",
            "FACT: The buyer requested a two-day pilot.\nMISSING: Budget owner",
            requester_owns_notes=True,
        )
        self.assertEqual(result.status, "draft_ready")

    def test_personal_inbox_request_does_not_activate(self):
        result = evaluate_request(
            "Summarize my personal inbox",
            "A personal message",
            requester_owns_notes=True,
        )
        self.assertEqual(result.status, "out_of_scope")

    def test_missing_owner_confirmation_pauses(self):
        result = evaluate_request(
            "Prepare a lead summary",
            "FACT: The buyer asked for a demo.",
            requester_owns_notes=False,
        )
        self.assertEqual(result.status, "needs_owner_confirmation")

    def test_api_key_is_blocked(self):
        result = evaluate_request(
            "Prepare a lead summary",
            "API key: sk-example123456",
            requester_owns_notes=True,
        )
        self.assertEqual(result.status, "sensitive_input_blocked")

    def test_private_url_is_blocked(self):
        result = evaluate_request(
            "Prepare a lead summary",
            "See https://internal.example.test/private/customer",
            requester_owns_notes=True,
        )
        self.assertEqual(result.status, "sensitive_input_blocked")

    def test_requested_send_is_converted_to_draft(self):
        result = evaluate_request(
            "Prepare a follow-up draft",
            "FACT: The buyer requested a written summary.",
            requester_owns_notes=True,
            requested_external_send=True,
        )
        self.assertEqual(result.status, "draft_ready")
        self.assertIn("converted to a draft", result.output["boundary_note"])

    def test_output_separates_confirmed_and_missing_information(self):
        result = evaluate_request(
            "Prepare a lead summary",
            "FACT: The buyer uses a public CSV.\nMISSING: Acceptance deadline",
            requester_owns_notes=True,
        )
        self.assertEqual(result.output["confirmed_facts"], ["The buyer uses a public CSV."])
        self.assertEqual(result.output["missing_information"], ["Acceptance deadline"])


if __name__ == "__main__":
    unittest.main()

