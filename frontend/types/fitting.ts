/**
 * TypeScript Schemas for AI Precision Fit
 * Matching 1-1 with OpenAPI 3.0 Contract (docs/api/ai_precision_fit_api.yaml),
 * Backend Pydantic models (backend/app/models/fitting.py), & Supabase Tables.
 */

// =============================================================================
// Common Types & Enums
// =============================================================================
export type Gender = 'female' | 'male';
export type FitPreference = 'slim' | 'regular' | 'relaxed';
export type FitMethod = 'ai_photo' | 'manual';
export type SizeLabel = 'XS' | 'S' | 'M' | 'L' | 'XL' | 'XXL';
export type FabricStretch = 'none' | 'low' | 'medium' | 'high';
export type Brand = 'zara' | 'uniqlo' | 'hm' | 'pullandbear' | 'stradivarius';
export type Category = 'jacket' | 'coat' | 'blazer' | 'puffer' | 'dress' | 'shirt' | 'pants';

export type FlowStep =
  | 'welcome'
  | 'profile_setup'
  | 'method_select'
  | 'upload_guide'
  | 'upload_verify'
  | 'manual_input'
  | 'analyzing'
  | 'recommendation'
  | 'profile_list'
  | 'profile_detail';

// =============================================================================
// 1. Database & Core Model Schemas
// =============================================================================
export interface UserProfile {
  id: string;
  userId?: string | null;
  sessionId?: string;
  name: string;
  gender: Gender;
  fitPreference: FitPreference;
  heightCm: number;
  weightKg: number;
  chestCm?: number;
  waistCm?: number;
  hipsCm?: number;
  shoulderCm?: number;
  frontImageUrl?: string;
  sideImageUrl?: string;
  isVerified: boolean;
  isDefault: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export type FitProfile = UserProfile;

export interface CreateFitProfileRequest {
  name: string;
  gender: Gender;
  fitPreference: FitPreference;
  heightCm: number;
  weightKg: number;
  chestCm?: number;
  waistCm?: number;
  hipsCm?: number;
  shoulderCm?: number;
  frontImageUrl?: string;
  sideImageUrl?: string;
  isDefault?: boolean;
}

export interface UpdateFitProfileRequest {
  name?: string;
  gender?: Gender;
  fitPreference?: FitPreference;
  heightCm?: number;
  weightKg?: number;
  chestCm?: number;
  waistCm?: number;
  hipsCm?: number;
  shoulderCm?: number;
  frontImageUrl?: string;
  sideImageUrl?: string;
  isVerified?: boolean;
  isDefault?: boolean;
}

export interface Garment {
  id: string;
  sku: string;
  name: string;
  brand: Brand;
  category: Category;
  gender: Gender | 'unisex';
  imageUrl: string;
  fabricStretch: FabricStretch;
  price?: number;
  description?: string;
  availableSizes?: SizeLabel[];
}

export interface GarmentSizeChart {
  id: string;
  garmentId: string;
  size: SizeLabel;
  chestMin?: number;
  chestMax?: number;
  waistMin?: number;
  waistMax?: number;
  hipsMin?: number;
  hipsMax?: number;
  shoulderWidth?: number;
  garmentLength?: number;
}

export interface GarmentDetail extends Garment {
  sizeCharts: GarmentSizeChart[];
}

// =============================================================================
// 2. Pagination & API Response Standards
// =============================================================================
export interface PaginationMetadata {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMetadata;
}

export interface GarmentsQueryParams {
  page?: number;
  pageSize?: number;
  brand?: 'all' | Brand;
  category?: 'all' | Category;
  gender?: 'all' | Gender | 'unisex';
  search?: string;
}

export interface FitProfilesListResponse {
  data: UserProfile[];
  total: number;
}

export interface APIErrorDetail {
  loc?: (string | number)[];
  msg?: string;
  type?: string;
  [key: string]: unknown;
}

export interface APIErrorResponse {
  error: {
    code: string;
    message: string;
    details?: APIErrorDetail[] | unknown;
  };
}

// =============================================================================
// 3. AI Pipeline & Try-On Request & Response Schemas
// =============================================================================

// --- /api/v1/quality-check ---
export interface QualityIssue {
  code: 'feet_cut_off' | 'head_cut_off' | 'blurry' | 'bad_lighting' | 'multi_person' | 'no_person' | 'bad_pose';
  severity: 'error' | 'warning';
  message: string;
  box?: [number, number, number, number]; // [ymin, xmin, ymax, xmax]
}

export interface QualityCheckRequest {
  imageBase64?: string;
  imageUrl?: string;
}

export interface QualityCheckResponse {
  isValid: boolean;
  confidenceScore: number;
  issues: QualityIssue[];
  blurScore: number;
  landmarksDetected: number;
}

// --- /api/v1/measure ---
export interface BodyMeasurements {
  heightCm: number;
  weightKg: number;
  shoulderCm?: number;
  chestCm?: number;
  waistCm?: number;
  hipsCm?: number;
}

export interface MeasurementRequest {
  frontImageUrl?: string;
  sideImageUrl?: string;
  knownHeightCm?: number;
  gender: Gender;
}

export interface MeasurementResponse {
  measurements: BodyMeasurements;
  confidencePercent: number;
  method: 'ai_vision' | 'anthropometric_hybrid';
}

// --- /api/v1/size-recommend ---
export interface PartFitEvaluation {
  part: 'shoulder' | 'chest' | 'waist' | 'hips' | 'length';
  partLabel: string;
  status: 'perfect' | 'slightly_tight' | 'slightly_loose' | 'too_tight' | 'too_loose';
  statusLabel: string;
  diffCm: number;
}

export interface SizeComparisonItem {
  fitScore: number;
  badgeLabel: string;
  description: string;
}

export interface SizeRecommendRequest {
  garmentId: string;
  profileId?: string;
  fitPreferenceOverride?: FitPreference;
  gender?: Gender;
  fitPreference?: FitPreference;
  measurements?: BodyMeasurements;
}

export interface SizeRecommendResponse {
  recommendedSize: SizeLabel;
  confidencePercent: number;
  fitPreferenceLabel: string;
  summaryExplanation: string;
  breakdown: PartFitEvaluation[];
  sizeComparisons: Record<string, SizeComparisonItem>;
}

export type SizeRecommendationResult = SizeRecommendResponse;

// --- /api/v1/tryon ---
export interface CreateTryOnJobRequest {
  profileId: string;
  garmentId: string;
  personImageUrl?: string;
  garmentImageUrl?: string;
}

export type TryOnJobRequest = CreateTryOnJobRequest;

export interface TryOnJob {
  jobId: string;
  profileId?: string;
  garmentId?: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  resultImageUrl?: string;
  errorMessage?: string;
  estimatedSeconds: number;
  createdAt?: string;
}

export type TryOnJobResponse = TryOnJob;
