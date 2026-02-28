import apiClient from "./client";

export interface ParkingAlert {
  id: string;
  alert_type: "BLACKLIST" | "OVERSTAY" | "DUPLICATE_PLATE" | "LOW_CONFIDENCE" | "FRAUD" | "REVENUE_ANOMALY";
  severity: "critical" | "high" | "medium" | "low";
  plate?: string;
  gate_id?: string;
  message: string;
  resolved: boolean;
  resolved_by?: string;
  resolved_at?: string;
  created_at: string;
}

export const alertsApi = {
  list: () => apiClient.get<ParkingAlert[]>("/api/alerts"),
  resolve: (id: string) => apiClient.put(`/api/alerts/${id}/resolve`),
  history: () => apiClient.get<ParkingAlert[]>("/api/alerts/history"),
};
