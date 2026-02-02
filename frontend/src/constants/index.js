/**
 * Constants for the frontend application
 */

// API Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
};

// User Roles
export const USER_ROLES = {
  FAMILY_MEMBER: 'family_member',
  POLICE_OFFICER: 'police_officer',
  GOVERNMENT_OFFICIAL: 'government_official',
  MORGUE_STAFF: 'morgue_staff',
  ADMIN: 'admin',
};

// Missing Person Status
export const MISSING_PERSON_STATUS = {
  REPORTED: 'reported',
  SEARCHING: 'searching',
  FOUND: 'found',
  CLOSED: 'closed',
};

// Match Status
export const MATCH_STATUS = {
  PENDING_REVIEW: 'pending_review',
  VERIFIED: 'verified',
  FALSE_POSITIVE: 'false_positive',
};

// Processing Status
export const PROCESSING_STATUS = {
  QUEUED: 'queued',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

// Priority Levels
export const PRIORITY_LEVELS = {
  LOW: 'low',
  NORMAL: 'normal',
  HIGH: 'high',
  URGENT: 'urgent',
};

// Notification Types
export const NOTIFICATION_TYPES = {
  MATCH_FOUND: 'match_found',
  PROCESSING_COMPLETE: 'processing_complete',
  VERIFICATION_REQUIRED: 'verification_required',
  STATUS_UPDATE: 'status_update',
  SYSTEM_ALERT: 'system_alert',
};

// Notification Delivery Channels
export const NOTIFICATION_CHANNELS = {
  IN_APP: 'in_app',
  EMAIL: 'email',
  SMS: 'sms',
  PUSH: 'push',
};

// Gender Options
export const GENDER_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
];

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/token/',
    REGISTER: '/auth/users/',
    ME: '/auth/users/me/',
    CHANGE_PASSWORD: '/auth/users/change_password/',
    REFRESH_TOKEN: '/auth/token/refresh/',
  },
  MISSING_PERSONS: {
    LIST: '/facial-recognition/missing-persons/',
    CREATE: '/facial-recognition/missing-persons/',
    DETAIL: (id) => `/facial-recognition/missing-persons/${id}/`,
    UPLOAD_IMAGE: (id) => `/facial-recognition/missing-persons/${id}/upload_image/`,
  },
  MATCHES: {
    LIST: '/facial-recognition/matches/',
    VERIFY: (id) => `/facial-recognition/matches/${id}/verify/`,
    REJECT: (id) => `/facial-recognition/matches/${id}/reject/`,
  },
  QUEUE: {
    LIST: '/facial-recognition/processing-queue/',
  },
  NOTIFICATIONS: {
    LIST: '/notifications/notifications/',
    MARK_READ: (id) => `/notifications/notifications/${id}/mark_as_read/`,
    MARK_ALL_READ: '/notifications/notifications/mark_all_as_read/',
    PREFERENCES: '/notifications/preferences/my_preferences/',
  },
  HEALTH: {
    CHECK: '/health/check/',
  },
};

// Form Validation Rules
export const VALIDATION_RULES = {
  USERNAME: {
    min: 3,
    max: 150,
    pattern: /^[a-zA-Z0-9_-]+$/,
  },
  PASSWORD: {
    min: 8,
    max: 128,
  },
  EMAIL: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  PHONE: {
    pattern: /^\d{10,15}$/,
  },
};

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
};

// Cache Duration (in milliseconds)
export const CACHE_DURATION = {
  SHORT: 5 * 60 * 1000, // 5 minutes
  MEDIUM: 15 * 60 * 1000, // 15 minutes
  LONG: 60 * 60 * 1000, // 1 hour
};

// UI Constants
export const UI = {
  ANIMATION_DURATION: 300,
  TOAST_DURATION: 3000,
  MODAL_ANIMATION_DURATION: 200,
};
