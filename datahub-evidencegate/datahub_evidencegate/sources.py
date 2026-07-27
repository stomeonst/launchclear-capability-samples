from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Protocol

from .models import AssetContext


class ContextSource(Protocol):
    def collect(self, urn: str) -> AssetContext:
        """Return the minimum metadata needed for impact analysis."""


class FixtureContextSource:
    def __init__(self, fixture_path: Path) -> None:
        self.fixture_path = fixture_path

    def collect(self, urn: str) -> AssetContext:
        payload = json.loads(self.fixture_path.read_text())
        entity = payload["entities"].get(urn)
        if entity is None:
            raise LookupError(f"fixture has no entity for {urn}")
        return AssetContext(
            urn=urn,
            name=entity["name"],
            schema_fields=tuple(entity.get("schema_fields", [])),
            owners=tuple(entity.get("owners", [])),
            downstream_urns=tuple(entity.get("downstream_urns", [])),
            quality_signals=tuple(entity.get("quality_signals", [])),
            source=f"fixture:{self.fixture_path.name}",
        )


class DataHubCliContextSource:
    """Read-only adapter for an already authenticated DataHub CLI profile."""

    def __init__(
        self,
        executable: str = "datahub",
        timeout_seconds: int = 30,
    ) -> None:
        self.executable = executable
        self.timeout_seconds = timeout_seconds

    def collect(self, urn: str) -> AssetContext:
        entity = self._run(
            "get",
            "--urn",
            urn,
        )
        lineage = self._run(
            "lineage",
            "--urn",
            urn,
            "--direction",
            "downstream",
            "--format",
            "json",
        )
        return self._normalize(urn, entity, lineage)

    def _run(self, *arguments: str) -> dict[str, object]:
        completed = subprocess.run(
            [self.executable, *arguments],
            capture_output=True,
            check=False,
            text=True,
            timeout=self.timeout_seconds,
        )
        if completed.returncode != 0:
            message = completed.stderr.strip() or "DataHub CLI command failed"
            raise RuntimeError(message)
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("DataHub CLI returned non-JSON output") from exc
        if not isinstance(payload, dict):
            raise RuntimeError("DataHub CLI returned an unexpected JSON shape")
        return payload

    @staticmethod
    def _normalize(
        urn: str,
        entity: dict[str, object],
        lineage: dict[str, object],
    ) -> AssetContext:
        schema = entity.get("schemaMetadata") or entity.get("schema") or {}
        fields = schema.get("fields", []) if isinstance(schema, dict) else []
        schema_fields = tuple(
            str(field.get("fieldPath"))
            for field in fields
            if isinstance(field, dict) and field.get("fieldPath")
        )

        ownership = entity.get("ownership") or {}
        owners = ownership.get("owners", []) if isinstance(ownership, dict) else []
        owner_urns = tuple(
            str(owner.get("owner"))
            for owner in owners
            if isinstance(owner, dict) and owner.get("owner")
        )

        edges = lineage.get("relationships") or lineage.get("entities") or []
        downstream = tuple(
            str(edge.get("urn") or edge.get("entity"))
            for edge in edges
            if isinstance(edge, dict) and (edge.get("urn") or edge.get("entity"))
        )

        assertions = entity.get("assertions") or entity.get("qualitySignals") or []
        quality_signals = tuple(
            str(item.get("urn") or item.get("name") or item)
            for item in assertions
            if item
        )
        properties = entity.get("properties") or {}
        name = (
            properties.get("name")
            if isinstance(properties, dict)
            else None
        ) or urn

        return AssetContext(
            urn=urn,
            name=str(name),
            schema_fields=schema_fields,
            owners=owner_urns,
            downstream_urns=downstream,
            quality_signals=quality_signals,
            source="datahub-cli",
        )
