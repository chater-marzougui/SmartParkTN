import { useEffect, useRef, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useDashboardStore } from "../store/dashboardStore";

const WS_URL = import.meta.env.VITE_WS_URL || "http://localhost:8000";

export function useWebSocket() {
  const socketRef = useRef<Socket | null>(null);
  const { addLiveEvent, addAlert, setOccupancy, setWsConnected } = useDashboardStore();

  const connect = useCallback(() => {
    if (socketRef.current?.connected) return;
    const token = localStorage.getItem("access_token");
    socketRef.current = io(WS_URL, {
      auth: { token },
      transports: ["websocket"],
    });

    socketRef.current.on("connect", () => setWsConnected(true));
    socketRef.current.on("disconnect", () => setWsConnected(false));

    socketRef.current.on("gate_event", (data) => addLiveEvent(data));
    socketRef.current.on("new_alert", (data) => addAlert(data));
    socketRef.current.on("occupancy_update", (data) =>
      setOccupancy(data.current, data.total)
    );
  }, [addLiveEvent, addAlert, setOccupancy, setWsConnected]);

  const disconnect = useCallback(() => {
    socketRef.current?.disconnect();
    socketRef.current = null;
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { connected: socketRef.current?.connected ?? false };
}
