from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class DecisionState(StrEnum):
    CONTEXT_COLLECTED = "context_collected"
    BLOCKED_MISSING_AUTHORITY = "blocked_missing_authority"
    BLOCKED_MISSING_CONTEXT = "blocked_missing_context"
    BLOCKED_INVALID_CHANGE = "blocked_invalid_change"
    HUMAN_APPROVAL_REQUIRED = "human_approval_required"


@dataclass(frozen=True)
class ChangeRequest:
    request_id: str
    target_urn: str
    removed_fields: tuple[str, ...]
    owner_confirmed: bool
    reason: str


@dataclass(frozen=True)
class AssetContext:
    urn: str
    name: str
    schema_fields: tuple[str, ...]
    owners: tuple[str, ...]
    downstream_urns: tuple[str, ...]
    quality_signals: tuple[str, ...]
    source: str


@dataclass(frozen=True)
class ImpactFinding:
    code: str
    severity: str
    evidence: str


@dataclass(frozen=True)
class ChangePlan:
    request_id: str
    target_urn: str
    removed_fields: tuple[str, ...]
    impacted_downstream_urns: tuple[str, ...]
    findings: tuple[ImpactFinding, ...]
    rollback: str
    writeback_preview: str
    state: DecisionState


@dataclass(frozen=True)
class DecisionReceipt:
    request_id: str
    state: DecisionState
    input_hash: str
    context_hash: str
    plan_hash: str
    approval_required: bool
    trace: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AnalysisResult:
    context: AssetContext | None
    plan: ChangePlan | None
    receipt: DecisionReceipt


def jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    if isinstance(value, StrEnum):
        return value.value
    return value
