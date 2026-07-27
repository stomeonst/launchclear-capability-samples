from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from datahub_evidencegate.analysis import EvidenceGateDataHub
from datahub_evidencegate.demo import DEMO_URN, build_request
from datahub_evidencegate.models import ChangeRequest, DecisionState
from datahub_evidencegate.sources import (
    DataHubCliContextSource,
    FixtureContextSource,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "catalog.json"


class EvidenceGateDataHubTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = EvidenceGateDataHub(FixtureContextSource(FIXTURE))

    def test_fixture_demo_stops_for_human_approval(self) -> None:
        result = self.analyzer.analyze(build_request())
        self.assertEqual(
            result.receipt.state,
            DecisionState.HUMAN_APPROVAL_REQUIRED,
        )
        self.assertTrue(result.receipt.approval_required)
        self.assertEqual(len(result.plan.impacted_downstream_urns), 2)

    def test_missing_authority_blocks_before_context_read(self) -> None:
        request = ChangeRequest(
            **{**build_request().__dict__, "owner_confirmed": False}
        )
        result = self.analyzer.analyze(request)
        self.assertEqual(
            result.receipt.state,
            DecisionState.BLOCKED_MISSING_AUTHORITY,
        )
        self.assertIsNone(result.context)

    def test_unknown_field_is_rejected(self) -> None:
        request = ChangeRequest(
            **{**build_request().__dict__, "removed_fields": ("not_a_field",)}
        )
        result = self.analyzer.analyze(request)
        self.assertEqual(
            result.receipt.state,
            DecisionState.BLOCKED_INVALID_CHANGE,
        )
        self.assertIsNone(result.plan)

    def test_missing_entity_is_blocked(self) -> None:
        request = ChangeRequest(
            **{**build_request().__dict__, "target_urn": "urn:li:dataset:missing"}
        )
        result = self.analyzer.analyze(request)
        self.assertEqual(
            result.receipt.state,
            DecisionState.BLOCKED_MISSING_CONTEXT,
        )

    def test_downstream_assets_become_findings(self) -> None:
        result = self.analyzer.analyze(build_request())
        downstream = [
            finding
            for finding in result.plan.findings
            if finding.code == "downstream_dependency"
        ]
        self.assertEqual(len(downstream), 2)
        self.assertTrue(all(item.severity == "high" for item in downstream))

    def test_writeback_remains_preview_only(self) -> None:
        result = self.analyzer.analyze(build_request())
        self.assertIn("Preview only", result.plan.writeback_preview)
        self.assertIn("No mutation has been executed", result.plan.writeback_preview)

    def test_receipts_are_deterministic(self) -> None:
        first = self.analyzer.analyze(build_request()).receipt
        second = self.analyzer.analyze(build_request()).receipt
        self.assertEqual(first.input_hash, second.input_hash)
        self.assertEqual(first.context_hash, second.context_hash)
        self.assertEqual(first.plan_hash, second.plan_hash)

    @patch("datahub_evidencegate.sources.subprocess.run")
    def test_live_adapter_uses_read_only_datahub_commands(self, run_mock) -> None:
        entity = {
            "properties": {"name": "analytics.orders"},
            "schemaMetadata": {
                "fields": [{"fieldPath": "customer_email"}]
            },
            "ownership": {
                "owners": [{"owner": "urn:li:corpuser:data_steward"}]
            },
            "assertions": [{"name": "freshness passed"}],
        }
        lineage = {
            "relationships": [{"urn": "urn:li:dashboard:(looker,revenue)"}]
        }
        run_mock.side_effect = [
            subprocess.CompletedProcess([], 0, json.dumps(entity), ""),
            subprocess.CompletedProcess([], 0, json.dumps(lineage), ""),
        ]
        context = DataHubCliContextSource().collect(DEMO_URN)
        commands = [call.args[0] for call in run_mock.call_args_list]
        self.assertEqual(commands[0][1], "get")
        self.assertEqual(commands[1][1], "lineage")
        self.assertNotIn("graphql", " ".join(commands[0] + commands[1]))
        self.assertEqual(context.schema_fields, ("customer_email",))
        self.assertEqual(len(context.downstream_urns), 1)

    def test_malformed_fixture_has_no_side_effect(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            malformed = Path(directory) / "catalog.json"
            malformed.write_text(json.dumps({"entities": {}}))
            analyzer = EvidenceGateDataHub(FixtureContextSource(malformed))
            result = analyzer.analyze(build_request())
        self.assertEqual(
            result.receipt.state,
            DecisionState.BLOCKED_MISSING_CONTEXT,
        )


if __name__ == "__main__":
    unittest.main()
