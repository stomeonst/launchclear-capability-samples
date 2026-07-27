from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import EvidenceGateDataHub
from .models import ChangeRequest, jsonable
from .sources import DataHubCliContextSource, FixtureContextSource


DEMO_URN = "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.orders,PROD)"


def build_request(urn: str = DEMO_URN) -> ChangeRequest:
    return ChangeRequest(
        request_id="DH-DEMO-001",
        target_urn=urn,
        removed_fields=("customer_email",),
        owner_confirmed=True,
        reason="Fictional schema cleanup request for impact-analysis demonstration.",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("fixture", "live"), default="fixture")
    parser.add_argument("--urn", default=DEMO_URN)
    parser.add_argument("--output", type=Path, default=Path("artifacts/demo-result.json"))
    parser.add_argument("--fixture", type=Path, default=Path("fixtures/catalog.json"))
    args = parser.parse_args()

    source = (
        FixtureContextSource(args.fixture)
        if args.mode == "fixture"
        else DataHubCliContextSource()
    )
    result = EvidenceGateDataHub(source).analyze(build_request(args.urn))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(jsonable(result), indent=2, ensure_ascii=False) + "\n"
    )
    print(result.receipt.state.value)
    print(args.output)


if __name__ == "__main__":
    main()
