// ============================================================
// Cube.com Frontend - User Service API
// Handles user authentication, profile, and statistics requests.
// ============================================================

import api from "./api";
import type {
  User,
  AuthResponse,
  LoginCredentials,
  RegisterPayload,
  Stats,
} from "../types";

/**
 * Log in with email and password.
 * Stores the JWT token in localStorage on success.
 */
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>("/users/login", credentials);
  // Persist the token for subsequent requests
  localStorage.setItem("access_token", response.data.access_token);
  return response.data;
}

/**
 * Register a new user account.
 * Automatically logs in on successful registration.
 */
export async function register(payload: RegisterPayload): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>("/users/register", payload);
  localStorage.setItem("access_token", response.data.access_token);
  return response.data;
}

/**
 * Fetch the authenticated user's profile.
 */
export async function getProfile(): Promise<User> {
  const response = await api.get<User>("/users/profile");
  return response.data;
}

/**
 * Fetch the authenticated user's solving statistics.
 */
export async function getStats(): Promise<Stats> {
  const response = await api.get<Stats>("/users/stats");
  return response.data;
}

/**
 * Log out the current user by clearing the stored token.
 */
export function logout(): void {
  localStorage.removeItem("access_token");
  window.location.href = "/login";
}
