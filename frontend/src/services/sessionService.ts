// ============================================================
// Cube.com Frontend - Session Service API
// Handles solve sessions, timer tracking, and live matchmaking.
// ============================================================

import api from "./api";
import type { Session } from "../types";

export interface SoloSessionStartResponse {
  session_id: string;
  user_id: string;
  scramble: string;
  started_at: number;
}

export interface SoloSessionEndResponse {
  session_id: string;
  user_id: string;
  solve_time_ms: number;
  scramble: string;
  message: string;
}

export const sessionService = {
  /**
   * Start a new solving session with a given scramble and user ID.
   */
  startSession: (userId: string, scramble: string) =>
    api.post<SoloSessionStartResponse>("/sessions/solo/start", { user_id: userId, scramble }),

  /**
   * End an active session by recording the solve time.
   */
  endSession: (sessionId: string, solveTimeMs: number) =>
    api.post<SoloSessionEndResponse>("/sessions/solo/end", {
      session_id: sessionId,
      solve_time_ms: solveTimeMs,
    }),

  /**
   * Join ranked matchmaking queue.
   */
  joinMatchmaking: (userId: string, rating: number = 1200) =>
    api.post("/sessions/matchmaking/join", { user_id: userId, rating }),

  /**
   * Leave matchmaking queue.
   */
  leaveMatchmaking: (userId: string) =>
    api.delete(`/sessions/matchmaking/leave?user_id=${userId}`),
};

export default sessionService;
