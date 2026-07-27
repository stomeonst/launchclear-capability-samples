import { AgentHarness } from "./harness.js";
import type { AgentTool } from "./types.js";

const tools: AgentTool[] = [
  {
    name: "read_fixture",
    risk: "read",
    async execute() {
      return {
        channel: "whatsapp",
        request: "Where is order DEMO-1042?",
        source: "fictional_fixture",
      };
    },
  },
  {
    name: "draft_reply",
    risk: "internal_write",
    async execute(input) {
      return {
        draft: `Order ${String(input.orderId)} is ready for a human-reviewed reply.`,
      };
    },
  },
  {
    name: "send_message",
    risk: "external_write",
    async execute() {
      throw new Error("external tool must not execute without approval");
    },
  },
];

const harness = new AgentHarness(tools);
const receipt = await harness.run({
  id: "fictional-whatsapp-order-status",
  objective: "Prepare a bounded order-status reply from fictional data",
  ownerConfirmed: true,
  sanitized: true,
  allowedTools: ["read_fixture", "draft_reply", "send_message"],
  maxSteps: 4,
  maxContextEntries: 4,
  plan: [
    { tool: "read_fixture", input: {} },
    { tool: "draft_reply", input: { orderId: "DEMO-1042" } },
    {
      tool: "send_message",
      input: { destination: "fictional-whatsapp-contact" },
    },
  ],
});

console.log(JSON.stringify(receipt, null, 2));
