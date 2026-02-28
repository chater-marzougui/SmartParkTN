import { useState, useCallback } from "react";
import { assistantApi, type ChatMessage } from "../api/assistant";

export function useAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (content: string, context?: { plate?: string; session_id?: string }) => {
      setError(null);
      const userMsg: ChatMessage = { role: "user", content };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      try {
        const res = await assistantApi.chat(content, context);
        const assistantMsg: ChatMessage = {
          role: "assistant",
          content: res.data.answer,
          sources: res.data.sources,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch {
        setError("Failed to get a response. Please try again.");
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const clearHistory = useCallback(() => setMessages([]), []);

  return { messages, isLoading, error, sendMessage, clearHistory };
}
