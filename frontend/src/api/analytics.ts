import apiClient from "./client";

export interface AnalyticsOccupancy { current: number; total: number; percentage: number }
export interface RevenueData { date: string; amount: number; category: string }
export interface PeakHour { hour: number; day: number; count: number }
export interface TopVehicle { plate: string; visits: number; last_seen: string }
export interface DecisionBreakdown { allow: number; deny: number; alert: number }

export const analyticsApi = {
  occupancy: () => apiClient.get<AnalyticsOccupancy>("/api/analytics/occupancy"),
  revenue: (params?: { from?: string; to?: string }) => apiClient.get<RevenueData[]>("/api/analytics/revenue", { params }),
  peakHours: () => apiClient.get<PeakHour[]>("/api/analytics/peak-hours"),
  topVehicles: () => apiClient.get<TopVehicle[]>("/api/analytics/top-vehicles"),
  decisions: () => apiClient.get<DecisionBreakdown>("/api/analytics/decisions"),
};
