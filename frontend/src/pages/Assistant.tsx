import { useRef, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useAssistant } from "../hooks/useAssistant";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Bot, User, Send, RotateCcw, Loader2 } from "lucide-react";
import { useState } from "react";

const quickPrompts = [
  "Pourquoi ce véhicule a été refusé ?",
  "Quel est le tarif visiteur actuel ?",
  "Combien de revenus ce mois-ci ?",
  "Quelles sont les règles d'accès VIP ?",
  "Comment fonctionne la liste noire ?",
];

export default function Assistant() {
  const [searchParams] = useSearchParams();
  const initialPlate = searchParams.get("plate") ?? "";
  const [input, setInput] = useState(initialPlate ? `Pourquoi ${initialPlate} a été refusé ?` : "");
  const [contextPlate, setContextPlate] = useState(initialPlate);
  const { messages, isLoading, error, sendMessage, clearHistory } = useAssistant();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const msg = input.trim();
    setInput("");
    await sendMessage(msg, contextPlate ? { plate: contextPlate } : undefined);
  };

  return (
    <div className="h-full flex flex-col p-6 gap-4 max-w-4xl mx-auto w-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><Bot className="h-6 w-6 text-primary" />AI Assistant</h1>
          <p className="text-sm text-muted-foreground">Ask questions about rules, decisions, and billing in French</p>
        </div>
        <Button variant="ghost" size="sm" onClick={clearHistory}><RotateCcw className="h-4 w-4 mr-2" />Clear</Button>
      </div>

      {/* Context plate */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Vehicle context:</span>
        <Input
          placeholder="Plate number (optional)"
          className="w-48 h-8 text-sm font-mono"
          value={contextPlate}
          onChange={(e) => setContextPlate(e.target.value)}
        />
        {contextPlate && <Badge variant="outline" className="font-mono">{contextPlate}</Badge>}
      </div>

      {/* Quick prompts */}
      <div className="flex flex-wrap gap-2">
        {quickPrompts.map((p) => (
          <button key={p} className="text-xs bg-muted hover:bg-muted/80 rounded-full px-3 py-1.5 text-muted-foreground hover:text-foreground transition-colors"
            onClick={() => setInput(p)}>
            {p}
          </button>
        ))}
      </div>

      <Separator />

      {/* Messages */}
      <Card className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-12">
                <Bot className="h-10 w-10 mx-auto mb-3 opacity-30" />
                <p className="text-sm">Ask a question about parking rules, billing, or decisions.</p>
                <p className="text-xs mt-1">Answers are grounded in regulations and real system data.</p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                  {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>
                <div className={`max-w-[80%] ${msg.role === "user" ? "items-end" : "items-start"} flex flex-col gap-1`}>
                  <div className={`rounded-2xl px-4 py-2.5 text-sm ${msg.role === "user" ? "bg-primary text-primary-foreground rounded-tr-sm" : "bg-muted rounded-tl-sm"}`}>
                    {msg.content}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {msg.sources.map((s, si) => (
                        <Badge key={si} variant="outline" className="text-xs">{s}</Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3">
                <div className="w-7 h-7 rounded-full bg-muted flex items-center justify-center"><Bot className="h-4 w-4" /></div>
                <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Thinking…</span>
                </div>
              </div>
            )}
            {error && <p className="text-sm text-red-600 text-center">{error}</p>}
            <div ref={bottomRef} />
          </div>
        </ScrollArea>
      </Card>

      {/* Input */}
      <div className="flex gap-2">
        <Input
          placeholder="Ask in French, Arabic, or English…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          disabled={isLoading}
          className="flex-1"
        />
        <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
