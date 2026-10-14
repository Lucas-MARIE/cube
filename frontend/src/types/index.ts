// ============================================================
// Cube.com Frontend - TypeScript Interfaces
// Shared type definitions used across the application.
// ============================================================

/** User account information */
export interface User {
  id: string;
  username: string;
  email: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

/** Authentication credentials for login */
export interface LoginCredentials {
  email: string;
  password: string;
}

/** Registration payload for new users */
export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

/** JWT authentication response */
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/** A Rubik's Cube solving lesson */
export interface Lesson {
  id: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  category: string;
  steps: LessonStep[];
  created_at: string;
}

/** A single step within a lesson */
export interface LessonStep {
  order: number;
  title: string;
  description: string;
  algorithm?: string;
  image_url?: string;
}

/** A Rubik's Cube algorithm (e.g., OLL, PLL) */
export interface Algorithm {
  id: string;
  name: string;
  category: string;
  notation: string;
  description: string;
  image_url?: string;
}

/** A timed solving session */
export interface Session {
  id: string;
  user_id: string;
  scramble: string;
  start_time: string;
  end_time?: string;
  duration_ms?: number;
  penalty?: "none" | "+2" | "DNF";
  created_at: string;
}

/** User statistics summary */
export interface Stats {
  total_solves: number;
  best_time_ms: number;
  average_time_ms: number;
  ao5: number | null;    // Average of 5
  ao12: number | null;   // Average of 12
  ao100: number | null;  // Average of 100
}

/** A competitive match between users */
export interface Match {
  id: string;
  players: string[];
  scramble: string;
  results: MatchResult[];
  status: "waiting" | "in_progress" | "completed";
  created_at: string;
}

/** Individual result within a match */
export interface MatchResult {
  user_id: string;
  duration_ms: number;
  penalty?: "none" | "+2" | "DNF";
}
