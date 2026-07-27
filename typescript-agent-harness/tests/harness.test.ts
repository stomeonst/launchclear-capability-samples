import assert from "node:assert/strict";
import test from "node:test";

import { AgentHarness } from "../src/harness.js";
import type { AgentTool } from "../src/types.js";

function tools(calls: string[]): AgentTool[] {
  return [
    {
      name: "read_fixture",
      risk: "read",
      async execute(input) {
        calls.push("read_fixture");
        return { found: true, ...input };
      },
    },
    {
      name: "draft_reply",
      risk: "internal_write",
      async execute(input) {
        calls.push("draft_reply");
        return { draft: String(input.message ?? "ready") };
      },
    },
    {
      name: "send_message",
      risk: "external_write",
      async execute() {
        calls.push("send_message");
        return { sent: true };
      },
    },
    {
      name: "fail",
      risk: "read",
      async execute() {
        throw new Error("fixture_failure");
      },
    },
  ];
}

function task(overrides: Record<string, unknown> = {}) {
  return {
    id: "demo-task",
    objective: "Prepare a reply",
    ownerConfirmed: true,
    sanitized: true,
    allowedTools: ["read_fixture", "draft_reply", "send_message", "fail"],
    plan: [{ tool: "read_fixture", input: { orderId: "DEMO-1" } }],
    ...overrides,
  };
}

test("executes bounded read and internal tools", async () => {
  const calls: string[] = [];
  const receipt = await new AgentHarness(tools(calls)).run(
    task({
      plan: [
        { tool: "read_fixture", input: { orderId: "DEMO-1" } },
        { tool: "draft_reply", input: { message: "Ready" } },
      ],
    }),
  );

  assert.equal(receipt.status, "completed");
  assert.deepEqual(calls, ["read_fixture", "draft_reply"]);
  assert.equal(receipt.completedSteps, 2);
  assert.match(receipt.receiptHash, /^[a-f0-9]{64}$/);
});

test("stops before an external write", async () => {
  const calls: string[] = [];
  const receipt = await new AgentHarness(tools(calls)).run(
    task({
      plan: [
        { tool: "read_fixture", input: {} },
        { tool: "send_message", input: { destination: "fictional-contact" } },
      ],
    }),
  );

  assert.equal(receipt.status, "human_approval_required");
  assert.equal(receipt.reason, "external_write_requires_approval");
  assert.equal(receipt.pendingCall?.tool, "send_message");
  assert.deepEqual(calls, ["read_fixture"]);
});

test("blocks a tool outside the allowlist", async () => {
  const calls: string[] = [];
  const receipt = await new AgentHarness(tools(calls)).run(
    task({
      allowedTools: ["read_fixture"],
      plan: [{ tool: "draft_reply", input: {} }],
    }),
  );

  assert.equal(receipt.status, "blocked");
  assert.equal(receipt.reason, "tool_not_allowed");
  assert.deepEqual(calls, []);
});

test("blocks missing owner confirmation", async () => {
  const receipt = await new AgentHarness(tools([])).run(
    task({ ownerConfirmed: false }),
  );
  assert.equal(receipt.reason, "owner_confirmation_missing");
});

test("blocks sensitive values", async () => {
  const receipt = await new AgentHarness(tools([])).run(
    task({
      plan: [{ tool: "read_fixture", input: { apiKey: "sk-fictional-secret" } }],
    }),
  );
  assert.equal(receipt.reason, "sensitive_input_detected");
});

test("enforces the step limit", async () => {
  const calls: string[] = [];
  const receipt = await new AgentHarness(tools(calls)).run(
    task({
      maxSteps: 1,
      plan: [
        { tool: "read_fixture", input: {} },
        { tool: "draft_reply", input: {} },
      ],
    }),
  );
  assert.equal(receipt.reason, "step_limit_reached");
  assert.deepEqual(calls, ["read_fixture"]);
});

test("trims context to the configured window", async () => {
  const receipt = await new AgentHarness(tools([])).run(
    task({
      maxContextEntries: 1,
      plan: [
        { tool: "read_fixture", input: { sequence: 1 } },
        { tool: "read_fixture", input: { sequence: 2 } },
      ],
    }),
  );
  assert.equal(receipt.context.length, 1);
  assert.equal(receipt.context[0]?.input.sequence, 2);
});

test("turns a tool exception into a blocked receipt", async () => {
  const receipt = await new AgentHarness(tools([])).run(
    task({ plan: [{ tool: "fail", input: {} }] }),
  );
  assert.equal(receipt.status, "blocked");
  assert.equal(receipt.reason, "tool_failed:fixture_failure");
});

test("produces the same hash for the same run", async () => {
  const first = await new AgentHarness(tools([])).run(task());
  const second = await new AgentHarness(tools([])).run(task());
  assert.equal(first.receiptHash, second.receiptHash);
});
