// ============================================================
// Cube.com Frontend - Lesson Service API
// Handles lesson, algorithm, and scramble-related requests.
// ============================================================

import api from "./api";
import type { Lesson, Algorithm } from "../types";

export interface ScrambleResponse {
  scramble: string;
  length: number;
  case?: string;
}

export const lessonService = {
  /**
   * Fetch all lessons with optional category filter.
   */
  getLessons: (category?: string) => {
    const params = category && category !== "ALL" ? { category } : {};
    return api.get<Lesson[]>("/lessons/lessons", { params });
  },

  /**
   * Fetch a single lesson by ID.
   */
  getLesson: (lessonId: string) => api.get<Lesson>(`/lessons/lessons/${lessonId}`),

  /**
   * Fetch CFOP algorithms (F2L, OLL, PLL).
   */
  getAlgorithms: (category?: string) => {
    const params = category && category !== "ALL" ? { category } : {};
    return api.get<Algorithm[]>("/lessons/algorithms", { params });
  },

  /**
   * Request a random official WCA scramble.
   */
  getRandomScramble: (length: number = 20) =>
    api.get<ScrambleResponse>("/lessons/scrambles/random", { params: { length } }),

  /**
   * Request a targeted scramble for a specific case (e.g. t-perm, sune).
   */
  getTargetedScramble: (caseName: string) =>
    api.get<ScrambleResponse>("/lessons/scrambles/targeted", { params: { case: caseName } }),
};

// Also export standalone functions for backward compatibility
export const getLessons = (category?: string) => lessonService.getLessons(category).then((res) => res.data);
export const getLesson = (id: string) => lessonService.getLesson(id).then((res) => res.data);
export const getAlgorithms = (category?: string) => lessonService.getAlgorithms(category).then((res) => res.data);
export const getScramble = () => lessonService.getRandomScramble().then((res) => res.data.scramble);

export default lessonService;
