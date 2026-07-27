# EvidenceGate AgentOps

EvidenceGate AgentOps is a credential-free reference implementation for bounded multi-agent workflow repair. It turns a sanitized repair request into:

1. a machine-readable scope contract;
2. a minimal repair proposal with rollback instructions;
3. an independent verification report;
4. a tamper-evident run receipt;
5. a human approval request when execution would affect an external system.

The included demo uses fictional form and Airtable-style records. It does not connect to Airtable, n8n, Make, Zapier, or any customer system.

## Agents

| Agent | Responsibility | Main artifact |
| --- | --- | --- |
| Scope and Permission | Validate ownership, materials, allowed fields and sensitive-data boundaries | `scope-contract.json` |
| Diagnosis and Repair | Reproduce the failure and produce the smallest permitted transformation | `repair-proposal.json` |
| Verification and Audit | Run independent success and failure tests, verify scope and generate hashes | `verification-report.json`, `run-receipt.json` |

## Demo

```bash
python3 -m evidencegate.demo --output-dir artifacts/demo-run
```

Expected terminal state:

```text
human_approval_required
```

The production write step remains disabled. The receipt records why approval is required.

## Test

```bash
python3 -m unittest discover -s tests -v
```

The test suite covers:

1. a valid sanitized repair request;
2. credential detection;
3. missing ownership confirmation;
4. out-of-scope changes;
5. duplicate email normalization;
6. invalid email rejection;
7. verification failure;
8. deterministic receipt hashing.

## Safety boundary

This directory contains fictional fixtures only. Do not paste credentials, personal data, customer records, private URLs, or confidential workflow exports into issues or demo inputs.

## License

Apache-2.0
