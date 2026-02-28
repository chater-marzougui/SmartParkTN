import { useEffect, useState } from "react";
import { sessionsApi, type Session } from "../api/sessions";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Download, Search, FileText } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

const paymentColors: Record<string, string> = {
  pending:  "bg-yellow-100 text-yellow-700",
  paid:     "bg-green-100 text-green-700",
  disputed: "bg-red-100 text-red-700",
  waived:   "bg-gray-100 text-gray-600",
};

export default function SessionHistory() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    sessionsApi.list().then((r) => setSessions(r.data)).catch(() => toast.error("Failed to load sessions")).finally(() => setLoading(false));
  }, []);

  const filtered = sessions.filter((s) => {
    const matchSearch = !search || s.plate.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "all" || s.payment_status === statusFilter;
    return matchSearch && matchStatus;
  });

  const totalRevenue = sessions.filter(s => s.payment_status === "paid").reduce((acc, s) => acc + (s.amount_due ?? 0), 0);

  const exportCSV = async () => {
    try {
      const r = await sessionsApi.export("csv");
      const url = URL.createObjectURL(r.data);
      const a = document.createElement("a"); a.href = url; a.download = "sessions.csv"; a.click();
    } catch { toast.error("Export failed"); }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Session History</h1>
          <p className="text-sm text-muted-foreground">{sessions.length} sessions total · <span className="font-medium text-green-700">{totalRevenue.toFixed(3)} TND revenue</span></p>
        </div>
        <Button variant="outline" onClick={exportCSV}><Download className="h-4 w-4 mr-2" />Export CSV</Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search plate…" className="pl-8" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="paid">Paid</SelectItem>
                <SelectItem value="disputed">Disputed</SelectItem>
                <SelectItem value="waived">Waived</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Plate</TableHead><TableHead>Entry</TableHead><TableHead>Exit</TableHead>
                <TableHead>Duration</TableHead><TableHead>Amount</TableHead><TableHead>Payment</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading && <TableRow><TableCell colSpan={7} className="text-center py-8">Loading…</TableCell></TableRow>}
              {!loading && filtered.length === 0 && <TableRow><TableCell colSpan={7} className="text-center py-8 text-muted-foreground">No sessions found</TableCell></TableRow>}
              {filtered.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-mono font-semibold">{s.plate}</TableCell>
                  <TableCell className="text-sm">{format(new Date(s.entry_time), "dd/MM/yyyy HH:mm")}</TableCell>
                  <TableCell className="text-sm">{s.exit_time ? format(new Date(s.exit_time), "dd/MM/yyyy HH:mm") : <span className="text-blue-600">Active</span>}</TableCell>
                  <TableCell>{s.duration_minutes ? `${Math.floor(s.duration_minutes / 60)}h ${s.duration_minutes % 60}m` : "—"}</TableCell>
                  <TableCell>{s.amount_due != null ? `${s.amount_due.toFixed(3)} TND` : "—"}</TableCell>
                  <TableCell><Badge className={paymentColors[s.payment_status]} variant="outline">{s.payment_status}</Badge></TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm"><FileText className="h-4 w-4" /></Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
