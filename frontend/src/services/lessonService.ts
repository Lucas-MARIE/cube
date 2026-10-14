// ============================================================
// Cube.com Frontend - Lesson Service API
// Handles lesson, algorithm, and scramble-related requests.
// ============================================================

import api from "./api";
import type { Lesson, Algorithm } from "../types";

/**
 * Fetch all available lessons, optionally filtered by difficulty.
 */
export async function getLessons(difficulty?: string): Promise<Lesson[]> {
  const params = difficulty ? { difficulty } : {};
  const response = await api.get<Lesson[]>("/lessons/", { params });
  return response.data;
}

/**
 * Fetch a single lesson by its ID.
 */
export async function getLesson(lessonId: string): Promise<Lesson> {
  const response = await api.get<Lesson>(`/lessons/${lessonId}`);
  return response.data;
}

/**
 * Fetch all algorithms, optionally filtered by category (e.g., OLL, PLL).
 */
export async function getAlgorithms(category?: string): Promise<Algorithm[]> {
  const params = category ? { category } : {};
  const response = await api.get<Algorithm[]>("/lessons/algorithms", { params });
  return response.data;
}

/**
 * Request a new random scramble sequence from the server.
 */
export async function getScramble(): Promise<string> {
  const response = await api.get<{ scramble: string }>("/lessons/scramble");
  return response.data.scramble;
}
