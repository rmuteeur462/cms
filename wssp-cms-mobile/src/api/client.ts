import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { Config } from '../constants/config';
import { StorageService } from '../services/storage';

export const apiClient = axios.create({
  baseURL: Config.BASE_URL,
  timeout: Config.TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      const token = await StorageService.getItem<string>(Config.STORAGE_KEYS.ACCESS_TOKEN);
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (err) {
      console.warn('[ApiClient] Failed to attach token:', err);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle Errors & Token Expiration
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // If 401 Unauthorized and not already retried
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await StorageService.getItem<string>(Config.STORAGE_KEYS.REFRESH_TOKEN);
        if (refreshToken) {
          // Request new access token
          const refreshResponse = await axios.post(`${Config.BASE_URL}/api/cms/auth/refresh/`, {
            refresh: refreshToken,
          });

          if (refreshResponse.status === 200 && refreshResponse.data.access) {
            const newAccessToken = refreshResponse.data.access;
            await StorageService.setItem(Config.STORAGE_KEYS.ACCESS_TOKEN, newAccessToken);

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            }
            return apiClient(originalRequest);
          }
        }
      } catch (refreshErr) {
        console.warn('[ApiClient] Token refresh failed. Clearing session...');
        await StorageService.removeItem(Config.STORAGE_KEYS.ACCESS_TOKEN);
        await StorageService.removeItem(Config.STORAGE_KEYS.REFRESH_TOKEN);
        await StorageService.removeItem(Config.STORAGE_KEYS.USER_PROFILE);
      }
    }

    return Promise.reject(error);
  }
);
