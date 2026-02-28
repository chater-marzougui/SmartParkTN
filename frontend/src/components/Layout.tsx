import { Link, useLocation, Outlet } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAuthStore } from "../store/authStore";
import { useDashboardStore } from "../store/dashboardStore";
import {
  LayoutDashboard, Car, Clock, History, List, Bot, BarChart2,
  Bell, Shield, LogOut, Wifi, WifiOff, ChevronRight,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const navItems = [
  { to: "/dashboard",       label: "Live Dashboard",    icon: LayoutDashboard },
  { to: "/vehicles",        label: "Vehicle Registry",  icon: Car },
  { to: "/sessions/active", label: "Active Sessions",   icon: Clock },
  { to: "/sessions",        label: "Session History",   icon: History },
  { to: "/events",          label: "Event Log",         icon: List },
  { to: "/assistant",       label: "AI Assistant",      icon: Bot },
  { to: "/analytics",       label: "Analytics",         icon: BarChart2 },
  { to: "/alerts",          label: "Alerts",            icon: Bell },
  { to: "/admin",           label: "Admin Panel",       icon: Shield },
];

export default function Layout() {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { wsConnected, alerts } = useDashboardStore();
  const unresolvedAlerts = alerts.filter((a) => !a.resolved).length;

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <aside className="w-60 border-r bg-card flex flex-col shrink-0">
        {/* Logo */}
        <div className="h-16 flex items-center gap-2 px-4 border-b">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <Car className="h-4 w-4 text-primary-foreground" />
          </div>
          <div>
            <p className="text-sm font-bold leading-tight">TunisPark AI</p>
            <p className="text-xs text-muted-foreground">Smart Parking</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          {navItems.map(({ to, label, icon: Icon }) => {
            const active = location.pathname.startsWith(to) && (to !== "/" || location.pathname === "/");
            return (
              <Link key={to} to={to}>
                <span
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                    active
                      ? "bg-primary text-primary-foreground font-medium"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {label}
                  {label === "Alerts" && unresolvedAlerts > 0 && (
                    <Badge variant="destructive" className="ml-auto h-5 px-1.5 text-xs">
                      {unresolvedAlerts}
                    </Badge>
                  )}
                </span>
              </Link>
            );
          })}
        </nav>

        <Separator />

        {/* Footer */}
        <div className="p-3 space-y-2">
          <div className="flex items-center gap-2 px-1">
            <Tooltip>
              <TooltipTrigger>
                {wsConnected ? (
                  <Wifi className="h-4 w-4 text-green-500" />
                ) : (
                  <WifiOff className="h-4 w-4 text-red-500" />
                )}
              </TooltipTrigger>
              <TooltipContent>{wsConnected ? "Live connected" : "Disconnected"}</TooltipContent>
            </Tooltip>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium truncate">{user?.full_name ?? user?.username}</p>
              <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
            </div>
            <Avatar className="h-7 w-7">
              <AvatarFallback className="text-xs">
                {user?.full_name?.[0] ?? "U"}
              </AvatarFallback>
            </Avatar>
          </div>
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2 text-muted-foreground" onClick={logout}>
            <LogOut className="h-4 w-4" /> Sign out
          </Button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
