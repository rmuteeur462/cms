import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { StorageService } from '../services/storage';
import { Config } from '../constants/config';
import { AuthApi, UserProfile, CitizenRegisterPayload } from '../api/auth';
import { setSessionExpiredHandler } from '../api/client';

interface LoginResult {
  success: boolean;
  error?: string;
  token?: string;
  user?: UserProfile;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isLoading: boolean;
  isInitialLoading: boolean;
  login: (username: string, password: string, autoCommit?: boolean) => Promise<LoginResult>;
  loginCitizen: (mobileNumber: string, password: string, autoCommit?: boolean) => Promise<LoginResult>;
  registerCitizen: (payload: CitizenRegisterPayload) => Promise<{ success: boolean; message?: string; error?: string }>;
  commitSession: (token: string, user: UserProfile) => void;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isInitialLoading, setIsInitialLoading] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Listen for session expiry from API interceptor
  useEffect(() => {
    setSessionExpiredHandler(() => {
      setToken(null);
      setUser(null);
    });
    return () => {
      setSessionExpiredHandler(null);
    };
  }, []);

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
            const isCitizen = savedUser.account_type === 'citizen' || (!savedUser.is_staff && !savedUser.is_superuser);
            const liveProfile = isCitizen ? await AuthApi.getCitizenProfile() : await AuthApi.getProfile();
            setUser(liveProfile);
            await StorageService.setItem(Config.STORAGE_KEYS.USER_PROFILE, liveProfile);
          } catch (verifyErr: any) {
            console.warn('[AuthContext] Background profile verify failed:', verifyErr);
            if (verifyErr?.response?.status === 401) {
              await StorageService.removeItem(Config.STORAGE_KEYS.ACCESS_TOKEN);
              await StorageService.removeItem(Config.STORAGE_KEYS.REFRESH_TOKEN);
              await StorageService.removeItem(Config.STORAGE_KEYS.USER_PROFILE);
              setToken(null);
              setUser(null);
            }
          }
        }
      } catch (err) {
        console.error('[AuthContext] Initialization error:', err);
      } finally {
        setIsInitialLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const commitSession = (sessionToken: string, sessionUser: UserProfile) => {
    setToken(sessionToken);
    setUser(sessionUser);
  };

  const login = async (
    username: string,
    password: string,
    autoCommit = false
  ): Promise<LoginResult> => {
    setIsLoading(true);
    try {
      const response = await AuthApi.login(username, password);

      // Save tokens and profile to persistent storage
      await StorageService.setItem(Config.STORAGE_KEYS.ACCESS_TOKEN, response.access);
      await StorageService.setItem(Config.STORAGE_KEYS.REFRESH_TOKEN, response.refresh);
      await StorageService.setItem(Config.STORAGE_KEYS.USER_PROFILE, response.user);
      await StorageService.setItem(Config.STORAGE_KEYS.SAVED_USERNAME, username);

      if (autoCommit) {
        // Brief pause to allow the animated logo transition to display smoothly
        await new Promise((resolve) => setTimeout(resolve, 1400));
        setToken(response.access);
        setUser(response.user);
      }

      return {
        success: true,
        token: response.access,
        user: response.user,
      };
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

  const loginCitizen = async (
    mobileNumber: string,
    password: string,
    autoCommit = false
  ): Promise<LoginResult> => {
    setIsLoading(true);
    try {
      const response = await AuthApi.loginCitizen(mobileNumber, password);

      await StorageService.setItem(Config.STORAGE_KEYS.ACCESS_TOKEN, response.access);
      await StorageService.setItem(Config.STORAGE_KEYS.REFRESH_TOKEN, response.refresh);
      await StorageService.setItem(Config.STORAGE_KEYS.USER_PROFILE, response.user);
      await StorageService.setItem(Config.STORAGE_KEYS.SAVED_USERNAME, mobileNumber);

      if (autoCommit) {
        await new Promise((resolve) => setTimeout(resolve, 1400));
        setToken(response.access);
        setUser(response.user);
      }

      return {
        success: true,
        token: response.access,
        user: response.user,
      };
    } catch (err: any) {
      let message = 'Login failed. Please check your credentials.';
      if (err.response?.data?.errors) {
        const errors = err.response.data.errors;
        const firstKey = Object.keys(errors)[0];
        message = Array.isArray(errors[firstKey]) ? errors[firstKey][0] : errors[firstKey];
      } else if (err.response?.data?.message) {
        message = err.response.data.message;
      } else if (err.response?.data?.detail) {
        message = err.response.data.detail;
      } else if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error') || !err.response) {
        message = `Cannot reach WSSP backend at ${Config.BASE_URL}. Ensure Django server is running.`;
      } else if (err.message) {
        message = err.message;
      }
      return { success: false, error: message };
    } finally {
      setIsLoading(false);
    }
  };

  const registerCitizen = async (
    payload: CitizenRegisterPayload
  ): Promise<{ success: boolean; message?: string; error?: string }> => {
    setIsLoading(true);
    try {
      const response = await AuthApi.registerCitizen(payload);
      return {
        success: response.success,
        message: response.message || 'Account created successfully! Please log in.',
      };
    } catch (err: any) {
      let message = 'Registration failed. Please check the form.';
      if (err.response?.data?.errors) {
        const errors = err.response.data.errors;
        const firstKey = Object.keys(errors)[0];
        message = Array.isArray(errors[firstKey]) ? errors[firstKey][0] : errors[firstKey];
      } else if (err.response?.data?.message) {
        message = err.response.data.message;
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
        isInitialLoading,
        login,
        loginCitizen,
        registerCitizen,
        commitSession,
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
