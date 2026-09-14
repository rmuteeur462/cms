import { Platform } from 'react-native';
import Constants from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Current machine Wi-Fi IPv4 address
export const DEFAULT_DEV_MACHINE_IP = '192.168.100.2';
const CUSTOM_SERVER_STORAGE_KEY = '@wssp_cms_custom_server_url';

let inMemoryCustomBaseUrl: string | null = null;

// Initialize custom URL from storage if previously saved
//fastuniversity577@gmail.com
AsyncStorage.getItem(CUSTOM_SERVER_STORAGE_KEY)
  .then((saved) => {
    if (saved && saved.trim().startsWith('http')) {
      inMemoryCustomBaseUrl = saved.trim().replace(/\/+$/, '');
    }
  })
  .catch(() => { });

const isIpv4 = (host: string): boolean => {
  return /^(\d{1,3}\.){3}\d{1,3}$/.test(host);
};

export const getAutoDetectedBaseUrl = (): string => {
  // In development on Chrome / Web, use 127.0.0.1
  if (Platform.OS === 'web') {
    return 'http://127.0.0.1:8000';
  }

  // Detect Expo Metro bundler host IP when running in Expo Go
  const hostUri =
    Constants.expoConfig?.hostUri ||
    (Constants as any)?.manifest2?.extra?.expoClient?.hostUri ||
    (Constants as any)?.manifest?.debuggerHost;

  if (hostUri) {
    const host = hostUri.split(':')[0];
    // ONLY use host if it's a valid local IPv4 address (not a tunnel domain like *.exp.direct or *.ngrok.io)
    if (host && isIpv4(host) && host !== 'localhost' && host !== '127.0.0.1') {
      return `http://${host}:8000`;
    }
  }

  // Active Wi-Fi IPv4 address of development machine
  return `http://${DEFAULT_DEV_MACHINE_IP}:8000`;
};

const getBaseUrl = (): string => {
  if (inMemoryCustomBaseUrl) {
    return inMemoryCustomBaseUrl;
  }
  return getAutoDetectedBaseUrl();
};

export const Config = {
  APP_NAME: 'WSSP CMS Mobile',
  APP_VERSION: '1.0.0 (Phase 4 Foundation)',
  DEPARTMENT_NAME: 'Water & Sanitation Services Peshawar',
  HELPLINE: '1334',

  // API URL
  get BASE_URL(): string {
    return getBaseUrl();
  },

  async setCustomBaseUrl(url: string | null): Promise<void> {
    if (!url || !url.trim()) {
      inMemoryCustomBaseUrl = null;
      await AsyncStorage.removeItem(CUSTOM_SERVER_STORAGE_KEY);
    } else {
      let formatted = url.trim().replace(/\/+$/, '');
      if (!formatted.startsWith('http://') && !formatted.startsWith('https://')) {
        formatted = `http://${formatted}`;
      }
      if (!formatted.includes(':', 7)) {
        formatted = `${formatted}:8000`;
      }
      inMemoryCustomBaseUrl = formatted;
      await AsyncStorage.setItem(CUSTOM_SERVER_STORAGE_KEY, formatted);
    }
  },

  getAutoDetectedBaseUrl,

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
