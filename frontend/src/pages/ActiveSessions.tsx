import { useEffect, useState } from "react";
import { sessionsApi, type Session } from "../api/sessions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { formatDistanceToNow, parseISO } from "date-fns";
import { Clock, DoorOpen, AlertTriangle } from "lucide-react";
import { toast } from "sonner";

function SessionCard({ session, maxHours, onClose }: { session: Session; maxHours: number; onClose: () => void }) {
  const minutes = Math.floor((Date.now() - parseISO(session.entry_time).getTime()) / 60000);
  const hours = minutes / 60;
  const overstay = hours > maxHours;

  return (
    <Card className={overstay ? "border-orange-400" : ""}>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle className="font-mono text-lg">{session.plate}</CardTitle>
          <Badge variant={overstay ? "destructive" : "secondary"}>
            {overstay ? "OVERSTAY" : "Parked"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4" />
          <span>Entered {formatDistanceToNow(parseISO(session.entry_time))} ago</span>
        </div>
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{hours.toFixed(1)}h / {maxHours}h max</span>
            <span>{Math.min(100, (hours / maxHours) * 100).toFixed(0)}%</span>
          </div>
          <Progress value={Math.min(100, (hours / maxHours) * 100)} className={overstay ? "[&>div]:bg-orange-500" : ""} />
        </div>
        {session.gate_entry && <p className="text-xs text-muted-foreground">Gate: {session.gate_entry}</p>}
        <Button className="w-full" size="sm" variant="outline" onClick={onClose}>
          <DoorOpen className="h-4 w-4 mr-2" />Close Session
        </Button>
      </CardContent>
    </Card>
  );
}

export default function ActiveSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmId, setConfirmId] = useState<string | null>(null);

  const fetch = async () => {
    setLoading(true);
    try { const r = await sessionsApi.openSessions(); setSessions(r.data); }
    catch { toast.error("Failed to load sessions"); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); const interval = setInterval(fetch, 30000); return () => clearInterval(interval); }, []);

  const closeSession = async (id: string) => {
    try {
      await sessionsApi.close(id);
      toast.success("Session closed");
      setConfirmId(null);
      fetch();
    } catch { toast.error("Failed to close session"); }
  };

  const overstay = sessions.filter((s) => {
    const hours = (Date.now() - parseISO(s.entry_time).getTime()) / 3600000;
    return hours > 24;
  }).length;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Active Sessions</h1>
          <p className="text-sm text-muted-foreground">{sessions.length} vehicles currently parked</p>
        </div>
        {overstay > 0 && (
          <div className="flex items-center gap-2 text-orange-600 bg-orange-50 border border-orange-200 rounded-lg px-3 py-2">
            <AlertTriangle className="h-4 w-4" />
            <span className="text-sm font-medium">{overstay} overstay(s)</span>
          </div>
        )}
      </div>

      {loading && <p className="text-muted-foreground text-sm text-center py-10">Loading sessions…</p>}

      {!loading && sessions.length === 0 && (
        <Card><CardContent className="py-16 text-center text-muted-foreground">No vehicles currently parked</CardContent></Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {sessions.map((s) => (
          <SessionCard key={s.id} session={s} maxHours={24} onClose={() => setConfirmId(s.id)} />
        ))}
      </div>

      <Dialog open={!!confirmId} onOpenChange={() => setConfirmId(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Close Session?</DialogTitle></DialogHeader>
          <p className="text-sm text-muted-foreground">This will calculate the final bill and mark the vehicle as exited.</p>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setConfirmId(null)}>Cancel</Button>
            <Button onClick={() => confirmId && closeSession(confirmId)}>Confirm</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
