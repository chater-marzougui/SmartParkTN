import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Vehicles from "./pages/Vehicles";
import ActiveSessions from "./pages/ActiveSessions";
import SessionHistory from "./pages/SessionHistory";
import EventLog from "./pages/EventLog";
import Assistant from "./pages/Assistant";
import Analytics from "./pages/Analytics";
import Alerts from "./pages/Alerts";
import AdminPanel from "./pages/Admin";
import UserManagement from "./pages/UserManagement";

function App() {
  return (
    <TooltipProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="vehicles" element={<Vehicles />} />
            <Route path="sessions/active" element={<ActiveSessions />} />
            <Route path="sessions" element={<SessionHistory />} />
            <Route path="events" element={<EventLog />} />
            <Route path="assistant" element={<Assistant />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="admin" element={<AdminPanel />} />
            <Route path="admin/users" element={<UserManagement />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </TooltipProvider>
  );
}

export default App;
