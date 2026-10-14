// ============================================================
// Cube.com Frontend - Axios API Instance
// Centralized HTTP client with base URL config and JWT interceptor.
// ============================================================

import axios from "axios";

// Base API URL from environment variable (set by Vite)
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8080/api";

/**
 * Pre-configured Axios instance for all API calls.
 * - Base URL is set from environment variables.
 * - JWT token is automatically attached to requests.
 * - 401 responses trigger automatic logout.
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 second timeout
});

// --- Request Interceptor: Attach JWT token ---
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- Response Interceptor: Handle auth errors ---
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If we receive a 401, clear stored token and redirect to login
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
