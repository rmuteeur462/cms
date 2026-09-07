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
  is_superuser: boolean;
  is_staff: boolean;
  role: string;
  has_cms_access: boolean;
  allowed_locations: AllowedLocation[];
  allowed_location_count: number;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: UserProfile;
  message?: string;
}

export const AuthApi = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/api/cms/auth/login/', {
      username,
      password,
    });
    return response.data;
  },

  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<{ user: UserProfile }>('/api/cms/auth/me/');
    return response.data.user;
  },

  async testSecurity(): Promise<any> {
    const response = await apiClient.get('/api/cms/auth/test-security/');
    return response.data;
  }
};
