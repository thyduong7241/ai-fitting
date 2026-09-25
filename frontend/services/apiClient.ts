/**
 * AI Precision Fit - Typed API Client
 * Conforms 100% to OpenAPI 3.1 Specification (docs/api/ai_precision_fit_api.yaml).
 *
 * Features:
 * - Structured error handling with FitAPIError
 * - Automatic X-Session-ID header injection for Zero-Auth Multi-Profile
 * - Idempotency-Key header support for async jobs
 * - Endpoints: /garments, /fit-profiles, /pipeline/quality-check, /pipeline/measure, /pipeline/size-recommend, /tryon/jobs
 */

import {
  Garment,
  GarmentDetail,
  GarmentSizeChart,
  PaginatedResponse,
  GarmentsQueryParams,
  UserProfile,
  CreateFitProfileRequest,
  UpdateFitProfileRequest,
  FitProfilesListResponse,
  QualityCheckRequest,
  QualityCheckResponse,
  MeasurementRequest,
  MeasurementResponse,
  SizeRecommendRequest,
  SizeRecommendResponse,
  CreateTryOnJobRequest,
  TryOnJob,
  APIErrorResponse,
} from '@/types/fitting';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class FitAPIError extends Error {
  code: string;
  status: number;
  details?: unknown;

  constructor(code: string, message: string, status: number, details?: unknown) {
    super(message);
    this.name = 'FitAPIError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: unknown;
  sessionId?: string;
  idempotencyKey?: string;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const {
    method = 'GET',
    headers = {},
    body,
    sessionId = typeof window !== 'undefined' ? (localStorage.getItem('ai_fitting_session_id') || 'demo-shopper') : 'demo-shopper',
    idempotencyKey,
  } = options;

  const requestHeaders: Record<string, string> = {
    'Accept': 'application/json',
    'X-Session-ID': sessionId,
    ...headers,
  };

  if (idempotencyKey) {
    requestHeaders['Idempotency-Key'] = idempotencyKey;
  }

  let requestBody: BodyInit | undefined;
  if (body instanceof FormData) {
    requestBody = body;
    // Let browser set the boundary header
    delete requestHeaders['Content-Type'];
  } else if (body !== undefined) {
    requestHeaders['Content-Type'] = 'application/json';
    requestBody = JSON.stringify(body);
  }

  const url = `${API_BASE_URL.replace(/\/$/, '')}${path.startsWith('/') ? path : `/${path}`}`;

  let response: Response;
  try {
    response = await fetch(url, {
      method,
      headers: requestHeaders,
      body: requestBody,
    });
  } catch (networkError) {
    throw new FitAPIError(
      'NETWORK_ERROR',
      networkError instanceof Error ? networkError.message : 'Không thể kết nối tới máy chủ AI.',
      0
    );
  }

  if (response.status === 204) {
    return undefined as unknown as T;
  }

  let responseData: any;
  try {
    responseData = await response.json();
  } catch {
    responseData = null;
  }

  if (!response.ok) {
    if (responseData && typeof responseData === 'object' && 'error' in responseData) {
      const errRes = responseData as APIErrorResponse;
      throw new FitAPIError(
        errRes.error.code || 'API_ERROR',
        errRes.error.message || `Lỗi yêu cầu (${response.status})`,
        response.status,
        errRes.error.details
      );
    }
    throw new FitAPIError(
      'HTTP_ERROR',
      (responseData && responseData.detail) || `Yêu cầu thất bại với mã ${response.status}`,
      response.status
    );
  }

  return responseData as T;
}

export const fitApiClient = {
  // ===========================================================================
  // 1. Garments & Catalog
  // ===========================================================================
  async getGarments(params?: GarmentsQueryParams): Promise<PaginatedResponse<Garment>> {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', String(params.page));
    if (params?.pageSize) query.append('page_size', String(params.pageSize));
    if (params?.brand && params.brand !== 'all') query.append('brand', params.brand);
    if (params?.category && params.category !== 'all') query.append('category', params.category);
    if (params?.gender && params.gender !== 'all') query.append('gender', params.gender);
    if (params?.search) query.append('search', params.search);

    const queryString = query.toString();
    return request<PaginatedResponse<Garment>>(`/garments${queryString ? `?${queryString}` : ''}`);
  },

  async getGarment(id: string): Promise<GarmentDetail> {
    return request<GarmentDetail>(`/garments/${id}`);
  },

  async getGarmentSizeCharts(id: string): Promise<GarmentSizeChart[]> {
    return request<GarmentSizeChart[]>(`/garments/${id}/size-charts`);
  },

  // ===========================================================================
  // 2. Fit Profiles
  // ===========================================================================
  async getFitProfiles(sessionId?: string): Promise<FitProfilesListResponse> {
    return request<FitProfilesListResponse>('/fit-profiles', { sessionId });
  },

  async getFitProfile(id: string): Promise<UserProfile> {
    return request<UserProfile>(`/fit-profiles/${id}`);
  },

  async createFitProfile(data: CreateFitProfileRequest): Promise<UserProfile> {
    return request<UserProfile>('/fit-profiles', {
      method: 'POST',
      body: data,
    });
  },

  async updateFitProfile(id: string, data: UpdateFitProfileRequest): Promise<UserProfile> {
    return request<UserProfile>(`/fit-profiles/${id}`, {
      method: 'PATCH',
      body: data,
    });
  },

  async deleteFitProfile(id: string): Promise<void> {
    return request<void>(`/fit-profiles/${id}`, {
      method: 'DELETE',
    });
  },

  // ===========================================================================
  // 3. AI Pipeline Endpoints
  // ===========================================================================
  async checkQuality(input: QualityCheckRequest | FormData): Promise<QualityCheckResponse> {
    return request<QualityCheckResponse>('/pipeline/quality-check', {
      method: 'POST',
      body: input,
    });
  },

  async estimateMeasurements(data: MeasurementRequest): Promise<MeasurementResponse> {
    return request<MeasurementResponse>('/pipeline/measure', {
      method: 'POST',
      body: data,
    });
  },

  async getRecommendedSize(data: SizeRecommendRequest): Promise<SizeRecommendResponse> {
    return request<SizeRecommendResponse>('/pipeline/size-recommend', {
      method: 'POST',
      body: data,
    });
  },

  // ===========================================================================
  // 4. Virtual Try-On Endpoints
  // ===========================================================================
  async createTryOnJob(data: CreateTryOnJobRequest, idempotencyKey?: string): Promise<TryOnJob> {
    return request<TryOnJob>('/tryon/jobs', {
      method: 'POST',
      body: data,
      idempotencyKey,
    });
  },

  async getTryOnJob(jobId: string): Promise<TryOnJob> {
    return request<TryOnJob>(`/tryon/jobs/${jobId}`);
  },
};
