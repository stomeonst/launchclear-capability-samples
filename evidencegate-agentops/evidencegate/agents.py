from __future__ import annotations

import re
from collections.abc import Iterable

from .models import (
    RepairProposal,
    RepairRequest,
    ScopeContract,
    State,
    VerificationCase,
    VerificationReport,
)

SENSITIVE_PATTERNS = {
    "api_key": re.compile(r"\b(?:api[_ -]?key|secret)\s*[:=]\s*\S+", re.I),
    "bearer_token": re.compile(r"\bbearer\s+[A-Za-z0-9._-]+", re.I),
    "private_url": re.compile(r"https?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.)", re.I),
}


class ScopePermissionAgent:
    def evaluate(self, request: RepairRequest) -> ScopeContract:
        if not request.owner_confirmed or not request.acceptance_criteria:
            return self._contract(request, State.BLOCKED_MISSING_EVIDENCE)

        findings = tuple(
            label
            for label, pattern in SENSITIVE_PATTERNS.items()
            if any(pattern.search(material) for material in request.materials)
        )
        if findings:
            return self._contract(request, State.BLOCKED_SENSITIVE_DATA, findings)
        if not request.allowed_path or not request.allowed_fields:
            return self._contract(request, State.BLOCKED_OUT_OF_SCOPE)
        return self._contract(request, State.SCOPE_CHECKED)

    @staticmethod
    def _contract(
        request: RepairRequest,
        state: State,
        findings: tuple[str, ...] = (),
    ) -> ScopeContract:
        return ScopeContract(
            request_id=request.request_id,
            allowed_path=request.allowed_path,
            allowed_fields=request.allowed_fields,
            acceptance_criteria=request.acceptance_criteria,
            sensitive_findings=findings,
            state=state,
        )


class DiagnosisRepairAgent:
    def propose(self, contract: ScopeContract) -> RepairProposal:
        if contract.state is not State.SCOPE_CHECKED:
            raise ValueError("scope contract must pass before diagnosis")
        changed_fields = ("email", "dedup_key")
        if not set(changed_fields).issubset(set(contract.allowed_fields)):
            return RepairProposal(
                request_id=contract.request_id,
                root_cause="required repair exceeds allowed fields",
                changed_fields=changed_fields,
                transformation="none",
                rollback="no change was applied",
                state=State.BLOCKED_OUT_OF_SCOPE,
            )
        return RepairProposal(
            request_id=contract.request_id,
            root_cause="email field is not normalized and duplicate writes lack a stable key",
            changed_fields=changed_fields,
            transformation="normalize email and derive dedup_key from normalized email",
            rollback="restore original mapping and remove the derived dedup_key field",
            state=State.REPAIR_PROPOSED,
        )

    @staticmethod
    def transform(record: dict[str, object]) -> dict[str, object]:
        raw = record.get("email")
        if not isinstance(raw, str):
            raise ValueError("email must be a string")
        email = raw.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("email is invalid")
        return {**record, "email": email, "dedup_key": email}


class VerificationAuditAgent:
    def verify(
        self,
        contract: ScopeContract,
        proposal: RepairProposal,
        fixtures: Iterable[dict[str, object]],
    ) -> VerificationReport:
        scope_preserved = set(proposal.changed_fields).issubset(contract.allowed_fields)
        cases: list[VerificationCase] = []
        seen: set[str] = set()
        for index, fixture in enumerate(fixtures, start=1):
            try:
                transformed = DiagnosisRepairAgent.transform(fixture)
                key = str(transformed["dedup_key"])
                duplicate = key in seen
                seen.add(key)
                cases.append(
                    VerificationCase(
                        name=f"fixture_{index}",
                        passed=True,
                        evidence=f"normalized={transformed['email']};duplicate={duplicate}",
                    )
                )
            except ValueError as exc:
                expected_failure = fixture.get("expected") == "reject"
                cases.append(
                    VerificationCase(
                        name=f"fixture_{index}",
                        passed=expected_failure,
                        evidence=f"rejected={exc}",
                    )
                )
        passed = scope_preserved and all(case.passed for case in cases)
        return VerificationReport(
            request_id=contract.request_id,
            scope_preserved=scope_preserved,
            cases=tuple(cases),
            state=State.VERIFICATION_PASSED if passed else State.VERIFICATION_FAILED,
        )
