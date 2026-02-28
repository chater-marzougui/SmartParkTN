import { useEffect, useState } from "react";
import { eventsApi, type ParkingEvent } from "../api/events";
import { assistantApi } from "../api/assistant";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Bot, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";

const decisionIcon: Record<string, React.ReactNode> = {
  allow: <CheckCircle2 className="h-4 w-4 text-green-500" />,
  deny:  <XCircle className="h-4 w-4 text-red-500" />,
  alert: <AlertTriangle className="h-4 w-4 text-yellow-500" />,
};

export default function EventLog() {
  const [events, setEvents] = useState<ParkingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [decisionFilter, setDecisionFilter] = useState("all");
  const [selected, setSelected] = useState<ParkingEvent | null>(null);
  const [explanation, setExplanation] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    eventsApi.list().then((r) => setEvents(r.data)).finally(() => setLoading(false));
  }, []);

  const filtered = events.filter((e) => {
    const matchSearch = !search || e.plate.toLowerCase().includes(search.toLowerCase());
    const matchDecision = decisionFilter === "all" || e.decision === decisionFilter;
    return matchSearch && matchDecision;
  });

  const openDetail = async (event: ParkingEvent) => {
    setSelected(event);
    setExplanation(null);
    if (event.decision === "deny" || event.decision === "alert") {
      try {
        const r = await assistantApi.explain(event.id);
        setExplanation(r.data.reason);
      } catch { setExplanation("Explanation not available."); }
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Event Log</h1>
        <p className="text-sm text-muted-foreground">Full audit trail — every camera detection</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search plate…" className="pl-8" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            <Select value={decisionFilter} onValueChange={setDecisionFilter}>
              <SelectTrigger className="w-36"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="allow">Allow</SelectItem>
                <SelectItem value="deny">Deny</SelectItem>
                <SelectItem value="alert">Alert</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead><TableHead>Plate</TableHead><TableHead>Gate</TableHead>
                <TableHead>Type</TableHead><TableHead>Confidence</TableHead><TableHead>Decision</TableHead>
                <TableHead>Rule Applied</TableHead><TableHead className="text-right">Detail</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading && <TableRow><TableCell colSpan={8} className="text-center py-8">Loading…</TableCell></TableRow>}
              {filtered.map((e) => (
                <TableRow key={e.id} className="cursor-pointer hover:bg-muted/50" onClick={() => openDetail(e)}>
                  <TableCell className="text-xs tabular-nums">{format(new Date(e.timestamp), "dd/MM HH:mm:ss")}</TableCell>
                  <TableCell className="font-mono font-semibold">{e.plate}</TableCell>
                  <TableCell>{e.gate_id}</TableCell>
                  <TableCell><Badge variant="outline" className="text-xs capitalize">{e.event_type}</Badge></TableCell>
                  <TableCell>
                    {e.ocr_confidence != null ? (
                      <span className={e.ocr_confidence < 0.7 ? "text-red-600 font-medium" : ""}>{(e.ocr_confidence * 100).toFixed(0)}%</span>
                    ) : "—"}
                  </TableCell>
                  <TableCell><div className="flex items-center gap-1">{e.decision && decisionIcon[e.decision]}<span className="capitalize text-sm">{e.decision}</span></div></TableCell>
                  <TableCell className="text-xs text-muted-foreground">{e.rule_applied ?? "—"}</TableCell>
                  <TableCell className="text-right"><Button variant="ghost" size="sm" onClick={(ev) => { ev.stopPropagation(); openDetail(e); }}>View</Button></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={!!selected} onOpenChange={() => setSelected(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>Event Detail — {selected?.plate}</DialogTitle></DialogHeader>
          {selected && (
            <div className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div><p className="text-muted-foreground">Timestamp</p><p>{format(new Date(selected.timestamp), "dd/MM/yyyy HH:mm:ss")}</p></div>
                <div><p className="text-muted-foreground">Gate</p><p>{selected.gate_id}</p></div>
                <div><p className="text-muted-foreground">Decision</p><p className="capitalize font-semibold">{selected.decision}</p></div>
                <div><p className="text-muted-foreground">Rule Applied</p><p>{selected.rule_applied ?? "—"}</p></div>
                <div><p className="text-muted-foreground">OCR Confidence</p><p>{selected.ocr_confidence != null ? `${(selected.ocr_confidence * 100).toFixed(1)}%` : "—"}</p></div>
              </div>
              {explanation && (
                <div className="bg-muted rounded-lg p-3">
                  <p className="text-muted-foreground mb-1 text-xs font-medium">AI Explanation</p>
                  <p>{explanation}</p>
                </div>
              )}
              <Button className="w-full" variant="outline" onClick={() => { navigate(`/assistant?plate=${selected.plate}`); setSelected(null); }}>
                <Bot className="h-4 w-4 mr-2" />Ask AI about this event
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
