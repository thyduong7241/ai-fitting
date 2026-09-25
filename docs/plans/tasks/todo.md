# Task Tracking: AI Precision Fit Implementation

> **Kế hoạch chi tiết:** `docs/plans/vibe_coding_first_plan.md`  
> **Kế hoạch Backend & AI (Deferred):** `docs/plans/DEFERRED_BACKEND_AND_AI_INTEGRATION.md`  
> **API Contract:** `docs/api/ai_precision_fit_api.yaml`  
> **Figma Spec:** [AI Precision Fit - Mobile Design System (Node 8:10 & 8:12)](https://www.figma.com/design/DOGArspqs5nAybRQh5k7OL/AI-Precision-Fit---Mobile-Design-System?node-id=8-10)

---

## Phase 0: Foundation & Multi-Profile Data Layer

- [x] **Task 0.1 [SHARED]:** Chuẩn hóa Type Contracts & Schemas
  - *Files:* `frontend/types/fitting.ts`, `backend/app/models/fitting.py`
  - *DoD:* Bổ sung `brand`, mở rộng enum `category` (50 products outerwear), khớp 100% với OpenAPI spec.
  - *Verification:* `cd frontend && npx tsc --noEmit` (Pass 0 errors)

- [x] **Task 0.2 [FE]:** Tích hợp 50 Sản phẩm Mẫu & Mock Size Charts
  - *Files:* `frontend/data/mockFittingData.ts`, `frontend/public/products/`
  - *DoD:* Copy đủ 50 ảnh từ `samples/assets/products/` sang `public/products/` theo 5 brand; export 50 garments kèm size chart.
  - *Verification:* `find frontend/public/products -type f | wc -l` (kết quả = 50), `npm run check:fast` (Pass 0 errors)

- [x] **Task 0.3 [FE]:** Multi-Profile Manager Hook (`useProfiles.ts`)
  - *Files:* `frontend/hooks/useProfiles.ts`
  - *DoD:* Quản lý `profiles`, `activeProfile`, seed sẵn Trang & Minh, lưu trữ `localStorage`.
  - *Verification:* Typecheck pass (`npm run check:task`), thao tác add/switch/update/delete hoạt động chuẩn.

### Checkpoint 0: Foundation & Data Layer
- [x] Tất cả Type definitions đồng bộ giữa FE và BE.
- [x] 50 ảnh sản phẩm sẵn sàng phục vụ tĩnh từ public.
- [x] State Multi-Profile hoạt động ổn định trên LocalStorage.

---

## Phase 1: Design Tokens & Base UI Primitives

- [x] **Task 1.1 [FE]:** Cấu hình Tailwind Theme & Design Tokens
  - *Files:* `frontend/tailwind.config.js`, `frontend/app/globals.css`, `frontend/app/layout.tsx`
  - *DoD:* Cài đặt bảng màu Figma Node 8:10 & 8:12 (Teal `#16ABAD`, Navy `#183247`, Slate `#5C738C`, Border `#DFEBEF`, Canvas `#F6FBFA`), font `Be Vietnam Pro` (fallback Inter).
  - *Verification:* `cd frontend && npm run build` pass không warning.

- [x] **Task 1.2 [FE]:** Mobile Layout Shell (`WidgetContainer.tsx`)
  - *Files:* `frontend/components/fitting/WidgetContainer.tsx`
  - *DoD:* Khung 390px x 844px căn giữa trên Desktop, full màn hình trên Mobile, có status bar giả lập.
  - *Verification:* Responsive sạch, không bị thanh cuộn ngang trên mọi độ phân giải.

- [x] **Task 1.3 [FE]:** Bộ Atomic UI Primitives (Button, Badge, StepHeader)
  - *Files:* `frontend/components/ui/Button.tsx`, `frontend/components/ui/Badge.tsx`, `frontend/components/ui/StepHeader.tsx`
  - *DoD:* Cung cấp đủ variants, trạng thái loading, màu sắc chuẩn Figma.
  - *Verification:* Export đầy đủ TypeScript props, không lỗi type (`npm run check:task` pass).

- [x] **Task 1.4 [FE]:** Bộ Form & Selection Controls (SegmentedControl, StepperInput, ProfileSwitcher)
  - *Files:* `frontend/components/ui/SegmentedControl.tsx`, `frontend/components/ui/StepperInput.tsx`, `frontend/components/ui/ProfileSwitcher.tsx`
  - *DoD:* Tab trượt mượt mà, Stepper +/- tăng giảm số đo, ProfileSwitcher hiển thị pill chọn nhanh profile.
  - *Verification:* Bấm đổi profile trên ProfileSwitcher kích hoạt đúng callback (`npm run check:task` pass).

### Checkpoint 1: UI Shell & Primitives
- [x] Toàn bộ atomic components và layout shell sẵn sàng ghép vào màn hình nghiệp vụ.

---

## Phase 2: Core User Journey Screens (Fitting Widget Flow)

- [x] **Task 2.1 [FE]:** Fitting Flow State Machine Hook (`useFittingFlow.ts`)
  - *Files:* `frontend/hooks/useFittingFlow.ts`
  - *DoD:* Quản lý chuyển đổi qua lại 10 màn hình, hỗ trợ `goToStep`, `goBack`, lưu state session đo.
  - *Verification:* Test chuỗi chuyển bước và nút Back hoạt động chính xác theo stack (`npm run check:task` pass).

- [x] **Task 2.2 [FE]:** Screen 1 & 2 — WelcomeScreen & ProfileSetupScreen
  - *Files:* `frontend/components/fitting/WelcomeScreen.tsx`, `frontend/components/fitting/ProfileSetupScreen.tsx`
  - *DoD:* Màn hình chào mừng và form tạo nhanh profile (Tên, Giới tính, Gu mặc).
  - *Verification:* Tạo profile lưu thành công vào LocalStorage và tự động chuyển bước (`npm run check:task` pass).

- [x] **Task 2.3 [FE]:** Screen 3 — MethodSelectScreen (Chọn Phương Thức Đo)
  - *Files:* `frontend/components/fitting/MethodSelectScreen.tsx`
  - *DoD:* 2 tùy chọn: AI Chụp ảnh (badge Khuyên dùng) hoặc Nhập tay số đo 3 vòng.
  - *Verification:* Chọn AI đi tới Screen 4; chọn Nhập tay đi tới Screen 6 (`npm run check:task` pass).

### Checkpoint 2: Onboarding Flow
- [x] Luồng Welcome -> Setup -> Method Select vận hành trơn tru.

- [x] **Task 2.4 [FE]:** Screen 4 & 5 — UploadGuideScreen & UploadVerifyScreen
  - *Files:* `frontend/components/fitting/UploadGuideScreen.tsx`, `frontend/components/fitting/UploadVerifyScreen.tsx`
  - *DoD:* Hướng dẫn tư thế đứng; màn hình verify có toggle kiểm tra cả ảnh lỗi (cắt chân) và ảnh chuẩn (tick xanh).
  - *Verification:* Người dùng chuyển đổi được giữa 2 trạng thái kiểm định để verify giao diện (`npm run check:task` pass).

- [x] **Task 2.5 [FE]:** Screen 6 — ManualInputScreen (Nhập Số Đo Thủ Công)
  - *Files:* `frontend/components/fitting/ManualInputScreen.tsx`
  - *DoD:* Form nhập Chiều cao, Cân nặng, Vòng ngực, Eo, Hông, Vai; có toggle cm / inch.
  - *Verification:* Validate dữ liệu theo schema và lưu kết quả vào profile (`npm run check:task` pass).

- [x] **Task 2.6 [FE]:** Screen 7 — AnalyzingScreen (Scanning Radar Animation)
  - *Files:* `frontend/components/fitting/AnalyzingScreen.tsx`
  - *DoD:* Radar animation vòng tròn Teal, hiển thị 3 bước phân tích tuần tự, tự chuyển trang sau 2.5s.
  - *Verification:* Timer dọn dẹp sạch khi unmount, chuyển tiếp sang kết quả tự động (`npm run check:task` pass).

### Checkpoint 3: Input & Scanning Flow
- [x] Cả 2 luồng nhập liệu (AI ảnh & Nhập tay) đều hoàn tất và chạy qua bước quét vóc dáng.

- [x] **Task 2.7 [FE]:** Fit Engine Service & RecommendationScreen
  - *Files:* `frontend/services/fitEngine.ts`, `frontend/components/fitting/RecommendationScreen.tsx`
  - *DoD:* Thuật toán rule-based tính độ vừa vặn; hiển thị size khuyên dùng, 5 vùng cơ thể, hotspot so sánh size.
  - *Verification:* Đổi qua lại giữa Trang và Minh trên ProfileSwitcher thì size gợi ý tự động thay đổi tương ứng (`npm run check:task` pass).

- [x] **Task 2.8 [FE]:** Screen 9 & 10 — Profile Management (List & Detail)
  - *Files:* `frontend/components/fitting/ProfileListScreen.tsx`, `frontend/components/fitting/ProfileDetailScreen.tsx`
  - *DoD:* Quản lý danh sách profiles (chọn active, thêm mới, xóa) và xem/sửa chi tiết số đo từng profile.
  - *Verification:* Thêm/sửa/xóa profile cập nhật lập tức vào state và LocalStorage (`npm run check:task` pass).

- [x] **Task 2.9 [FE]:** Virtual Try-On Preview Modal (`VTOPreviewModal.tsx`)
  - *Files:* `frontend/components/fitting/VTOPreviewModal.tsx`, `docs/specs/SPEC-vto-modal.md`
  - *DoD:* Modal chuẩn Figma Node 8:12 quản lý 8 trạng thái: ready, queued, processing AI, kết quả thử đồ với toggle xem ảnh gốc, bad_quality, và service_unavailable.
  - *Verification:* Mở thử từ màn hình Recommendation hiển thị chính xác luồng 8 trạng thái (`npm run check:task` pass).

### Checkpoint 4: Fitting & Try-On Complete
- [x] Toàn bộ 10 màn hình của Fitting Widget hoạt động chuẩn xác không lỗi.

---

## Phase 3: Product Catalog Demo Integration

- [x] **Task 3.1 [FE]:** Xây dựng Catalog Demo Page (`frontend/app/page.tsx`)
  - *Files:* `frontend/app/page.tsx`
  - *DoD:* Sàn diễn thời trang demo 50 sản phẩm thực tế, lọc theo 5 thương hiệu, hiển thị ProfileSwitcher trên header, bấm sản phẩm mở Fitting Widget.
  - *Verification:* Lọc brand và kích hoạt widget hoạt động chuẩn trên browser (`npm run check:task` pass, `npm run build` pass).

- [x] **Task 3.2 [FE]:** E2E Smoke Test & Linter Verification
  - *Files:* Toàn bộ frontend
  - *DoD:* Chạy production build không lỗi, test kịch bản đa profile từ A-Z.
  - *Verification:* `cd frontend && npm run build` -> Exit code 0 (Pass 8/8 routes, 0 TypeScript errors, 0 ESLint warnings).

### Checkpoint 5: Web App Ready for Presentation
- [x] 50 sản phẩm mẫu duyệt qua mượt mà với đầy đủ ảnh thật, size chart và bộ lọc.
- [x] Trải nghiệm Zero-Auth Multi-Profile hoàn hảo trên cả desktop và mobile browser.

---

## Deferred Phase 4: Backend & AI Pipeline (`[BE]`)
*(Sẽ kích hoạt ngay sau khi hoàn thành Phase 0-3. Xem chi tiết tại `docs/plans/DEFERRED_BACKEND_AND_AI_INTEGRATION.md`)*

- [ ] **Task BE-4.1 [BE]:** Supabase Migrations & 50 Products Seed Script (`seed_50_garments.py`)
- [ ] **Task BE-4.2 [BE]:** FastAPI Garments & Profiles REST Endpoints
- [ ] **Task BE-4.3 [BE]:** MediaPipe Pose & Laplacian Blur Quality Gate Service (`/quality-check`)
- [ ] **Task BE-4.4 [BE]:** Anthropometric 33-Landmark Measurement Service (`/measure`)
- [ ] **Task BE-4.5 [BE]:** Backend Rule-Based Fit Engine & Template Explanation (`/size-recommend`)
- [ ] **Task BE-4.6 [BE]:** CatVTON GPU Microservice Queue & TryOn Job Manager (`/tryon/jobs`)
- [ ] **Task BE-4.7 [FE]:** Frontend API Client Bridge (`USE_REAL_BACKEND_API` Feature Flag)
