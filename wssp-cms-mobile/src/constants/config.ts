import { Platform } from 'react-native';

/**
 * Global Configuration for WSSP CMS Mobile
 * Handles environment-specific API hosts across Web, Android Emulator, and Physical Devices (Expo Go).
 */

const getBaseUrl = (): string => {
  // In development, web runs on localhost:8000
  if (Platform.OS === 'web') {
    return 'http://127.0.0.1:8000';
  }
  // Android Emulator standard loopback is 10.0.2.2
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }
  // Default to localhost
  return 'http://127.0.0.1:8000';
};

export const Config = {
  APP_NAME: 'WSSP CMS Mobile',
  APP_VERSION: '1.0.0 (Phase 4 Foundation)',
  DEPARTMENT_NAME: 'Water & Sanitation Services Peshawar',
  HELPLINE: '1334',
  
  // API URL
  BASE_URL: getBaseUrl(),
  API_PREFIX: '/api',

  // Storage Keys
  STORAGE_KEYS: {
    ACCESS_TOKEN: '@wssp_cms_access_token',
    REFRESH_TOKEN: '@wssp_cms_refresh_token',
    USER_PROFILE: '@wssp_cms_user_profile',
    SAVED_USERNAME: '@wssp_cms_saved_username',
  },

  // Request Timeouts
  TIMEOUT_MS: 15000,
};
