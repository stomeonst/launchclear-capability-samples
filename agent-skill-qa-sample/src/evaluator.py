"""Deterministic contract evaluator for the fictional Lead Summary Skill."""

from __future__ import annotations

import re
from dataclasses import dataclass


SENSITIVE_PATTERNS = (
    re.compile(r"\b(?:api[_ -]?key|access[_ -]?token|password|secret)\b", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"https?://[^\s]*(?:private|internal)[^\s]*", re.I),
)


@dataclass(frozen=True)
class Evaluation:
    status: str
    reason: str
    output: dict[str, object] | None = None


def evaluate_request(
    request: str,
    notes: str,
    *,
    requester_owns_notes: bool,
    requested_external_send: bool = False,
) -> Evaluation:
    """Evaluate a request against the revised fictional skill contract."""

    normalized_request = " ".join(request.lower().split())
    allowed_intent = any(
        phrase in normalized_request
        for phrase in ("lead summary", "follow-up draft", "follow up draft")
    )
    if not allowed_intent:
        return Evaluation("out_of_scope", "The request is not a lead summary or follow-up draft.")

    if not requester_owns_notes:
        return Evaluation(
            "needs_owner_confirmation",
            "Confirm that you are authorized to use the sanitized lead notes.",
        )

    if any(pattern.search(notes) for pattern in SENSITIVE_PATTERNS):
        return Evaluation(
            "sensitive_input_blocked",
            "Remove credentials, tokens, passwords, private URLs, and confidential data.",
        )

    confirmed = [
        line.split(":", 1)[1].strip()
        for line in notes.splitlines()
        if line.strip().upper().startswith("FACT:")
    ]
    missing = [
        line.split(":", 1)[1].strip()
        for line in notes.splitlines()
        if line.strip().upper().startswith("MISSING:")
    ]
    boundary = "Human review is required. No message or CRM update was performed."
    if requested_external_send:
        boundary = (
            "The requested send was converted to a draft. "
            "Human review is required and no external action was performed."
        )

    draft_facts = "; ".join(confirmed) if confirmed else "No confirmed lead facts supplied"
    draft = (
        f"Hello, I reviewed the supplied notes. Confirmed context: {draft_facts}. "
        "Could you confirm the missing details before we define a next step?"
    )
    return Evaluation(
        "draft_ready",
        "A bounded draft was prepared.",
        {
            "confirmed_facts": confirmed,
            "missing_information": missing,
            "draft": draft,
            "boundary_note": boundary,
        },
    )
