---
name: lead-summary-draft
description: Use when the requester asks for a reviewable sales follow-up draft from lead notes they are authorized to use and have sanitized.
---

# Lead Summary Draft

## Required inputs

1. Sanitized lead notes supplied by the requester.
2. Requester confirmation that they are authorized to use the notes.
3. A request to prepare a summary or draft.

## Refuse or pause

1. Do not process credentials, API keys, access tokens, passwords, private URLs, personal identifiers, or confidential customer data.
2. Ask for ownership confirmation when it is missing.
3. Do not activate for personal inbox summaries, general research, or unrelated writing.
4. Do not infer missing company facts, budgets, needs, results, or relationships.

## Output

Return a structured summary with:

1. Confirmed facts.
2. Missing information.
3. A concise follow-up draft.
4. A boundary note explaining that the draft requires human review.

Never send a message, update a CRM, or take another external action.

