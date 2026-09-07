import { apiClient } from './client';

export interface ComplaintSummaryItem {
  id: number;
  complaint_no: string;
  title: string;
  category: string;
  subtype: string | null;
  citizen_name: string;
  cell_number: string;
  location: string;
  uc: string;
  area: string;
  date: string | null;
  status: 'pending' | 'resolved' | string;
  before_image: string | null;
}

export interface DashboardMetrics {
  total: number;
  pending: number;
  resolved: number;
  today: number;
}

export interface DistributionItem {
  category?: string;
  zone?: string;
  count: number;
}

export interface DashboardData {
  metrics: DashboardMetrics;
  recent_complaints: ComplaintSummaryItem[];
  type_distribution: { category: string; count: number }[];
  zone_distribution: { zone: string; count: number }[];
}

export interface ComplaintListResponse {
  total_count: number;
  num_pages: number;
  current_page: number;
  has_next: boolean;
  has_previous: boolean;
  results: ComplaintSummaryItem[];
}

export const ComplaintsApi = {
  async getDashboard(): Promise<DashboardData> {
    const response = await apiClient.get<DashboardData>('/api/cms/dashboard/');
    return response.data;
  },

  async getComplaints(params?: {
    search?: string;
    status?: string;
    location_id?: number;
    page?: number;
  }): Promise<ComplaintListResponse> {
    const response = await apiClient.get<ComplaintListResponse>('/api/cms/complaints/', {
      params,
    });
    return response.data;
  },

  async getComplaintDetail(id: number): Promise<any> {
    const response = await apiClient.get(`/api/cms/complaints/${id}/`);
    return response.data;
  }
};
