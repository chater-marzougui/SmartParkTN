import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { UserProfile } from "../api/auth";
import { authApi } from "../api/auth";

interface AuthState {
  user: UserProfile | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: localStorage.getItem("access_token"),
      isLoading: false,

      login: async (username, password) => {
        set({ isLoading: true });
        const res = await authApi.login({ username, password });
        const { access_token } = res.data;
        localStorage.setItem("access_token", access_token);
        set({ token: access_token, isLoading: false });
        const meRes = await authApi.me();
        set({ user: meRes.data });
      },

      logout: () => {
        localStorage.removeItem("access_token");
        set({ user: null, token: null });
      },

      fetchMe: async () => {
        const res = await authApi.me();
        set({ user: res.data });
      },
    }),
    { name: "auth-storage", partialize: (s) => ({ token: s.token }) }
  )
);
