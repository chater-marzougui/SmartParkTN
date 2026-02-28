import apiClient from "./client";

export interface ChatMessage { role: "user" | "assistant"; content: string; sources?: string[] }
export interface ChatResponse { answer: string; sources: string[]; confidence: number }
export interface DecisionExplanation { decision: string; reason: string; rule_ref: string; timestamp: string; facts: Record<string, unknown> }

export const assistantApi = {
  chat: (message: string, context?: { plate?: string; session_id?: string }) =>
    apiClient.post<ChatResponse>("/api/assistant/chat", { message, context }),
  explain: (decisionId: string) =>
    apiClient.get<DecisionExplanation>(`/api/assistant/explain/${decisionId}`),
};
