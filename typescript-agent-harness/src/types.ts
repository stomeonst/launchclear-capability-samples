export type HarnessStatus =
  | "completed"
  | "blocked"
  | "human_approval_required";

export type ToolRisk = "read" | "internal_write" | "external_write";

export interface AgentTask {
  id: string;
  objective: string;
  ownerConfirmed: boolean;
  sanitized: boolean;
  allowedTools: string[];
  plan: ToolCall[];
  maxSteps?: number;
  maxContextEntries?: number;
}

export interface ToolCall {
  tool: string;
  input: Record<string, unknown>;
}

export interface AgentTool {
  name: string;
  risk: ToolRisk;
  execute(input: Record<string, unknown>): Promise<Record<string, unknown>>;
}

export interface ContextEntry {
  step: number;
  tool: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
}

export interface RunReceipt {
  taskId: string;
  status: HarnessStatus;
  reason: string;
  completedSteps: number;
  pendingCall?: ToolCall;
  context: ContextEntry[];
  receiptHash: string;
}
