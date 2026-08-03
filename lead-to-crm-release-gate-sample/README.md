# Lead-to-CRM AI Workflow Release Gate Sample

Sample ID: LC-L2C-2026-08-SYNTHETIC

Prepared by Gang Qu on 2026-08-03.

## Truth boundary

This is an independently prepared fictional capability sample. No customer commissioned, reviewed, approved, sponsored, or paid for it. It uses synthetic data and no production system, private repository, credential, customer record, API key, or personal data.

## Business goal

Check that one qualified website lead creates exactly one traceable CRM record while preserving consent, low-confidence human review, failure handling, and audit evidence.

## Fixed scope

1. One fictional Lead-to-CRM workflow.
2. Two fictional connected systems: FormBridge Fixture and NimbusCRM Sandbox Fixture.
3. One deterministic classification fixture with no model API call.
4. Twelve acceptance checks.
5. One bounded retest of the findings.

## Initial result

Ten checks passed and two failed. The initial recommendation was to hold release.

### Finding F-01

An unknown campaign code created a CRM record with no owner. The record could remain outside every sales queue.

Acceptance condition: every unknown campaign must receive a fallback owner and a human-review task.

### Finding F-02

The workflow produced a notification while `approval_state` was still `pending`.

Acceptance condition: only `approved` may create a notification. `pending`, `rejected`, and `snoozed` must create no notification.

## Bounded retest

The fictional correction added a fallback owner, a review task, and a strict approval-state check. F-01 and F-02 passed on retest. The other ten fixtures were replayed and remained passing. Final result: twelve of twelve checks passed.

## Reproduce the evidence

The sample now includes a human-readable matrix, twelve synthetic fixture cases, a deterministic runner, and zero-dependency unit tests.

```bash
python3 run_acceptance.py --version initial
python3 run_acceptance.py --version corrected
python3 -m unittest -v test_release_gate.py
```

Expected summary:

| Fixture state | Passed | Failed | Recommendation |
| --- | ---: | ---: | --- |
| Initial | 10 | 2 | Hold |
| Corrected | 12 | 0 | Conditional release |

The initial run reproduces only LC-06 and LC-07. The corrected run closes both findings while replaying the other ten cases. Every email address uses the reserved `example.test` domain. The runner makes no network request and writes to no external system.

Files:

1. [`acceptance_matrix.csv`](acceptance_matrix.csv) provides the reviewable twelve-check matrix.
2. [`fixture_cases.json`](fixture_cases.json) contains the synthetic inputs and policy expectations.
3. [`run_acceptance.py`](run_acceptance.py) simulates the initial and corrected fixture states.
4. [`test_release_gate.py`](test_release_gate.py) verifies coverage, the two bounded findings, the clean retest, and the reserved-data boundary.

## Example release recommendation

Conditional release. The actual business owner must confirm ownership rules, notification recipients, and consent-field meaning, then replay one real configuration in a sandbox. The first 24 hours should be observed for duplicate suppression, review-queue backlog, CRM write failures, and notification volume.

This recommendation applies only to the fictional fixture. It does not prove that a real production workflow has passed acceptance.

## Commercial boundary

The current fixed-scope service covers one existing workflow, up to two connected systems, and twelve reproducible checks. It delivers a boundary map, test matrix, evidence-linked findings, a release recommendation, and one bounded retest within 48 hours after complete sanitized inputs, confirmed scope, and verified payment.

The service excludes security testing, regulated-data review, production credentials, real customer data in public channels, destructive operations, a new multi-system implementation, and guarantees about revenue, conversion, compliance, or absolute reliability.
