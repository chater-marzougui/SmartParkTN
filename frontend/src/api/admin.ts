import apiClient from "./client";

export interface Rule { key: string; value: unknown; description: string; updated_at: string }
export interface Tariff {
  id: string;
  name: string;
  vehicle_types: string[];
  first_hour_tnd: number;
  extra_hour_tnd: number;
  daily_max_tnd: number;
  night_multiplier: number;
  night_start: string;
  night_end: string;
  weekend_multiplier: number;
  valid_from?: string;
  valid_until?: string;
  active: boolean;
}

export const rulesApi = {
  list: () => apiClient.get<Rule[]>("/api/rules"),
  update: (key: string, value: unknown) => apiClient.put(`/api/rules/${key}`, { value }),
  history: (key: string) => apiClient.get(`/api/rules/${key}/history`),
};

export const tariffsApi = {
  list: () => apiClient.get<Tariff[]>("/api/tariffs"),
  create: (data: Partial<Tariff>) => apiClient.post<Tariff>("/api/tariffs", data),
  update: (id: string, data: Partial<Tariff>) => apiClient.put<Tariff>(`/api/tariffs/${id}`, data),
  delete: (id: string) => apiClient.delete(`/api/tariffs/${id}`),
  simulate: (duration: number, vehicleType: string) =>
    apiClient.get(`/api/tariffs/simulate?duration=${duration}&vehicle_type=${vehicleType}`),
};
