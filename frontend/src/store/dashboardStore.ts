import { create } from "zustand";
import type { ParkingAlert } from "../api/alerts";
import type { ParkingEvent } from "../api/events";

interface GateEvent {
  id: string;
  plate: string;
  gate: string;
  decision: "allow" | "deny" | "alert";
  timestamp: string;
  snapshot?: string;
}

interface DashboardState {
  liveEvents: GateEvent[];
  alerts: ParkingAlert[];
  recentEvents: ParkingEvent[];
  occupancy: { current: number; total: number };
  wsConnected: boolean;
  addLiveEvent: (event: GateEvent) => void;
  addAlert: (alert: ParkingAlert) => void;
  setOccupancy: (current: number, total: number) => void;
  setWsConnected: (connected: boolean) => void;
  clearLiveEvents: () => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  liveEvents: [],
  alerts: [],
  recentEvents: [],
  occupancy: { current: 0, total: 200 },
  wsConnected: false,

  addLiveEvent: (event) =>
    set((state) => ({
      liveEvents: [event, ...state.liveEvents].slice(0, 50),
    })),

  addAlert: (alert) =>
    set((state) => ({ alerts: [alert, ...state.alerts] })),

  setOccupancy: (current, total) =>
    set({ occupancy: { current, total } }),

  setWsConnected: (connected) => set({ wsConnected: connected }),

  clearLiveEvents: () => set({ liveEvents: [] }),
}));
