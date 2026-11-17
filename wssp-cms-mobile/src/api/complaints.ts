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

export interface AnalyticsPeriod {
  year: number | null;
  month: number | null;
  start_date: string;
  end_date: string;
  label: string;
  period_type: 'year' | 'month' | 'custom';
}

export interface AnalyticsScope {
  role: 'head_office' | 'zonal_manager' | 'department_manager' | 'staff';
  role_title: string;
  zone: string;
  department: string;
  is_single_department: boolean;
}

export interface AnalyticsSummary {
  total: number;
  pending: number;
  in_progress: number;
  resolved: number;
  registered_this_period: number;
}

export interface StatusDistributionItem {
  status: string;
  label: string;
  count: number;
  percentage: number;
  color: string;
}

export interface TypeDistributionItem {
  id: number;
  name: string;
  count: number;
  percentage: number;
}

export interface SubtypeDistributionItem {
  id: number | null;
  name: string;
  count: number;
  percentage: number;
}

export interface TrendItem {
  date?: string;
  month?: number;
  year?: number;
  label: string;
  full_label?: string;
  count: number;
  resolved?: number;
  pending?: number;
  resolved_percentage?: number;
  pending_percentage?: number;
}

export interface DashboardAnalyticsResponse {
  success: boolean;
  period: AnalyticsPeriod;
  scope: AnalyticsScope;
  summary: AnalyticsSummary;
  status_distribution: StatusDistributionItem[];
  type_distribution: TypeDistributionItem[];
  subtype_distribution: SubtypeDistributionItem[];
  trend: TrendItem[];
}

export interface ComplaintListResponse {
  total_count: number;
  resolved_count?: number;
  pending_count?: number;
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

  async getDashboardAnalytics(params?: {
    year?: number | 'all' | string;
    month?: number;
    start_date?: string;
    end_date?: string;
    location_id?: number;
  }): Promise<DashboardAnalyticsResponse> {
    const response = await apiClient.get<DashboardAnalyticsResponse>('/api/cms/v1/dashboard/analytics/', {
      params,
    });
    return response.data;
  },


  async getComplaints(params?: {
    search?: string;
    status?: string;
    location_id?: number;
    year?: number | string;
    month?: number;
    start_date?: string;
    end_date?: string;
    category_id?: number;
    subtype_id?: number;
    category?: string;
    subtype?: string;
    page?: number;
    page_size?: number;
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

export interface CitizenComplaintItem {
  id: number;
  complaint_no: string;
  title: string;
  category: string;
  subcategory: string | null;
  location_name: string;
  uc_name: string | null;
  area: string;
  address: string;
  complaint_detail: string;
  status: 'pending' | 'resolved' | string;
  date: string | null;
  before_image_url: string | null;
  created_at: string;
  has_feedback?: boolean;
}

export interface CitizenComplaintDetail extends CitizenComplaintItem {
  updated_at: string;
  resolution?: {
    description: string;
    customer_satisfaction: string;
    after_image_url: string | null;
  } | null;
  feedbacks: {
    id: number;
    happy: boolean;
    complaint_feedback: string;
    created_at: string;
  }[];
  can_give_feedback: boolean;
}

export interface CitizenTimelineStep {
  step: number;
  key: string;
  title: string;
  subtitle: string;
  timestamp: string | null;
  status: 'completed' | 'in_progress' | 'pending' | 'available' | 'locked';
  badge: string;
  description: string;
  after_image_url?: string | null;
  feedback_data?: {
    id: number;
    happy: boolean;
    comment: string;
    submitted_at: string;
  } | null;
}

export interface CitizenTrackingResponse {
  success: boolean;
  complaint: {
    id: number;
    complaint_no: string;
    title: string;
    status: string;
    category: string;
    subcategory: string | null;
    location: string;
    uc: string | null;
    area: string;
    address: string;
    complaint_detail: string;
    before_image_url: string | null;
    created_at: string;
    updated_at: string;
  };
  timeline: CitizenTimelineStep[];
  can_give_feedback: boolean;
  feedback_given: boolean;
}

export interface CitizenDashboardData {
  success: boolean;
  citizen: {
    full_name: string;
    mobile_number: string;
    email: string;
    address: string;
  };
  metrics: {
    total: number;
    pending: number;
    resolved: number;
  };
  recent_complaints: CitizenComplaintItem[];
  contacts: {
    helpline: string;
    landline: string;
    email: string;
    website: string;
  };
}

export interface CitizenTypeItem {
  id: number;
  type_name: string;
}

export interface CitizenSubtypeItem {
  id: number;
  type_name: string;
  complaint_type: number;
}

export interface CitizenLocationItem {
  id: number;
  location_name: string;
}

export interface CitizenUCItem {
  id: number;
  uc_name: string;
  location: number;
}

export const CitizenComplaintsApi = {
  async getDashboard(): Promise<CitizenDashboardData> {
    const res = await apiClient.get<CitizenDashboardData>('/api/citizen/v1/dashboard/');
    return res.data;
  },

  async getComplaints(params?: { status?: string; q?: string; page?: number }): Promise<{
    count: number;
    next: string | null;
    previous: string | null;
    results: CitizenComplaintItem[];
  }> {
    const res = await apiClient.get('/api/citizen/v1/complaints/', { params });
    return res.data;
  },

  async getComplaintDetail(id: number): Promise<CitizenComplaintDetail> {
    const res = await apiClient.get<{ success: boolean; data: CitizenComplaintDetail }>(
      `/api/citizen/v1/complaints/${id}/`
    );
    return res.data.data;
  },

  async getComplaintTracking(id: number): Promise<CitizenTrackingResponse> {
    const res = await apiClient.get<CitizenTrackingResponse>(
      `/api/citizen/v1/complaints/${id}/tracking/`
    );
    return res.data;
  },

  async submitComplaint(formData: FormData): Promise<{
    success: boolean;
    message: string;
    data: CitizenComplaintItem;
  }> {
    const res = await apiClient.post('/api/citizen/v1/complaints/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  async submitFeedback(
    complaintId: number,
    payload: { happy: boolean; complaint_feedback?: string }
  ): Promise<{ success: boolean; message: string; data: any }> {
    const res = await apiClient.post(
      `/api/citizen/v1/complaints/${complaintId}/feedback/`,
      payload
    );
    return res.data;
  },

  async getComplaintTypes(): Promise<CitizenTypeItem[]> {
    const res = await apiClient.get<{ success: boolean; data: CitizenTypeItem[] }>(
      '/api/citizen/v1/complaint-types/'
    );
    return res.data.data;
  },

  async getSubtypes(complaintTypeId?: number): Promise<CitizenSubtypeItem[]> {
    const params = complaintTypeId ? { complaint_type: complaintTypeId } : {};
    const res = await apiClient.get<{ success: boolean; data: CitizenSubtypeItem[] }>(
      '/api/citizen/v1/subtypes/',
      { params }
    );
    return res.data.data;
  },

  async getLocations(): Promise<CitizenLocationItem[]> {
    const res = await apiClient.get<{ success: boolean; data: CitizenLocationItem[] }>(
      '/api/citizen/v1/locations/'
    );
    return res.data.data;
  },

  async getUCs(locationId?: number): Promise<CitizenUCItem[]> {
    const params = locationId ? { location: locationId } : {};
    const res = await apiClient.get<{ success: boolean; data: CitizenUCItem[] }>(
      '/api/citizen/v1/ucs/',
      { params }
    );
    return res.data.data;
  },
};

