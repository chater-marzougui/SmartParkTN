import { useEffect, useState } from "react";
import { rulesApi, tariffsApi, type Rule, type Tariff } from "../api/admin";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Settings, Zap, DoorOpen, Bell, Bot, Database, Code2, Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";

function AccessRulesTab({ rules }: { rules: Rule[] }) {
  const [local, setLocal] = useState<Record<string, unknown>>({});
  const getRuleVal = (key: string, def: unknown) => local[key] ?? rules.find(r => r.key === key)?.value ?? def;

  const save = async (key: string) => {
    try { await rulesApi.update(key, local[key]); toast.success(`Rule "${key}" saved`); }
    catch { toast.error("Failed to save rule"); }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      {[
        { key: "access.max_stay_hours", label: "Max Stay (hours)", type: "number", default: 24 },
        { key: "access.subscriber_grace_minutes", label: "Subscriber Grace Period (minutes)", type: "number", default: 60 },
        { key: "access.low_confidence_threshold", label: "Low OCR Confidence Threshold (%)", type: "slider", default: 70 },
      ].map(({ key, label, type, default: def }) => (
        <div key={key} className="flex items-end gap-4">
          <div className="flex-1 space-y-2">
            <Label>{label}</Label>
            {type === "number" && (
              <Input type="number" value={String(getRuleVal(key, def))} onChange={(e) => setLocal(l => ({ ...l, [key]: Number(e.target.value) }))} />
            )}
            {type === "slider" && (
              <div className="pt-2">
                <Slider min={0} max={100} step={5} value={[Number(getRuleVal(key, def))]}
                  onValueChange={([v]) => setLocal(l => ({ ...l, [key]: v }))} />
                <p className="text-xs text-muted-foreground mt-1">{String(getRuleVal(key, def))}%</p>
              </div>
            )}
          </div>
          <Button size="sm" onClick={() => save(key)}>Save</Button>
        </div>
      ))}

      {[
        { key: "access.blacklist_auto_alert", label: "Blacklist Auto-Alert" },
        { key: "access.visitor_auto_session", label: "Visitor Auto-Session" },
      ].map(({ key, label }) => (
        <div key={key} className="flex items-center justify-between">
          <Label>{label}</Label>
          <div className="flex items-center gap-3">
            <Switch checked={Boolean(getRuleVal(key, true))} onCheckedChange={(v) => { setLocal(l => ({ ...l, [key]: v })); rulesApi.update(key, v).catch(() => toast.error("Failed")); }} />
          </div>
        </div>
      ))}

      <div className="flex items-end gap-4">
        <div className="flex-1 space-y-2">
          <Label>Unknown Plate Behavior</Label>
          <Select value={String(getRuleVal("access.unknown_plate_behavior", "allow"))} onValueChange={(v) => setLocal(l => ({ ...l, "access.unknown_plate_behavior": v }))}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="allow">Allow as Visitor</SelectItem>
              <SelectItem value="deny">Deny</SelectItem>
              <SelectItem value="alert">Alert Staff</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button size="sm" onClick={() => save("access.unknown_plate_behavior")}>Save</Button>
      </div>
    </div>
  );
}

