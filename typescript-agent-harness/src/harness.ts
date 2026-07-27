import { createHash } from "node:crypto";

import type {
  AgentTask,
  AgentTool,
  ContextEntry,
  RunReceipt,
  ToolCall,
} from "./types.js";

const SENSITIVE_PATTERN =
  /(api[_ -]?key|password|secret|bearer\s+[a-z0-9._-]+|sk-[a-z0-9_-]+)/i;

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(canonicalJson).join(",")}]`;
  }
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    const fields = Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(record[key])}`);
    return `{${fields.join(",")}}`;
  }
  return JSON.stringify(value);
}

function containsSensitiveValue(value: unknown): boolean {
  if (typeof value === "string") {
    return SENSITIVE_PATTERN.test(value);
  }
  if (Array.isArray(value)) {
    return value.some(containsSensitiveValue);
  }
  if (value !== null && typeof value === "object") {
    return Object.entries(value as Record<string, unknown>).some(
      ([key, nested]) =>
        SENSITIVE_PATTERN.test(key) || containsSensitiveValue(nested),
    );
  }
  return false;
}

function hashReceipt(receipt: Omit<RunReceipt, "receiptHash">): string {
  return createHash("sha256").update(canonicalJson(receipt)).digest("hex");
}

export class AgentHarness {
  private readonly tools: Map<string, AgentTool>;

  constructor(tools: AgentTool[]) {
    this.tools = new Map(tools.map((tool) => [tool.name, tool]));
  }

  async run(task: AgentTask): Promise<RunReceipt> {
    const context: ContextEntry[] = [];

    if (!task.ownerConfirmed) {
      return this.receipt(task.id, "blocked", "owner_confirmation_missing", context);
    }
    if (!task.sanitized || containsSensitiveValue(task)) {
      return this.receipt(task.id, "blocked", "sensitive_input_detected", context);
    }

    const maxSteps = Math.max(1, task.maxSteps ?? 5);
    const maxContextEntries = Math.max(1, task.maxContextEntries ?? 5);

    for (const [index, call] of task.plan.entries()) {
      if (index >= maxSteps) {
        return this.receipt(task.id, "blocked", "step_limit_reached", context);
      }

      const tool = this.resolveTool(call, task.allowedTools);
      if (!tool) {
        return this.receipt(task.id, "blocked", "tool_not_allowed", context);
      }
      if (tool.risk === "external_write") {
        return this.receipt(
          task.id,
          "human_approval_required",
          "external_write_requires_approval",
          context,
          call,
        );
      }

      try {
        const output = await tool.execute(call.input);
        context.push({
          step: index + 1,
          tool: call.tool,
          input: call.input,
          output,
        });
        if (context.length > maxContextEntries) {
          context.splice(0, context.length - maxContextEntries);
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : "unknown_tool_error";
        return this.receipt(task.id, "blocked", `tool_failed:${message}`, context);
      }
    }

    return this.receipt(task.id, "completed", "plan_completed", context);
  }

  private resolveTool(call: ToolCall, allowedTools: string[]): AgentTool | undefined {
    if (!allowedTools.includes(call.tool)) {
      return undefined;
    }
    return this.tools.get(call.tool);
  }

  private receipt(
    taskId: string,
    status: RunReceipt["status"],
    reason: string,
    context: ContextEntry[],
    pendingCall?: ToolCall,
  ): RunReceipt {
    const base: Omit<RunReceipt, "receiptHash"> = {
      taskId,
      status,
      reason,
      completedSteps: context.length,
      context,
      ...(pendingCall ? { pendingCall } : {}),
    };
    return { ...base, receiptHash: hashReceipt(base) };
  }
}
