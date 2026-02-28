import apiClient from "./client";

export interface Vehicle {
  id: string;
  plate: string;
  plate_normalized: string;
  category: "visitor" | "subscriber" | "vip" | "blacklist";
  vehicle_type: "car" | "truck" | "motorcycle" | "bus";
  owner_name?: string;
  owner_phone?: string;
  owner_email?: string;
  subscription_expires?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export const vehiclesApi = {
  list: (params?: Record<string, string>) => apiClient.get<Vehicle[]>("/api/vehicles", { params }),
  get: (id: string) => apiClient.get<Vehicle>(`/api/vehicles/${id}`),
  create: (data: Partial<Vehicle>) => apiClient.post<Vehicle>("/api/vehicles", data),
  update: (id: string, data: Partial<Vehicle>) => apiClient.put<Vehicle>(`/api/vehicles/${id}`, data),
  delete: (id: string) => apiClient.delete(`/api/vehicles/${id}`),
  search: (plate: string) => apiClient.get<Vehicle[]>(`/api/vehicles/search?plate=${plate}`),
  blacklist: (id: string) => apiClient.post(`/api/vehicles/${id}/blacklist`),
  whitelist: (id: string) => apiClient.post(`/api/vehicles/${id}/whitelist`),
};
