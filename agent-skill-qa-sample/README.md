# Fictional Lead Summary Skill QA Sample

Prepared on 2026-07-27.

This is a fictional, dependency-free demonstration of a fixed-scope AI Agent Skill QA delivery. It contains no customer data, credentials, private repository content, live model calls, or external delivery.

## Buyer question

Can a broad lead-summary skill be narrowed so that it activates only for authorized, sanitized sales notes and always stops at a reviewable draft?

## Delivery

1. [`SKILL.before.md`](fixtures/SKILL.before.md) preserves the fictional starting point.
2. [`qa-report.md`](qa-report.md) contains the trigger matrix and three prioritized findings.
3. [`SKILL.after.md`](fixtures/SKILL.after.md) shows the bounded correction.
4. [`evaluator.py`](src/evaluator.py) models the revised trigger and action contract.
5. [`test_evaluator.py`](tests/test_evaluator.py) provides deterministic retest evidence.

## Run the retest

```bash
python3 -m unittest discover -s agent-skill-qa-sample/tests -v
```

Expected result: seven tests pass.

## Scope boundary

The evaluator prepares a structured draft only. It cannot send email, modify a CRM, open a private link, process a credential, or claim that a customer workflow was repaired.

