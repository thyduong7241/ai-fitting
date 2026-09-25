-- Seed data for AI Precision Fit

-- 1. Profiles mẫu (Khớp Figma Node 8:10)
INSERT INTO public.fit_profiles (id, name, gender, fit_preference, height_cm, weight_kg, chest_cm, waist_cm, hips_cm, shoulder_cm, is_verified, is_default)
VALUES 
  ('a1111111-1111-1111-1111-111111111111', 'Trang', 'female', 'regular', 162.0, 50.0, 84.0, 65.0, 90.0, 37.0, true, true),
  ('b2222222-2222-2222-2222-222222222222', 'Minh', 'male', 'relaxed', 175.0, 68.0, 94.0, 78.0, 96.0, 43.0, true, false)
ON CONFLICT (id) DO NOTHING;

-- 2. Sản phẩm thời trang mẫu (Đầm Linen dáng suông trong thiết kế Figma)
INSERT INTO public.garments (id, sku, name, category, gender, image_url, fabric_stretch, description)
VALUES 
  ('c3333333-3333-3333-3333-333333333333', 'DR-LINEN-01', 'Đầm Linen Dáng Suông Phối Túi', 'dress', 'female', '/garments/linen-dress-flatlay.png', 'none', 'Đầm linen tự nhiên thoáng mát, form suông A nhẹ nhàng che khuyết điểm.')
ON CONFLICT (sku) DO NOTHING;

-- 3. Bảng size chi tiết cho Đầm Linen (Size M là vừa vặn chuẩn nhất cho profile Trang)
INSERT INTO public.garment_size_charts (garment_id, size, chest_min, chest_max, waist_min, waist_max, hips_min, hips_max, shoulder_width, garment_length)
VALUES 
  ('c3333333-3333-3333-3333-333333333333', 'XS', 78.0, 82.0, 60.0, 63.0, 84.0, 88.0, 36.0, 105.0),
  ('c3333333-3333-3333-3333-333333333333', 'S',  82.0, 86.0, 64.0, 67.0, 88.0, 92.0, 37.5, 107.0),
  ('c3333333-3333-3333-3333-333333333333', 'M',  86.0, 90.0, 68.0, 72.0, 92.0, 96.0, 39.0, 109.0),
  ('c3333333-3333-3333-3333-333333333333', 'L',  90.0, 95.0, 73.0, 77.0, 96.0, 101.0, 40.5, 111.0),
  ('c3333333-3333-3333-3333-333333333333', 'XL', 95.0, 101.0, 78.0, 83.0, 101.0, 107.0, 42.0, 113.0)
ON CONFLICT (garment_id, size) DO NOTHING;