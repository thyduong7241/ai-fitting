-- Migration: AI Precision Fit Schema
-- Description: Creates fit_profiles, garments, garment_size_charts, fit_recommendations, tryon_jobs tables with RLS

-- 1. Table: fit_profiles
CREATE TABLE IF NOT EXISTS public.fit_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  session_id TEXT,
  name TEXT NOT NULL,
  gender TEXT NOT NULL CHECK (gender IN ('female', 'male')),
  fit_preference TEXT NOT NULL CHECK (fit_preference IN ('slim', 'regular', 'relaxed')),
  height_cm NUMERIC(5,2) NOT NULL,
  weight_kg NUMERIC(5,2) NOT NULL,
  chest_cm NUMERIC(5,2),
  waist_cm NUMERIC(5,2),
  hips_cm NUMERIC(5,2),
  shoulder_cm NUMERIC(5,2),
  front_image_url TEXT,
  side_image_url TEXT,
  is_verified BOOLEAN DEFAULT FALSE NOT NULL,
  is_default BOOLEAN DEFAULT FALSE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fit_profiles_user_id ON public.fit_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_fit_profiles_session_id ON public.fit_profiles(session_id);

-- 2. Table: garments
CREATE TABLE IF NOT EXISTS public.garments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sku TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('dress', 'shirt', 'pants', 'jacket')),
  gender TEXT NOT NULL CHECK (gender IN ('female', 'male', 'unisex')),
  image_url TEXT NOT NULL,
  fabric_stretch TEXT DEFAULT 'none' CHECK (fabric_stretch IN ('none', 'low', 'medium', 'high')),
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_garments_sku ON public.garments(sku);

-- 3. Table: garment_size_charts
CREATE TABLE IF NOT EXISTS public.garment_size_charts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  garment_id UUID NOT NULL REFERENCES public.garments(id) ON DELETE CASCADE,
  size TEXT NOT NULL CHECK (size IN ('XS', 'S', 'M', 'L', 'XL', 'XXL')),
  chest_min NUMERIC(5,2),
  chest_max NUMERIC(5,2),
  waist_min NUMERIC(5,2),
  waist_max NUMERIC(5,2),
  hips_min NUMERIC(5,2),
  hips_max NUMERIC(5,2),
  shoulder_width NUMERIC(5,2),
  garment_length NUMERIC(5,2),
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  UNIQUE (garment_id, size)
);

CREATE INDEX IF NOT EXISTS idx_size_charts_garment_id ON public.garment_size_charts(garment_id);

-- 4. Table: fit_recommendations
CREATE TABLE IF NOT EXISTS public.fit_recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES public.fit_profiles(id) ON DELETE CASCADE,
  garment_id UUID NOT NULL REFERENCES public.garments(id) ON DELETE CASCADE,
  recommended_size TEXT NOT NULL,
  confidence_score NUMERIC(4,2) NOT NULL,
  fit_breakdown JSONB NOT NULL,
  explanation_text TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- 5. Table: tryon_jobs
CREATE TABLE IF NOT EXISTS public.tryon_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES public.fit_profiles(id) ON DELETE CASCADE,
  garment_id UUID NOT NULL REFERENCES public.garments(id) ON DELETE CASCADE,
  status TEXT NOT NULL CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
  result_image_url TEXT,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Row Level Security (RLS) Setup
ALTER TABLE public.fit_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.garments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.garment_size_charts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fit_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tryon_jobs ENABLE ROW LEVEL SECURITY;

-- Garments & Size Charts: Public Read
CREATE POLICY "Public read garments" ON public.garments FOR SELECT USING (true);
CREATE POLICY "Public read garment_size_charts" ON public.garment_size_charts FOR SELECT USING (true);

-- Fit Profiles: User can manage own profiles, or guest by session_id
CREATE POLICY "Users can manage own fit_profiles" ON public.fit_profiles
  FOR ALL USING (
    (auth.uid() IS NOT NULL AND auth.uid() = user_id) OR
    (auth.uid() IS NULL AND session_id IS NOT NULL)
  );

-- Fit Recommendations: Read policy
CREATE POLICY "Users can read own recommendations" ON public.fit_recommendations
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.fit_profiles
      WHERE public.fit_profiles.id = fit_recommendations.profile_id
      AND (
        (auth.uid() IS NOT NULL AND auth.uid() = fit_profiles.user_id) OR
        (auth.uid() IS NULL AND fit_profiles.session_id IS NOT NULL)
      )
    )
  );
