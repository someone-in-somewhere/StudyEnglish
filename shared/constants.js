/**
 * Shared constants for Study English app
 * Can be used by both web frontend and potentially React Native
 */

export const APP_CONFIG = {
  name: 'Study English',
  version: '1.0.0',
};

// CEFR Levels
export const CEFR_LEVELS = {
  A1: { name: 'Beginner', color: '#22C55E' },
  A2: { name: 'Elementary', color: '#84CC16' },
  B1: { name: 'Intermediate', color: '#EAB308' },
  B2: { name: 'Upper Intermediate', color: '#F97316' },
  C1: { name: 'Advanced', color: '#EF4444' },
  C2: { name: 'Proficiency', color: '#8B5CF6' },
};

// Topics
export const TOPICS = {
  essential: ['greetings', 'numbers', 'time', 'colors'],
  daily_life: ['food', 'shopping', 'home', 'health'],
  professional: ['business', 'technology', 'education', 'work'],
  general: ['nature', 'weather', 'travel', 'sports'],
  culture: ['music', 'movies', 'art', 'literature'],
  specialized: ['science', 'medicine', 'law'],
};

// Quiz Types
export const QUIZ_TYPES = {
  MULTIPLE_CHOICE: 'multiple_choice',
  FILL_IN_BLANK: 'fill_in_blank',
  MATCHING: 'matching',
};

// Exercise Types
export const EXERCISE_TYPES = {
  FILL_IN_BLANK: 'fill_in_blank',
  REWRITING: 'rewriting',
  TRANSLATION: 'translation',
  WORD_ORDER: 'word_order',
  ERROR_CORRECTION: 'error_correction',
};

// SRS Intervals (SM-2 algorithm)
export const SRS_INTERVALS = {
  AGAIN: 1,      // 1 minute
  HARD: 6,       // 6 minutes
  GOOD: 10,      // 10 minutes
  EASY: 4320,    // 3 days in minutes
};

// API Endpoints
export const API_ENDPOINTS = {
  VOCABULARY: '/api/vocabulary',
  QUIZ: '/api/quiz',
  TRANSLATION: '/api/translation',
  CHAT: '/api/chat',
  READING: '/api/reading',
  WRITING: '/api/writing',
  FLASHCARDS: '/api/flashcards',
  SRS: '/api/srs',
  PROGRESS: '/api/progress',
  EXERCISES: '/api/exercises',
  LEARNING_PATHS: '/api/learning-paths',
};

// Colors (matching Tailwind)
export const COLORS = {
  primary: '#3B82F6',
  primaryDark: '#2563EB',
  secondary: '#10B981',
  success: '#22C55E',
  warning: '#F59E0B',
  error: '#EF4444',
  background: '#F8FAFC',
  surface: '#FFFFFF',
  textPrimary: '#1E293B',
  textSecondary: '#64748B',
};
