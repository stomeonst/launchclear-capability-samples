# AI Agent Skill QA Sample Design

Date: 2026-07-27

## Purpose

Create a public, fictional delivery sample for the fixed-scope AI Agent Skill QA service. The sample must show how a buyer's vague skill can be reviewed, narrowed, patched, and retested without using customer data, credentials, private repositories, or live external actions.

## Chosen approach

Use a fictional Lead Summary Skill with deliberately broad activation and unsafe delivery language as the input. Deliver:

1. A before skill contract.
2. A five-task trigger and boundary matrix.
3. Three prioritized, reproducible findings.
4. A bounded after skill contract.
5. A deterministic Python evaluator that models the revised contract.
6. Automated tests covering activation, near misses, ownership, sensitive inputs, external delivery, and structured draft output.

This approach gives buyers a complete review artifact while keeping the sample small enough to inspect in minutes.

## Alternatives considered

1. A prose-only report would be faster to publish but would provide weaker retest evidence.
2. A full agent runtime would look more technical but would add model and provider dependencies that distract from the QA service.
3. The selected contract evaluator is dependency-free, deterministic, and directly maps each claim to a test.

## Data and action boundaries

All names, organizations, notes, tasks, and outputs are fictional. The evaluator accepts plain strings and boolean confirmations only. It rejects sensitive-token patterns, requires requester ownership confirmation, and cannot send email or call an external service. Valid requests end in `draft_ready`.

## Success criteria

1. Five representative tasks are documented with expected activation and outcome.
2. Three findings include reproduction, impact, and bounded correction.
3. Tests prove all stated activation and boundary behaviors.
4. The root repository links directly to the sample.
5. Public wording labels the work as fictional and avoids customer or production claims.

