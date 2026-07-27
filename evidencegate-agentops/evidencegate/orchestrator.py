from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from .agents import DiagnosisRepairAgent, ScopePermissionAgent, VerificationAuditAgent
from .models import RepairRequest, RunReceipt, State, jsonable


def digest(value: object) -> str:
    encoded = json.dumps(
        jsonable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class RunArtifacts:
    scope_contract: object
    repair_proposal: object | None
    verification_report: object | None
    run_receipt: RunReceipt


class EvidenceGateOrchestrator:
    def __init__(self) -> None:
        self.scope_agent = ScopePermissionAgent()
        self.repair_agent = DiagnosisRepairAgent()
        self.verification_agent = VerificationAuditAgent()

    def run(
        self,
        request: RepairRequest,
        fixtures: list[dict[str, object]],
    ) -> RunArtifacts:
        trace = [State.RECEIVED.value]
        contract = self.scope_agent.evaluate(request)
        trace.append(contract.state.value)
        if contract.state is not State.SCOPE_CHECKED:
            return self._blocked(request, contract, trace)

        proposal = self.repair_agent.propose(contract)
        trace.append(proposal.state.value)
        if proposal.state is not State.REPAIR_PROPOSED:
            return self._blocked(request, contract, trace, proposal)

        report = self.verification_agent.verify(contract, proposal, fixtures)
        trace.append(report.state.value)
        terminal = (
            State.HUMAN_APPROVAL_REQUIRED
            if report.state is State.VERIFICATION_PASSED
            else State.VERIFICATION_FAILED
        )
        trace.append(terminal.value)
        receipt = RunReceipt(
            request_id=request.request_id,
            state=terminal,
            input_hash=digest({"request": request, "fixtures": fixtures}),
            output_hash=digest(
                {"contract": contract, "proposal": proposal, "report": report}
            ),
            tests_total=len(report.cases),
            tests_failed=sum(not case.passed for case in report.cases),
            approval_required=terminal is State.HUMAN_APPROVAL_REQUIRED,
            trace=tuple(trace),
        )
        return RunArtifacts(contract, proposal, report, receipt)

    @staticmethod
    def _blocked(
        request: RepairRequest,
        contract: object,
        trace: list[str],
        proposal: object | None = None,
    ) -> RunArtifacts:
        state = getattr(proposal, "state", getattr(contract, "state"))
        receipt = RunReceipt(
            request_id=request.request_id,
            state=state,
            input_hash=digest(request),
            output_hash=digest({"contract": contract, "proposal": proposal}),
            tests_total=0,
            tests_failed=0,
            approval_required=False,
            trace=tuple(trace),
        )
        return RunArtifacts(contract, proposal, None, receipt)
