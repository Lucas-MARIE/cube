// ============================================================
// Cube.com Frontend - User Service API
// Handles user authentication, profile, and statistics requests.
// ============================================================

import api from "./api";
import type {
  User,
  LoginCredentials,
  RegisterPayload,
  Stats,
} from "../types";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const userService = {
  /**
   * Authenticate a user and store JWT token.
   */
  login: async (email: string, password: string) => {
    const res = await api.post<TokenResponse>("/users/v1/auth/login", { email, password });
    if (res.data?.access_token) {
      localStorage.setItem("access_token", res.data.access_token);
    }
    return res;
  },

  /**
   * Register a new user and automatically log them in.
   */
  register: async (payload: RegisterPayload) => {
    // 1. Create account
    await api.post<User>("/users/v1/auth/register", payload);
    // 2. Obtain JWT token
    const loginRes = await api.post<TokenResponse>("/users/v1/auth/login", {
      email: payload.email,
      password: payload.password,
    });
    if (loginRes.data?.access_token) {
      localStorage.setItem("access_token", loginRes.data.access_token);
    }
    return loginRes;
  },

  /**
   * Fetch current authenticated user profile.
   */
  getProfile: () => api.get<User>("/users/v1/users/me"),

  /**
   * Fetch user solving stats (PB, AO5, AO12, total solves).
   */
  getStats: () => api.get<Stats>("/users/v1/stats/me/stats"),

  /**
   * Record a new solve time.
   */
  recordSolve: (time_ms: number, scramble: string) =>
    api.post("/users/v1/stats/me/solves", { time_ms, scramble }),

  /**
   * Fetch unlocked achievements.
   */
  getAchievements: () => api.get("/users/v1/stats/me/achievements"),

  /**
   * Log out user and redirect to login.
   */
  logout: () => {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  },
};

// Also export standalone functions for backward compatibility
export const login = (creds: LoginCredentials) => userService.login(creds.email, creds.password);
export const register = (payload: RegisterPayload) => userService.register(payload);
export const getProfile = () => userService.getProfile().then((res) => res.data);
export const getStats = () => userService.getStats().then((res) => res.data);
export const logout = userService.logout;

export default userService;
