import apiClient from "./client";

export interface LoginPayload { username: string; password: string }
export interface AuthResponse { access_token: string; token_type: string }
export interface UserProfile { id: string; username: string; full_name: string; role: string; email: string }

export const authApi = {
  login: (data: LoginPayload) => {
    const params = new URLSearchParams();
    params.append("username", data.username);
    params.append("password", data.password);
    return apiClient.post<AuthResponse>("/api/auth/login", params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  logout: () => apiClient.post("/api/auth/logout"),
  me: () => apiClient.get<UserProfile>("/api/auth/me"),
  refresh: () => apiClient.post<AuthResponse>("/api/auth/refresh"),
};
