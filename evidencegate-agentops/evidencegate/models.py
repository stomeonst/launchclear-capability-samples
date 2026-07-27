from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class State(StrEnum):
    RECEIVED = "received"
    SCOPE_CHECKED = "scope_checked"
    DIAGNOSED = "diagnosed"
    REPAIR_PROPOSED = "repair_proposed"
    VERIFICATION_PASSED = "verification_passed"
    HUMAN_APPROVAL_REQUIRED = "human_approval_required"
    BLOCKED_MISSING_EVIDENCE = "blocked_missing_evidence"
    BLOCKED_OUT_OF_SCOPE = "blocked_out_of_scope"
    BLOCKED_SENSITIVE_DATA = "blocked_sensitive_data"
    VERIFICATION_FAILED = "verification_failed"


@dataclass(frozen=True)
class RepairRequest:
    request_id: str
    owner_confirmed: bool
    description: str
    allowed_path: str
    allowed_fields: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    materials: tuple[str, ...] = ()
    risk: str = "medium"


@dataclass(frozen=True)
class ScopeContract:
    request_id: str
    allowed_path: str
    allowed_fields: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    sensitive_findings: tuple[str, ...]
    state: State


@dataclass(frozen=True)
class RepairProposal:
    request_id: str
    root_cause: str
    changed_fields: tuple[str, ...]
    transformation: str
    rollback: str
    state: State


@dataclass(frozen=True)
class VerificationCase:
    name: str
    passed: bool
    evidence: str


@dataclass(frozen=True)
class VerificationReport:
    request_id: str
    scope_preserved: bool
    cases: tuple[VerificationCase, ...]
    state: State


@dataclass(frozen=True)
class RunReceipt:
    request_id: str
    state: State
    input_hash: str
    output_hash: str
    tests_total: int
    tests_failed: int
    approval_required: bool
    trace: tuple[str, ...] = field(default_factory=tuple)


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
