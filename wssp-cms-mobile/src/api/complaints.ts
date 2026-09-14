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
  },

  async getComplaintOptions(): Promise<ComplaintOptionsResponse> {
    const response = await apiClient.get<ComplaintOptionsResponse>('/api/cms/complaints/options/');
    return response.data;
  },

  async createComplaint(formData: FormData): Promise<CreateComplaintResponse> {
    const response = await apiClient.post<CreateComplaintResponse>('/api/cms/complaints/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export interface LocationOption {
  id: number;
  name: string;
}

export interface UCOption {
  id: number;
  name: string;
  location_id: number;
}

export interface SourceOption {
  id: number;
  name: string;
}

export interface TypeOption {
  id: number;
  name: string;
}

export interface SubtypeOption {
  id: number;
  name: string;
  type_id: number;
}

export interface ComplaintOptionsResponse {
  locations: LocationOption[];
  ucs: UCOption[];
  sources: SourceOption[];
  types: TypeOption[];
  subtypes: SubtypeOption[];
  genders: { value: string; label: string }[];
  consumer_types: { value: string; label: string }[];
}

export interface CreateComplaintResponse {
  success: boolean;
  message: string;
  complaint: {
    id: number;
    complaint_no: string;
    title: string;
    citizen_name: string;
    cell_number: string;
    location: string;
    uc: string;
    category: string;
    subtype: string | null;
    date: string;
    status: string;
    before_image: string | null;
  };
}

