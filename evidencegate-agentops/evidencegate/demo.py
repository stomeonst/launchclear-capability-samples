from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import RepairRequest, jsonable
from .orchestrator import EvidenceGateOrchestrator


def build_demo() -> tuple[RepairRequest, list[dict[str, object]]]:
    request = RepairRequest(
        request_id="demo-form-airtable-001",
        owner_confirmed=True,
        description="Fictional form writes an empty email and creates duplicate rows.",
        allowed_path="fictional-form/normalize-and-deduplicate",
        allowed_fields=("email", "dedup_key"),
        acceptance_criteria=(
            "normalize valid email",
            "reject invalid email",
            "identify repeated normalized email",
            "do not write to any external system",
        ),
        materials=("Fictional fixture only. No credentials or customer data.",),
    )
    fixtures = [
        {"email": "  DEMO@example.com  "},
        {"email": "demo@example.com"},
        {"email": "", "expected": "reject"},
    ]
    return request, fixtures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/demo-run")
    args = parser.parse_args()
    request, fixtures = build_demo()
    artifacts = EvidenceGateOrchestrator().run(request, fixtures)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    files = {
        "scope-contract.json": artifacts.scope_contract,
        "repair-proposal.json": artifacts.repair_proposal,
        "verification-report.json": artifacts.verification_report,
        "run-receipt.json": artifacts.run_receipt,
    }
    for name, value in files.items():
        if value is None:
            continue
        (output / name).write_text(
            json.dumps(jsonable(value), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(artifacts.run_receipt.state.value)


if __name__ == "__main__":
    main()
