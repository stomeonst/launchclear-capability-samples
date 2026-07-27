# TypeScript Agent Harness

This credential-free sample demonstrates a bounded agent tool loop in TypeScript. It was prepared on 2026-07-27 from fictional data after reviewing a public AI Agent Developer internship description.

The sample provides:

1. a strict tool allowlist;
2. read, internal-write and external-write risk classes;
3. owner-confirmation and sensitive-input gates;
4. a configurable step limit;
5. a bounded context window;
6. deterministic SHA-256 run receipts;
7. a required human approval state before an external message;
8. tests for success and failure paths.

## Run

```bash
pnpm install
pnpm test
pnpm demo
```

The demo uses a fictional WhatsApp-style order-status request. It performs two local steps and stops before `send_message` with:

```text
human_approval_required
```

## Truth boundary

This is an independent concept sample. It does not connect to Meta Business Suite, WhatsApp Cloud API, Messenger, Instagram, n8n, a customer system or any production service. It contains no credentials, customer data, private links or production claims.

The sample demonstrates TypeScript structure, async tool execution, explicit context management and approval controls. It does not claim a production deployment or prior client engagement.

## Files

| File | Purpose |
| --- | --- |
| `src/harness.ts` | Tool loop, scope gates, context bounds and receipt hashing |
| `src/types.ts` | Typed task, tool and receipt contracts |
| `src/demo.ts` | Fictional messaging workflow |
| `tests/harness.test.ts` | Nine deterministic tests |
