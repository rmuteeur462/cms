import { apiClient } from './client';

export interface AllowedLocation {
  id: number;
  name: string;
}

export interface UserProfile {
  id: number;
  username: string;
  full_name: string;
  email: string;
  is_superuser?: boolean;
  is_staff: boolean;
  role: string;
  account_type?: 'citizen' | 'staff';
  mobile_number?: string;
  address?: string;
  has_cms_access?: boolean;
  allowed_locations?: AllowedLocation[];
  allowed_location_count?: number;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: UserProfile;
  message?: string;
}

export interface CitizenRegisterPayload {
  full_name: string;
  mobile_number: string;
  password: string;
  confirm_password: string;
  email?: string;
  address?: string;
}

export interface CitizenRegisterResponse {
  success: boolean;
  message: string;
  data?: {
    user: UserProfile;
  };
  errors?: Record<string, string[] | string>;
}

export const AuthApi = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/api/cms/auth/login/', {
      username,
      password,
    });
    return response.data;
  },

  async loginCitizen(mobile_number: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<{
      success: boolean;
      message: string;
      data: {
        access: string;
        refresh: string;
        user: UserProfile;
      };
    }>('/api/citizen/v1/login/', {
      mobile_number,
      password,
    });
    return {
      access: response.data.data.access,
      refresh: response.data.data.refresh,
      user: {
        ...response.data.data.user,
        account_type: 'citizen',
        is_staff: false,
      },
      message: response.data.message,
    };
  },

  async registerCitizen(payload: CitizenRegisterPayload): Promise<CitizenRegisterResponse> {
    const response = await apiClient.post<CitizenRegisterResponse>('/api/citizen/v1/register/', payload);
    return response.data;
  },

  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<{ user: UserProfile }>('/api/cms/auth/me/');
    return response.data.user;
  },

  async getCitizenProfile(): Promise<UserProfile> {
    const response = await apiClient.get<{ success: boolean; data: any }>('/api/citizen/v1/profile/');
    return {
      ...response.data.data,
      account_type: 'citizen',
      is_staff: false,
      role: 'Citizen',
    };
  },

  async updateCitizenProfile(payload: { full_name?: string; email?: string; address?: string }): Promise<UserProfile> {
    const response = await apiClient.patch<{ success: boolean; data: any }>('/api/citizen/v1/profile/', payload);
    return {
      ...response.data.data,
      account_type: 'citizen',
      is_staff: false,
      role: 'Citizen',
    };
  },

  async testSecurity(): Promise<any> {
    const response = await apiClient.get('/api/cms/auth/test-security/');
    return response.data;
  }
};
