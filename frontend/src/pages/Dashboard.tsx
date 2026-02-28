import { useEffect, useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import { useDashboardStore } from "../store/dashboardStore";
import { analyticsApi } from "../api/analytics";
import { eventsApi, type ParkingEvent } from "../api/events";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { CheckCircle2, XCircle, AlertTriangle, Search, Activity } from "lucide-react";
import { format } from "date-fns";

const decisionStyle: Record<string, { color: string; icon: React.ReactNode }> = {
  allow: { color: "text-green-600 bg-green-50 border-green-200", icon: <CheckCircle2 className="h-4 w-4 text-green-600" /> },
  deny:  { color: "text-red-600 bg-red-50 border-red-200",       icon: <XCircle className="h-4 w-4 text-red-600" /> },
  alert: { color: "text-yellow-600 bg-yellow-50 border-yellow-200", icon: <AlertTriangle className="h-4 w-4 text-yellow-600" /> },
};

export default function Dashboard() {
  useWebSocket();
  const { liveEvents, occupancy, alerts } = useDashboardStore();
  const [events, setEvents] = useState<ParkingEvent[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    analyticsApi.occupancy().then((r) => {
      useDashboardStore.getState().setOccupancy(r.data.current, r.data.total);
    }).catch(() => {});
    eventsApi.list({ limit: "50" }).then((r) => setEvents(r.data)).catch(() => {});
  }, []);

  const criticalAlert = alerts.find((a) => a.severity === "critical" && !a.resolved);
  const filtered = events.filter((e) => !search || e.plate.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Live Gate Dashboard</h1>
          <p className="text-muted-foreground text-sm">Real-time monitoring · all gates</p>
        </div>
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-green-500 animate-pulse" />
          <span className="text-sm text-muted-foreground">Live</span>
        </div>
      </div>

      {/* Critical alert banner */}
      {criticalAlert && (
        <div className="bg-red-50 border border-red-300 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-red-600 shrink-0" />
          <p className="text-red-800 font-medium text-sm">
            ⚠️ BLACKLISTED VEHICLE — {criticalAlert.plate} — {criticalAlert.message}
          </p>
        </div>
      )}

      {/* KPI row */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Occupancy</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{occupancy.current}/{occupancy.total}</p>
            <Progress value={(occupancy.current / occupancy.total) * 100} className="mt-2 h-2" />
            <p className="text-xs text-muted-foreground mt-1">{((occupancy.current / occupancy.total) * 100).toFixed(0)}% full</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Today's Entries</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{events.filter(e => e.event_type === "entry").length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Denied Today</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold text-red-600">{events.filter(e => e.decision === "deny").length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Active Alerts</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold text-yellow-600">{alerts.filter(a => !a.resolved).length}</p></CardContent>
        </Card>
      </div>

      {/* Live event feed + search */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Activity Feed</CardTitle>
            <div className="relative w-64">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search plate…" className="pl-8 h-8 text-sm" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-96">
            {(liveEvents.length === 0 && filtered.length === 0) && (
              <p className="p-4 text-sm text-muted-foreground text-center">No events yet. Waiting for gate activity…</p>
            )}
            {[...liveEvents.map(e => ({ ...e, _live: true })), ...filtered.map(e => ({ ...e, plate: e.plate, gate: e.gate_id, decision: e.decision ?? "allow", timestamp: e.timestamp, _live: false  }))].slice(0, 50).map((event, i) => {
              const style = decisionStyle[event.decision] ?? decisionStyle.allow;
              return (
                <div key={i}>
                  <div className={`flex items-center gap-3 px-4 py-3 ${event._live ? "bg-blue-50/50" : ""}`}>
                    {style.icon}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-mono font-semibold">{event.plate}</p>
                      <p className="text-xs text-muted-foreground">Gate {event.gate}</p>
                    </div>
                    <Badge className={`text-xs ${style.color}`} variant="outline">{event.decision?.toUpperCase()}</Badge>
                    <span className="text-xs text-muted-foreground tabular-nums">
                      {format(new Date(event.timestamp), "HH:mm:ss")}
                    </span>
                  </div>
                  <Separator />
                </div>
              );
            })}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
