import { useEffect, useState } from "react";
import { alertsApi, type ParkingAlert } from "../api/alerts";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertTriangle, CheckCircle2, XCircle, Info, ShieldAlert } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { toast } from "sonner";

const severityConfig: Record<string, { bg: string; icon: React.ReactNode; label: string }> = {
  critical: { bg: "bg-red-50 border-red-300",    icon: <ShieldAlert className="h-5 w-5 text-red-600" />, label: "CRITICAL" },
  high:     { bg: "bg-orange-50 border-orange-300", icon: <AlertTriangle className="h-5 w-5 text-orange-600" />, label: "HIGH" },
  medium:   { bg: "bg-yellow-50 border-yellow-200", icon: <AlertTriangle className="h-5 w-5 text-yellow-600" />, label: "MEDIUM" },
  low:      { bg: "bg-blue-50 border-blue-200",   icon: <Info className="h-5 w-5 text-blue-600" />, label: "LOW" },
};

function AlertItem({ alert, onResolve }: { alert: ParkingAlert; onResolve: () => void }) {
  const cfg = severityConfig[alert.severity] ?? severityConfig.low;
  return (
    <div className={`rounded-lg border p-4 flex items-start gap-3 ${cfg.bg}`}>
      <div className="shrink-0 mt-0.5">{cfg.icon}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="outline" className="text-xs font-semibold">{cfg.label}</Badge>
          <span className="font-semibold text-sm">{alert.alert_type.replace(/_/g, " ")}</span>
          {alert.plate && <span className="font-mono text-sm bg-white/70 rounded px-2 py-0.5">{alert.plate}</span>}
        </div>
        <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
        <p className="text-xs text-gray-500 mt-1">{formatDistanceToNow(new Date(alert.created_at))} ago {alert.gate_id ? `· Gate ${alert.gate_id}` : ""}</p>
      </div>
      {!alert.resolved && (
        <Button size="sm" variant="outline" className="shrink-0" onClick={onResolve}>
          <CheckCircle2 className="h-4 w-4 mr-1" />Resolve
        </Button>
      )}
      {alert.resolved && <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />}
    </div>
  );
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<ParkingAlert[]>([]);
  const [history, setHistory] = useState<ParkingAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState("all");

  const fetch = async () => {
    setLoading(true);
    try {
      const [activeRes, histRes] = await Promise.all([alertsApi.list(), alertsApi.history()]);
      setAlerts(activeRes.data);
      setHistory(histRes.data);
    } catch { toast.error("Failed to load alerts"); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  const resolve = async (id: string) => {
    await alertsApi.resolve(id);
    toast.success("Alert resolved");
    fetch();
  };

  const filtered = (list: ParkingAlert[]) => severityFilter === "all" ? list : list.filter(a => a.severity === severityFilter);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Alerts</h1>
          <p className="text-sm text-muted-foreground">{alerts.filter(a => !a.resolved).length} unresolved alerts</p>
        </div>
        <Select value={severityFilter} onValueChange={setSeverityFilter}>
          <SelectTrigger className="w-36"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Severities</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Tabs defaultValue="active">
        <TabsList>
          <TabsTrigger value="active">Active ({alerts.filter(a => !a.resolved).length})</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>
        <TabsContent value="active" className="space-y-3 pt-3">
          {loading && <p className="text-center text-muted-foreground py-8">Loading…</p>}
          {!loading && filtered(alerts.filter(a => !a.resolved)).length === 0 && (
            <Card><CardContent className="py-12 text-center text-muted-foreground">
              <CheckCircle2 className="h-8 w-8 mx-auto mb-2 text-green-500" />
              <p>No active alerts. All clear!</p>
            </CardContent></Card>
          )}
          {filtered(alerts.filter(a => !a.resolved)).map((a) => (
            <AlertItem key={a.id} alert={a} onResolve={() => resolve(a.id)} />
          ))}
        </TabsContent>
        <TabsContent value="history" className="space-y-3 pt-3">
          {filtered(history).length === 0 && <p className="text-center text-muted-foreground py-8">No history</p>}
          {filtered(history).map((a) => <AlertItem key={a.id} alert={a} onResolve={() => {}} />)}
        </TabsContent>
      </Tabs>
    </div>
  );
}
