#!/usr/bin/env python3
"""Run the fictional Lead-to-CRM release gate fixture deterministically."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
KNOWN_OWNERS = {
    "google": "owner_growth",
    "partner": "owner_partnerships",
}


def simulate_workflow(payload: dict[str, Any], version: str) -> dict[str, Any]:
    """Return the observable outcome for one synthetic submission."""
    email = str(payload.get("email", "")).strip().lower()
    source = payload.get("source")

    if not EMAIL_PATTERN.fullmatch(email):
        return _blocked_result("invalid_email", source)

    if payload.get("consent") is not True:
        return _blocked_result("consent_missing", source)

    owner = KNOWN_OWNERS.get(str(payload.get("campaign", "")))
    review_tasks = 0
    if owner is None and version == "corrected":
        owner = "owner_unassigned_review"
        review_tasks = 1

    existing = {
        str(value).strip().lower()
        for value in payload.get("existing_emails", [])
    }
    crm_action = "update" if email in existing else "create"
    write_sequence = payload.get("crm_write_sequence", ["success"])
    write_succeeded = "success" in write_sequence

    if not write_succeeded:
        return {
            "status": "hold",
            "crm_action": crm_action,
            "crm_records": 0,
            "owner": owner,
            "review_tasks": review_tasks,
            "notifications": 0,
            "evidence_status": "crm_write_failed",
            "source": source,
        }

    approval_state = payload.get("approval_state")
    if version == "initial":
        notifications = int(approval_state not in {"rejected", "snoozed"})
    else:
        notifications = int(approval_state == "approved")

    return {
        "status": "completed",
        "crm_action": crm_action,
        "crm_records": 1,
        "owner": owner,
        "review_tasks": review_tasks,
        "notifications": notifications,
        "evidence_status": "crm_write_succeeded",
        "source": source,
    }


def _blocked_result(reason: str, source: Any) -> dict[str, Any]:
    return {
        "status": "rejected",
        "crm_action": "none",
        "crm_records": 0,
        "owner": None,
        "review_tasks": 0,
        "notifications": 0,
        "evidence_status": reason,
        "source": source,
    }


def run_suite(version: str) -> dict[str, Any]:
    cases = json.loads((ROOT / "fixture_cases.json").read_text(encoding="utf-8"))
    results = []

    for case in cases:
        actual = simulate_workflow(case["input"], version)
        differences = {
            key: {"expected": expected, "actual": actual.get(key)}
            for key, expected in case["expected"].items()
            if actual.get(key) != expected
        }
        results.append(
            {
                "id": case["id"],
                "name": case["name"],
                "passed": not differences,
                "differences": differences,
            }
        )

    passed = sum(result["passed"] for result in results)
    return {
        "sample_id": "LC-L2C-2026-08-SYNTHETIC",
        "version": version,
        "truth_boundary": "fictional fixture; no customer or production system",
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "release_recommendation": "conditional_release" if passed == len(results) else "hold",
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=("initial", "corrected"), required=True)
    args = parser.parse_args()
    print(json.dumps(run_suite(args.version), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
