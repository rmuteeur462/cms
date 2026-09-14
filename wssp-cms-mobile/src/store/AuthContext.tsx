import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { StorageService } from '../services/storage';
import { Config } from '../constants/config';
import { AuthApi, UserProfile } from '../api/auth';

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initialize Auth State from persistent storage on startup
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const savedToken = await StorageService.getItem<string>(Config.STORAGE_KEYS.ACCESS_TOKEN);
        const savedUser = await StorageService.getItem<UserProfile>(Config.STORAGE_KEYS.USER_PROFILE);

        if (savedToken && savedUser) {
          setToken(savedToken);
          setUser(savedUser);

          // Verify token validity in background
          try {
            const liveProfile = await AuthApi.getProfile();
            setUser(liveProfile);
            await StorageService.setItem(Config.STORAGE_KEYS.USER_PROFILE, liveProfile);
          } catch (verifyErr) {
            console.warn('[AuthContext] Background profile verify failed:', verifyErr);
          }
        }
      } catch (err) {
        console.error('[AuthContext] Initialization error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (username: string, password: string): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    try {
      const response = await AuthApi.login(username, password);

      // Save tokens and profile to persistent storage
      await StorageService.setItem(Config.STORAGE_KEYS.ACCESS_TOKEN, response.access);
      await StorageService.setItem(Config.STORAGE_KEYS.REFRESH_TOKEN, response.refresh);
      await StorageService.setItem(Config.STORAGE_KEYS.USER_PROFILE, response.user);
      await StorageService.setItem(Config.STORAGE_KEYS.SAVED_USERNAME, username);

      setToken(response.access);
      setUser(response.user);

      return { success: true };
    } catch (err: any) {
      let message = 'Login failed. Please check your credentials.';
      if (err.response?.data?.detail) {
        message = err.response.data.detail;
      } else if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error') || !err.response) {
        message = `Cannot reach WSSP backend at ${Config.BASE_URL}. Ensure Django is running with: python manage.py runserver 0.0.0.0:8000 and your phone is on the same Wi-Fi.`;
      } else if (err.message) {
        message = err.message;
      }
      return { success: false, error: message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await StorageService.removeItem(Config.STORAGE_KEYS.ACCESS_TOKEN);
      await StorageService.removeItem(Config.STORAGE_KEYS.REFRESH_TOKEN);
      await StorageService.removeItem(Config.STORAGE_KEYS.USER_PROFILE);
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshProfile = async () => {
    try {
      const updatedProfile = await AuthApi.getProfile();
      setUser(updatedProfile);
      await StorageService.setItem(Config.STORAGE_KEYS.USER_PROFILE, updatedProfile);
    } catch (err) {
      console.warn('[AuthContext] Refresh profile failed:', err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
