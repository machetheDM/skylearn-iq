/**
 * SKYLearn IQ — Expo 52 Learner Mobile App  (Phase 2 — COMPLETE)
 * ==============================================================
 * Purpose  : React Native mobile app for learners to take assessments,
 *            view results, and receive AI/tutor feedback.
 * Run      : npx expo start  (from learner-app/)  → press 'a' for Android emulator
 * Auth     : phone + password login → JWT stored in AsyncStorage
 *
 * Key screens
 *   (tabs)/index.tsx          — dashboard: stats, in-progress banner, recent results
 *   (tabs)/assessments.tsx    — list published assessments
 *   app/assessment/[id].tsx   — take assessment: MCQ + short-answer, timer
 *   app/assessment/result/    — score hero, answer breakdown, AI feedback
 *
 * API_URL notes
 *   Android emulator  → 10.0.2.2:8001
 *   Physical device   → your LAN IP, e.g. 192.168.1.x:8001  ← CHANGE THIS
 *   iOS simulator     → localhost:8001
 *
 * See CONTEXT.md at the project root for full architecture and phase progress.
 */
export const API_URL = "http://10.0.2.2:8001";
