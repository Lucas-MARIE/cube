// ============================================================
// Cube.com Frontend - Session Service API
// Handles solve sessions, timer tracking, and history.
// ============================================================

import api from "./api";
import type { Session } from "../types";

/**
 * Start a new solving session with the given scramble.
 * Returns the created session with a server-assigned ID.
 */
export async function startSession(scramble: string): Promise<Session> {
  const response = await api.post<Session>("/sessions/", { scramble });
  return response.data;
}

/**
 * End an active session by recording the solve time and optional penalty.
 */
export async function endSession(
  sessionId: string,
  durationMs: number,
  penalty: "none" | "+2" | "DNF" = "none"
): Promise<Session> {
  const response = await api.put<Session>(`/sessions/${sessionId}`, {
    duration_ms: durationMs,
    penalty,
  });
  return response.data;
}

/**
 * Fetch the user's solve history, with optional pagination.
 */
export async function getHistory(
  page: number = 1,
  limit: number = 20
): Promise<Session[]> {
  const response = await api.get<Session[]>("/sessions/history", {
    params: { page, limit },
  });
  return response.data;
}

/**
 * Delete a specific session from history.
 */
export async function deleteSession(sessionId: string): Promise<void> {
  await api.delete(`/sessions/${sessionId}`);
}
