import { useEffect, useState } from "react";
import { analyticsApi, type RevenueData, type PeakHour, type DecisionBreakdown } from "../api/analytics";
import { useDashboardStore } from "../store/dashboardStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { TrendingUp, Car, DoorOpen, XCircle } from "lucide-react";

const COLORS = ["#22c55e", "#ef4444", "#f59e0b"];

export default function Analytics() {
  const { occupancy } = useDashboardStore();
  const [revenue, setRevenue] = useState<RevenueData[]>([]);
  const [peakHours, setPeakHours] = useState<PeakHour[]>([]);
  const [decisions, setDecisions] = useState<DecisionBreakdown>({ allow: 0, deny: 0, alert: 0 });

  useEffect(() => {
    analyticsApi.revenue().then((r) => setRevenue(r.data)).catch(() => {});
    analyticsApi.peakHours().then((r) => setPeakHours(r.data)).catch(() => {});
    analyticsApi.decisions().then((r) => setDecisions(r.data)).catch(() => {});
  }, []);

  const totalRevenue = revenue.reduce((a, r) => a + r.amount, 0);
  const decisionsData = [
    { name: "Allowed", value: decisions.allow },
    { name: "Denied",  value: decisions.deny },
    { name: "Alert",   value: decisions.alert },
  ];

  // Build 24-hour grid for peak heatmap
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const maxCount = Math.max(...peakHours.map((p) => p.count), 1);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p className="text-sm text-muted-foreground">Revenue, occupancy, and traffic patterns</p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {[
          { title: "Total Revenue", value: `${totalRevenue.toFixed(3)} TND`, icon: TrendingUp, color: "text-green-600" },
          { title: "Occupancy", value: `${occupancy.current}/${occupancy.total}`, icon: Car, color: "text-blue-600" },
          { title: "Total Allowed", value: decisions.allow, icon: DoorOpen, color: "text-green-600" },
          { title: "Total Denied", value: decisions.deny, icon: XCircle, color: "text-red-600" },
        ].map(({ title, value, icon: Icon, color }) => (
          <Card key={title}>
            <CardHeader className="pb-2 flex-row items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
              <Icon className={`h-4 w-4 ${color}`} />
            </CardHeader>
            <CardContent><p className={`text-2xl font-bold ${color}`}>{value}</p></CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="revenue">
        <TabsList>
          <TabsTrigger value="revenue">Revenue</TabsTrigger>
          <TabsTrigger value="decisions">Decisions</TabsTrigger>
          <TabsTrigger value="peak">Peak Hours</TabsTrigger>
        </TabsList>

        <TabsContent value="revenue">
          <Card>
            <CardHeader><CardTitle>Daily Revenue (TND)</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={revenue}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="amount" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Revenue (TND)" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="decisions">
          <Card>
            <CardHeader><CardTitle>Decision Breakdown</CardTitle></CardHeader>
            <CardContent className="flex justify-center">
              <ResponsiveContainer width={350} height={300}>
                <PieChart>
                  <Pie data={decisionsData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                    {decisionsData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="peak">
          <Card>
            <CardHeader><CardTitle>Peak Hours Heatmap</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <div className="grid gap-1" style={{ gridTemplateColumns: `60px repeat(24, minmax(28px, 1fr))` }}>
                  <div />
                  {Array.from({ length: 24 }, (_, h) => (
                    <div key={h} className="text-xs text-center text-muted-foreground">{h}h</div>
                  ))}
                  {days.map((day, d) => (
                    <>
                      <div key={day} className="text-xs text-muted-foreground flex items-center">{day}</div>
                      {Array.from({ length: 24 }, (_, h) => {
                        const cell = peakHours.find((p) => p.day === d && p.hour === h);
                        const intensity = cell ? cell.count / maxCount : 0;
                        return (
                          <div
                            key={h}
                            className="h-6 rounded-sm"
                            style={{ backgroundColor: `rgba(59,130,246,${intensity})`, border: "1px solid rgba(0,0,0,0.05)" }}
                            title={cell ? `${cell.count} entries` : "0 entries"}
                          />
                        );
                      })}
                    </>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
