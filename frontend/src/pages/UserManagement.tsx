import { useState } from "react";
import apiClient from "../api/client";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent } from "@/components/ui/card";
import { Plus, UserCog, ShieldCheck } from "lucide-react";
import { useEffect } from "react";
import { toast } from "sonner";

interface User { id: string; username: string; full_name: string; email: string; role: string; active: boolean; created_at: string }
const roleColors: Record<string, string> = {
  superadmin: "bg-red-100 text-red-700",
  admin:      "bg-purple-100 text-purple-700",
  staff:      "bg-blue-100 text-blue-700",
  viewer:     "bg-gray-100 text-gray-600",
};

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState({ username: "", full_name: "", email: "", password: "", role: "staff" });

  const fetch = () => apiClient.get<User[]>("/api/admin/users").then(r => setUsers(r.data)).catch(() => {});
  useEffect(() => { fetch(); }, []);

  const createUser = async () => {
    try { await apiClient.post("/api/admin/users", form); toast.success("User created"); setDialogOpen(false); fetch(); }
    catch { toast.error("Failed to create user"); }
  };

  const toggleActive = async (user: User) => {
    try {
      await apiClient.put(`/api/admin/users/${user.id}`, { active: !user.active });
      toast.success(`User ${user.active ? "deactivated" : "activated"}`);
      fetch();
    } catch { toast.error("Action failed"); }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><UserCog className="h-6 w-6" />User Management</h1>
          <p className="text-sm text-muted-foreground">{users.length} staff accounts</p>
        </div>
        <Button onClick={() => setDialogOpen(true)}><Plus className="h-4 w-4 mr-2" />Add User</Button>
      </div>

      {/* Role legend */}
      <div className="flex gap-2 flex-wrap">
        {Object.entries(roleColors).map(([role, cls]) => (
          <div key={role} className={`text-xs rounded-full px-3 py-1 ${cls} flex items-center gap-1`}>
            <ShieldCheck className="h-3 w-3" />{role}
          </div>
        ))}
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader><TableRow><TableHead>Name</TableHead><TableHead>Username</TableHead><TableHead>Email</TableHead><TableHead>Role</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
            <TableBody>
              {users.length === 0 && <TableRow><TableCell colSpan={6} className="text-center py-8 text-muted-foreground">No users yet</TableCell></TableRow>}
              {users.map(u => (
                <TableRow key={u.id}>
                  <TableCell className="font-medium">{u.full_name}</TableCell>
                  <TableCell className="font-mono text-sm">{u.username}</TableCell>
                  <TableCell className="text-sm">{u.email}</TableCell>
                  <TableCell><Badge className={roleColors[u.role]} variant="outline">{u.role}</Badge></TableCell>
                  <TableCell><Badge variant={u.active ? "default" : "secondary"}>{u.active ? "Active" : "Inactive"}</Badge></TableCell>
                  <TableCell className="text-right"><Switch checked={u.active} onCheckedChange={() => toggleActive(u)} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Add Staff User</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2"><Label>Full Name</Label><Input value={form.full_name} onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))} /></div>
              <div className="space-y-2"><Label>Username</Label><Input value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} /></div>
              <div className="space-y-2"><Label>Email</Label><Input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} /></div>
              <div className="space-y-2"><Label>Password</Label><Input type="password" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} /></div>
            </div>
            <div className="space-y-2"><Label>Role</Label>
              <Select value={form.role} onValueChange={v => setForm(f => ({ ...f, role: v }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="superadmin">SuperAdmin</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="staff">Staff</SelectItem>
                  <SelectItem value="viewer">Viewer</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={createUser}>Create User</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
