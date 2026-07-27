from __future__ import annotations

import hashlib
import json

from .models import (
    AnalysisResult,
    ChangePlan,
    ChangeRequest,
    DecisionReceipt,
    DecisionState,
    ImpactFinding,
    jsonable,
)
from .sources import ContextSource


def digest(value: object) -> str:
    encoded = json.dumps(
        jsonable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


class EvidenceGateDataHub:
    def __init__(self, source: ContextSource) -> None:
        self.source = source

    def analyze(self, request: ChangeRequest) -> AnalysisResult:
        trace = ["received"]
        if not request.owner_confirmed:
            return self._blocked(
                request,
                DecisionState.BLOCKED_MISSING_AUTHORITY,
                trace,
            )
        if not request.target_urn or not request.removed_fields:
            return self._blocked(
                request,
                DecisionState.BLOCKED_INVALID_CHANGE,
                trace,
            )

        try:
            context = self.source.collect(request.target_urn)
        except (LookupError, RuntimeError) as exc:
            trace.append(f"context_error:{type(exc).__name__}")
            return self._blocked(
                request,
                DecisionState.BLOCKED_MISSING_CONTEXT,
                trace,
            )
        trace.append(DecisionState.CONTEXT_COLLECTED.value)

        unknown = tuple(
            field
            for field in request.removed_fields
            if field not in context.schema_fields
        )
        if unknown:
            trace.append("unknown_fields")
            return self._blocked(
                request,
                DecisionState.BLOCKED_INVALID_CHANGE,
                trace,
                context=context,
            )

        findings: list[ImpactFinding] = []
        if not context.owners:
            findings.append(
                ImpactFinding(
                    code="missing_owner",
                    severity="high",
                    evidence="DataHub context contains no owner for the target asset.",
                )
            )
        for downstream_urn in context.downstream_urns:
            findings.append(
                ImpactFinding(
                    code="downstream_dependency",
                    severity="high",
                    evidence=f"{downstream_urn} depends on the target asset.",
                )
            )
        for signal in context.quality_signals:
            findings.append(
                ImpactFinding(
                    code="quality_signal",
                    severity="medium",
                    evidence=signal,
                )
            )

        writeback = (
            "Preview only: add a DataHub documentation note recording "
            f"request {request.request_id}, proposed removal "
            f"{', '.join(request.removed_fields)}, and impacted downstream assets. "
            "No mutation has been executed."
        )
        plan = ChangePlan(
            request_id=request.request_id,
            target_urn=request.target_urn,
            removed_fields=request.removed_fields,
            impacted_downstream_urns=context.downstream_urns,
            findings=tuple(findings),
            rollback=(
                "Restore the original schema, re-run downstream validation, "
                "and remove the proposed DataHub documentation note."
            ),
            writeback_preview=writeback,
            state=DecisionState.HUMAN_APPROVAL_REQUIRED,
        )
        trace.append(plan.state.value)
        receipt = DecisionReceipt(
            request_id=request.request_id,
            state=plan.state,
            input_hash=digest(request),
            context_hash=digest(context),
            plan_hash=digest(plan),
            approval_required=True,
            trace=tuple(trace),
        )
        return AnalysisResult(context=context, plan=plan, receipt=receipt)

    @staticmethod
    def _blocked(
        request: ChangeRequest,
        state: DecisionState,
        trace: list[str],
        context: object | None = None,
    ) -> AnalysisResult:
        trace.append(state.value)
        receipt = DecisionReceipt(
            request_id=request.request_id,
            state=state,
            input_hash=digest(request),
            context_hash=digest(context),
            plan_hash=digest(None),
            approval_required=False,
            trace=tuple(trace),
        )
        return AnalysisResult(context=context, plan=None, receipt=receipt)
