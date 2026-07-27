import unittest

from evidencegate.agents import DiagnosisRepairAgent
from evidencegate.demo import build_demo
from evidencegate.models import RepairRequest, State
from evidencegate.orchestrator import EvidenceGateOrchestrator


class EvidenceGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = EvidenceGateOrchestrator()

    def test_valid_demo_stops_for_human_approval(self) -> None:
        request, fixtures = build_demo()
        result = self.orchestrator.run(request, fixtures)
        self.assertEqual(result.run_receipt.state, State.HUMAN_APPROVAL_REQUIRED)
        self.assertEqual(result.run_receipt.tests_total, 3)
        self.assertEqual(result.run_receipt.tests_failed, 0)
        self.assertTrue(result.run_receipt.approval_required)

    def test_sensitive_material_blocks_run(self) -> None:
        request, fixtures = build_demo()
        request = RepairRequest(
            **{
                **request.__dict__,
                "materials": ("api_key=should-never-be-accepted",),
            }
        )
        result = self.orchestrator.run(request, fixtures)
        self.assertEqual(result.run_receipt.state, State.BLOCKED_SENSITIVE_DATA)
        self.assertIn("api_key", result.scope_contract.sensitive_findings)

    def test_missing_ownership_blocks_run(self) -> None:
        request, fixtures = build_demo()
        request = RepairRequest(**{**request.__dict__, "owner_confirmed": False})
        result = self.orchestrator.run(request, fixtures)
        self.assertEqual(result.run_receipt.state, State.BLOCKED_MISSING_EVIDENCE)

    def test_out_of_scope_change_blocks_repair(self) -> None:
        request, fixtures = build_demo()
        request = RepairRequest(**{**request.__dict__, "allowed_fields": ("email",)})
        result = self.orchestrator.run(request, fixtures)
        self.assertEqual(result.run_receipt.state, State.BLOCKED_OUT_OF_SCOPE)
        self.assertEqual(result.repair_proposal.rollback, "no change was applied")

    def test_email_normalization_is_deterministic(self) -> None:
        first = DiagnosisRepairAgent.transform({"email": " DEMO@Example.COM "})
        second = DiagnosisRepairAgent.transform({"email": "demo@example.com"})
        self.assertEqual(first["dedup_key"], second["dedup_key"])

    def test_invalid_email_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid"):
            DiagnosisRepairAgent.transform({"email": "missing-at.example.com"})

    def test_permitted_repair_contains_rollback_instruction(self) -> None:
        request, fixtures = build_demo()
        result = self.orchestrator.run(request, fixtures)
        self.assertIn("restore original mapping", result.repair_proposal.rollback)

    def test_unexpected_invalid_fixture_fails_verification(self) -> None:
        request, _ = build_demo()
        result = self.orchestrator.run(request, [{"email": ""}])
        self.assertEqual(result.run_receipt.state, State.VERIFICATION_FAILED)
        self.assertEqual(result.run_receipt.tests_failed, 1)

    def test_receipt_hashes_are_repeatable(self) -> None:
        request, fixtures = build_demo()
        first = self.orchestrator.run(request, fixtures).run_receipt
        second = self.orchestrator.run(request, fixtures).run_receipt
        self.assertEqual(first.input_hash, second.input_hash)
        self.assertEqual(first.output_hash, second.output_hash)


if __name__ == "__main__":
    unittest.main()
