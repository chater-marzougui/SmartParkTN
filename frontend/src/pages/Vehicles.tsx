import { useEffect, useState } from "react";
import { vehiclesApi, type Vehicle } from "../api/vehicles";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Search, ShieldBan, ShieldCheck } from "lucide-react";
import { toast } from "sonner";

const categoryColors: Record<string, string> = {
  visitor:    "bg-gray-100 text-gray-700",
  subscriber: "bg-blue-100 text-blue-700",
  vip:        "bg-yellow-100 text-yellow-700",
  blacklist:  "bg-red-100 text-red-700",
};

function VehicleForm({ onSave, onClose }: { onSave: () => void; onClose: () => void }) {
  const [form, setForm] = useState<Partial<Vehicle>>({ category: "visitor", vehicle_type: "car" });
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setSaving(true);
    try {
      await vehiclesApi.create(form);
      toast.success("Vehicle added successfully");
      onSave();
      onClose();
    } catch { toast.error("Failed to save vehicle"); }
    finally { setSaving(false); }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Plate Number *</Label>
          <Input placeholder="e.g. 123 تونس 5678" value={form.plate || ""} onChange={(e) => setForm({ ...form, plate: e.target.value })} />
        </div>
        <div className="space-y-2">
          <Label>Category</Label>
          <Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v as Vehicle["category"] })}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="visitor">Visitor</SelectItem>
              <SelectItem value="subscriber">Subscriber</SelectItem>
              <SelectItem value="vip">VIP</SelectItem>
              <SelectItem value="blacklist">Blacklist</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Vehicle Type</Label>
          <Select value={form.vehicle_type} onValueChange={(v) => setForm({ ...form, vehicle_type: v as Vehicle["vehicle_type"] })}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="car">Car</SelectItem>
              <SelectItem value="truck">Truck</SelectItem>
              <SelectItem value="motorcycle">Motorcycle</SelectItem>
              <SelectItem value="bus">Bus</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Owner Name</Label>
          <Input value={form.owner_name || ""} onChange={(e) => setForm({ ...form, owner_name: e.target.value })} />
        </div>
        <div className="space-y-2">
          <Label>Owner Phone</Label>
          <Input value={form.owner_phone || ""} onChange={(e) => setForm({ ...form, owner_phone: e.target.value })} />
        </div>
        <div className="space-y-2">
          <Label>Subscription Expires</Label>
          <Input type="date" value={form.subscription_expires || ""} onChange={(e) => setForm({ ...form, subscription_expires: e.target.value })} />
        </div>
      </div>
      <div className="space-y-2">
        <Label>Notes</Label>
        <Textarea value={form.notes || ""} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={3} />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <Button variant="outline" onClick={onClose}>Cancel</Button>
        <Button onClick={save} disabled={saving}>{saving ? "Saving…" : "Save Vehicle"}</Button>
      </div>
    </div>
  );
}

export default function Vehicles() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [search, setSearch] = useState("");
  const [catFilter, setCatFilter] = useState("all");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetch = async () => {
    setLoading(true);
    try { const r = await vehiclesApi.list(); setVehicles(r.data); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  const filtered = vehicles.filter((v) => {
    const matchSearch = !search || v.plate.toLowerCase().includes(search.toLowerCase()) || v.owner_name?.toLowerCase().includes(search.toLowerCase());
    const matchCat = catFilter === "all" || v.category === catFilter;
    return matchSearch && matchCat;
  });

  const toggleBlacklist = async (vehicle: Vehicle) => {
    try {
      if (vehicle.category === "blacklist") await vehiclesApi.whitelist(vehicle.id);
      else await vehiclesApi.blacklist(vehicle.id);
      toast.success("Vehicle status updated");
      fetch();
    } catch { toast.error("Action failed"); }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold">Vehicle Registry</h1><p className="text-sm text-muted-foreground">{vehicles.length} vehicles registered</p></div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild><Button><Plus className="h-4 w-4 mr-2" />Add Vehicle</Button></DialogTrigger>
          <DialogContent className="max-w-xl">
            <DialogHeader><DialogTitle>Add New Vehicle</DialogTitle></DialogHeader>
            <VehicleForm onSave={fetch} onClose={() => setDialogOpen(false)} />
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search plate or owner…" className="pl-8" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            <Select value={catFilter} onValueChange={setCatFilter}>
              <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="visitor">Visitor</SelectItem>
                <SelectItem value="subscriber">Subscriber</SelectItem>
                <SelectItem value="vip">VIP</SelectItem>
                <SelectItem value="blacklist">Blacklist</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Plate</TableHead><TableHead>Category</TableHead><TableHead>Type</TableHead>
                <TableHead>Owner</TableHead><TableHead>Expires</TableHead><TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading && <TableRow><TableCell colSpan={6} className="text-center py-8 text-muted-foreground">Loading…</TableCell></TableRow>}
              {!loading && filtered.length === 0 && <TableRow><TableCell colSpan={6} className="text-center py-8 text-muted-foreground">No vehicles found</TableCell></TableRow>}
              {filtered.map((v) => (
                <TableRow key={v.id}>
                  <TableCell className="font-mono font-semibold">{v.plate}</TableCell>
                  <TableCell><Badge className={categoryColors[v.category]} variant="outline">{v.category}</Badge></TableCell>
                  <TableCell className="capitalize">{v.vehicle_type}</TableCell>
                  <TableCell>{v.owner_name ?? "—"}</TableCell>
                  <TableCell>{v.subscription_expires ?? "—"}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" onClick={() => toggleBlacklist(v)} title={v.category === "blacklist" ? "Remove from blacklist" : "Blacklist"}>
                      {v.category === "blacklist" ? <ShieldCheck className="h-4 w-4 text-green-600" /> : <ShieldBan className="h-4 w-4 text-red-500" />}
                    </Button>
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
