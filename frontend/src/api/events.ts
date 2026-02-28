import apiClient from "./client";

export interface ParkingEvent {
  id: string;
  plate: string;
  gate_id: string;
  camera_id?: string;
  event_type: "entry" | "exit" | "detection";
  ocr_confidence?: number;
  decision?: "allow" | "deny" | "alert";
  rule_applied?: string;
  image_url?: string;
  timestamp: string;
}

export const eventsApi = {
  list: (params?: Record<string, string>) => apiClient.get<ParkingEvent[]>("/api/events", { params }),
  get: (id: string) => apiClient.get<ParkingEvent>(`/api/events/${id}`),
};