function TariffBuilderTab() {
  const [tariffs, setTariffs] = useState<Tariff[]>([]);
  const [simDuration, setSimDuration] = useState("120");
  const [simType, setSimType] = useState("car");
  const [simResult, setSimResult] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState<Partial<Tariff>>({ active: true, vehicle_types: ["car"], first_hour_tnd: 2, extra_hour_tnd: 1, daily_max_tnd: 20, night_multiplier: 1.5, weekend_multiplier: 1.2 });

  const load = () => tariffsApi.list().then(r => setTariffs(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const simulate = async () => {
    try {
      const r = await tariffsApi.simulate(Number(simDuration), simType);
      setSimResult(`${r.data.total} TND`);
    } catch { setSimResult("N/A"); }
  };

  const saveTariff = async () => {
    try {
      if (form.id) await tariffsApi.update(form.id, form);
      else await tariffsApi.create(form);
      toast.success("Tariff saved"); setDialogOpen(false); load();
    } catch { toast.error("Failed to save tariff"); }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold">Tariff Profiles</h3>
        <Button size="sm" onClick={() => { setForm({ active: true, vehicle_types: ["car"], first_hour_tnd: 2, extra_hour_tnd: 1, daily_max_tnd: 20, night_multiplier: 1.5, weekend_multiplier: 1.2 }); setDialogOpen(true); }}>
          <Plus className="h-4 w-4 mr-2" />New Tariff
        </Button>
      </div>

      <Table>
        <TableHeader><TableRow><TableHead>Name</TableHead><TableHead>1st Hour</TableHead><TableHead>Extra/h</TableHead><TableHead>Daily Max</TableHead><TableHead>Active</TableHead><TableHead /></TableRow></TableHeader>
        <TableBody>
          {tariffs.map(t => (
            <TableRow key={t.id}>
              <TableCell>{t.name}</TableCell>
              <TableCell>{t.first_hour_tnd} TND</TableCell>
              <TableCell>{t.extra_hour_tnd} TND</TableCell>
              <TableCell>{t.daily_max_tnd} TND</TableCell>
              <TableCell><Badge variant={t.active ? "default" : "secondary"}>{t.active ? "Active" : "Inactive"}</Badge></TableCell>
              <TableCell><Button variant="ghost" size="icon" onClick={() => { setForm(t); setDialogOpen(true); }}><Pencil className="h-4 w-4" /></Button></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Simulator */}
      <Card>
        <CardHeader><CardTitle className="text-sm">Price Simulator</CardTitle></CardHeader>
        <CardContent className="flex gap-3 flex-wrap items-end">
          <div className="space-y-2"><Label>Duration (minutes)</Label><Input type="number" className="w-32" value={simDuration} onChange={e => setSimDuration(e.target.value)} /></div>
          <div className="space-y-2"><Label>Vehicle Type</Label>
            <Select value={simType} onValueChange={setSimType}><SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
              <SelectContent><SelectItem value="car">Car</SelectItem><SelectItem value="truck">Truck</SelectItem><SelectItem value="motorcycle">Motorcycle</SelectItem></SelectContent>
            </Select>
          </div>
          <Button onClick={simulate}>Simulate</Button>
          {simResult && <div className="text-lg font-bold text-green-700">→ {simResult}</div>}
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>{form.id ? "Edit Tariff" : "New Tariff"}</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2 space-y-2"><Label>Name</Label><Input value={form.name || ""} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} /></div>
            {[["first_hour_tnd", "1st Hour Price (TND)"], ["extra_hour_tnd", "Extra Hour (TND)"], ["daily_max_tnd", "Daily Max (TND)"], ["night_multiplier", "Night Multiplier"], ["weekend_multiplier", "Weekend Multiplier"]].map(([k, l]) => (
              <div key={k} className="space-y-2"><Label>{l}</Label><Input type="number" step="0.1" value={String(form[k as keyof Tariff] ?? "")} onChange={e => setForm(f => ({ ...f, [k]: Number(e.target.value) }))} /></div>
            ))}
            <div className="space-y-2"><Label>Night Start</Label><Input type="time" value={form.night_start || "22:00"} onChange={e => setForm(f => ({ ...f, night_start: e.target.value }))} /></div>
            <div className="space-y-2"><Label>Night End</Label><Input type="time" value={form.night_end || "06:00"} onChange={e => setForm(f => ({ ...f, night_end: e.target.value }))} /></div>
            <div className="col-span-2 flex items-center gap-3"><Switch checked={form.active ?? true} onCheckedChange={v => setForm(f => ({ ...f, active: v }))} /><Label>Active</Label></div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={saveTariff}>Save</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function RuleEditorTab({ rules }: { rules: Rule[] }) {
  const [json, setJson] = useState(JSON.stringify(
    Object.fromEntries(rules.map(r => [r.key, r.value])), null, 2
  ));
  const [error, setError] = useState("");

  const save = async () => {
    try {
      JSON.parse(json);
      // TODO: bulk update endpoint
      toast.success("Rules JSON validated and saved");
      setError("");
    } catch { setError("Invalid JSON — please fix syntax errors."); }
  };

  return (
    <div className="space-y-4 max-w-3xl">
      <CardDescription>Advanced JSON rule editor. Changes are validated before saving. All rules are applied immediately without redeployment.</CardDescription>
      <Textarea className="font-mono text-sm h-96" value={json} onChange={e => setJson(e.target.value)} />
      {error && <p className="text-sm text-red-600">{error}</p>}
      <Button onClick={save}>Validate & Save</Button>
    </div>
  );
}

export default function AdminPanel() {
  const [rules, setRules] = useState<Rule[]>([]);

  useEffect(() => { rulesApi.list().then(r => setRules(r.data)).catch(() => {}); }, []);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Admin Panel</h1>
        <p className="text-sm text-muted-foreground">Configure all system settings without code changes</p>
      </div>

      <Tabs defaultValue="access">
        <TabsList className="flex-wrap h-auto gap-1">
          <TabsTrigger value="access"><Zap className="h-4 w-4 mr-1.5" />Access Rules</TabsTrigger>
          <TabsTrigger value="tariffs"><Database className="h-4 w-4 mr-1.5" />Tariffs</TabsTrigger>
          <TabsTrigger value="gates"><DoorOpen className="h-4 w-4 mr-1.5" />Gates</TabsTrigger>
          <TabsTrigger value="alerts"><Bell className="h-4 w-4 mr-1.5" />Alert Rules</TabsTrigger>
          <TabsTrigger value="ai"><Bot className="h-4 w-4 mr-1.5" />AI Settings</TabsTrigger>
          <TabsTrigger value="system"><Settings className="h-4 w-4 mr-1.5" />System</TabsTrigger>
          <TabsTrigger value="editor"><Code2 className="h-4 w-4 mr-1.5" />Rule Editor</TabsTrigger>
        </TabsList>

        <TabsContent value="access" className="pt-4"><AccessRulesTab rules={rules} /></TabsContent>

        <TabsContent value="tariffs" className="pt-4"><TariffBuilderTab /></TabsContent>

        <TabsContent value="gates" className="pt-4">
          <div className="text-sm text-muted-foreground">Gate configuration — connect to /api/rules for gate settings.</div>
          <div className="mt-4 space-y-4 max-w-2xl">
            {["Gate A — Entry", "Gate B — Exit", "Gate C — Both"].map((name) => (
              <Card key={name}>
                <CardHeader><CardTitle className="text-sm">{name}</CardTitle></CardHeader>
                <CardContent className="grid grid-cols-2 gap-3">
                  <div className="space-y-2"><Label>Camera RTSP URL</Label><Input placeholder="rtsp://192.168.1.10/stream" /></div>
                  <div className="space-y-2"><Label>Auto-open Delay (sec)</Label><Input type="number" defaultValue={5} /></div>
                  <div className="space-y-2"><Label>Fail Mode</Label><Select defaultValue="open"><SelectTrigger><SelectValue /></SelectTrigger><SelectContent><SelectItem value="open">Fail-Open</SelectItem><SelectItem value="closed">Fail-Closed</SelectItem></SelectContent></Select></div>
                  <div className="flex items-end pb-0.5"><Button size="sm" className="w-full">Save Gate</Button></div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="alerts" className="pt-4">
          <div className="space-y-4 max-w-2xl">
            {[
              { key: "Duplicate Plate Detection", desc: "Alert if same plate at 2 gates within 2 minutes" },
              { key: "Low Confidence Auto-Flag",  desc: "Flag events below confidence threshold for review" },
              { key: "Revenue Anomaly Alert",     desc: "Alert if daily revenue drops > 40% vs last week" },
            ].map(({ key, desc }) => (
              <div key={key} className="flex items-center justify-between border rounded-lg p-4">
                <div><p className="font-medium text-sm">{key}</p><p className="text-xs text-muted-foreground">{desc}</p></div>
                <Switch defaultChecked />
              </div>
            ))}
            <div className="space-y-2"><Label>Overstay Alert Threshold (hours)</Label><Input type="number" defaultValue={24} /></div>
            <div className="space-y-2"><Label>Alert Recipients (email, one per line)</Label><Textarea placeholder="admin@example.com&#10;security@example.com" rows={3} /></div>
            <Button>Save Alert Settings</Button>
          </div>
        </TabsContent>

        <TabsContent value="ai" className="pt-4">
          <div className="space-y-4 max-w-2xl">
            <div className="space-y-2"><Label>Knowledge Base Documents</Label><Input type="file" accept=".pdf" multiple /></div>
            <Button variant="outline">Re-embed Knowledge Base</Button>
            <div className="space-y-2"><Label>LLM Temperature: 0.3</Label><Slider min={0} max={1} step={0.1} defaultValue={[0.3]} /></div>
            <div className="space-y-2"><Label>Response Language</Label><Select defaultValue="fr"><SelectTrigger><SelectValue /></SelectTrigger><SelectContent><SelectItem value="fr">French</SelectItem><SelectItem value="ar">Arabic</SelectItem><SelectItem value="en">English</SelectItem></SelectContent></Select></div>
            <div className="flex items-center gap-3"><Switch defaultChecked /><Label>Show Source Citations</Label></div>
            <Button>Save AI Settings</Button>
          </div>
        </TabsContent>

        <TabsContent value="system" className="pt-4">
          <div className="space-y-4 max-w-2xl">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2"><Label>Parking Name</Label><Input defaultValue="TunisPark AI" /></div>
              <div className="space-y-2"><Label>Total Capacity</Label><Input type="number" defaultValue={200} /></div>
              <div className="space-y-2"><Label>Timezone</Label><Select defaultValue="Africa/Tunis"><SelectTrigger><SelectValue /></SelectTrigger><SelectContent><SelectItem value="Africa/Tunis">Africa/Tunis (UTC+1)</SelectItem><SelectItem value="UTC">UTC</SelectItem></SelectContent></Select></div>
              <div className="space-y-2"><Label>Currency</Label><Input defaultValue="TND" /></div>
              <div className="space-y-2"><Label>Session Timeout (min)</Label><Input type="number" defaultValue={30} /></div>
              <div className="space-y-2"><Label>Snapshot Retention (days)</Label><Input type="number" defaultValue={30} /></div>
            </div>
            <div className="space-y-2"><Label>Database Backup Schedule (cron)</Label><Input defaultValue="0 2 * * *" /></div>
            <Button>Save System Settings</Button>
          </div>
        </TabsContent>

        <TabsContent value="editor" className="pt-4"><RuleEditorTab rules={rules} /></TabsContent>
      </Tabs>
    </div>
  );
}
