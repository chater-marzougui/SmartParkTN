import apiClient from "./client";

export interface Session {
  id: string;
  plate: string;
  vehicle_id?: string;
  entry_time: string;
  exit_time?: string;
  duration_minutes?: number;
  amount_due?: number;
  payment_status: "pending" | "paid" | "disputed" | "waived";
  gate_entry?: string;
  gate_exit?: string;
  tariff_snapshot?: Record<string, unknown>;
  notes?: string;
  created_at: string;
}

export const sessionsApi = {
  list: (params?: Record<string, string>) => apiClient.get<Session[]>("/api/sessions", { params }),
  get: (id: string) => apiClient.get<Session>(`/api/sessions/${id}`),
  openSessions: () => apiClient.get<Session[]>("/api/sessions/open"),
  close: (id: string) => apiClient.post(`/api/sessions/${id}/close`),
  export: (format: "csv" | "pdf") => apiClient.get(`/api/sessions/export?format=${format}`, { responseType: "blob" }),
};
