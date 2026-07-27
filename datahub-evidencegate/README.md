# EvidenceGate for Data Changes

EvidenceGate is a lightweight, evidence-first impact analysis agent for proposed DataHub schema changes. It reads the target asset schema, ownership, downstream lineage and quality signals, produces a bounded change plan and stops at `human_approval_required`.

The repository was started during the 2026 DataHub Agent Hackathon submission window. The local fixture is fictional. No customer metadata, credentials or production systems are included.

## Current capabilities

1. Read a fictional catalog snapshot without network access.
2. Read an authorized DataHub profile through the official `datahub get` and `datahub lineage` CLI operations.
3. Reject changes without owner authority, catalog context or valid schema fields.
4. Surface every downstream dependency as a high-severity impact finding.
5. Include quality signals, rollback guidance and deterministic SHA-256 receipts.
6. Generate a DataHub write-back description preview while executing no mutation.

## Fixture demo

```bash
python3 -m datahub_evidencegate.demo \
  --mode fixture \
  --output artifacts/demo-result.json
```

Expected terminal state:

```text
human_approval_required
```

## Authorized DataHub mode

Install and authenticate the official DataHub CLI first:

```bash
pip install acryl-datahub
datahub check server-config
```

Then run the read-only path:

```bash
python3 -m datahub_evidencegate.demo \
  --mode live \
  --urn "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.orders,PROD)"
```

The live adapter only invokes:

```text
datahub get --urn <URN>
datahub lineage --urn <URN> --direction downstream --format json
```

It never invokes a GraphQL mutation. A future authorized write-back must remain a separate command and require a human to approve the exact preview.

## Test

```bash
python3 -m unittest discover -s tests -v
```

The suite checks authority, missing context, unknown fields, downstream impact, preview-only write-back, deterministic receipts and the live adapter command boundary.

## Official DataHub integration

The command shapes follow the DataHub CLI reference shipped in the official [`datahub-project/datahub-skills`](https://github.com/datahub-project/datahub-skills) repository. The competition build still needs an authorized DataHub instance and a recorded live read before submission.

## Safety boundary

Do not place credentials, personal data, private catalog exports or customer metadata in the fixture directory or public issues. Use a sanitized demo catalog or an explicitly authorized DataHub profile.

## License

Apache-2.0
