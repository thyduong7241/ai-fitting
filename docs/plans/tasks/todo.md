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

## Phase 4: Backend & Real AI Pipeline Integration (`[BE]` & `[FE]`)
*(Kế hoạch kiến trúc chi tiết tại `docs/plans/DEFERRED_BACKEND_AND_AI_INTEGRATION.md`)*

### Phase 4A: Hạ Tầng Dữ Liệu & REST API Cốt Lõi

- [ ] **Task BE-4.1 [BE]:** Supabase Migrations & 50 Products Seed Script (`seed_50_garments.py`)
  - *Files:* `supabase/migrations/20240924000000_ai_fitting_schema.sql`, `backend/scripts/seed_50_garments.py`
  - *DoD:* Cập nhật enum `brand` ('zara', 'uniqlo', 'hm', 'pullandbear', 'stradivarius'), mở rộng `category` ('jacket', 'coat', 'blazer', 'puffer'...), thêm cột `price`, `available_sizes`, index tìm kiếm. Script `seed_50_garments.py` kết nối Supabase client nạp đủ 50 garments và size charts chuẩn từ dữ liệu mẫu vào PostgreSQL.
  - *Verification:* `cd backend && ./.venv/bin/python scripts/seed_50_garments.py` chạy thành công không lỗi; query database trả về đúng 50 sản phẩm.

- [ ] **Task BE-4.2 [BE]:** FastAPI Garments & Profiles REST Endpoints
  - *Files:* `backend/app/api/endpoints/garments.py`, `backend/app/api/endpoints/profiles.py`, `backend/app/services/garment_service.py`, `backend/app/services/profile_service.py`, `backend/app/main.py`
  - *DoD:* Triển khai `GET /api/v1/garments` (hỗ trợ phân trang `page`, `page_size`, lọc `brand`, `category`), `GET /api/v1/garments/{id}` (kèm size charts); CRUD `/api/v1/fit-profiles` lưu trữ theo header `X-Session-ID` (hỗ trợ Zero-Auth multi-profile). Khớp 100% Pydantic models `backend/app/models/fitting.py`.
  - *Verification:* `curl -s http://localhost:8000/api/v1/garments?brand=zara | grep -q "zara"` trả về status 200; Swagger UI tại `http://localhost:8000/docs` hiển thị đầy đủ schema và test thành công.

#### Checkpoint 4A: Database & Core REST Services
- [ ] Schema database đồng bộ 100% với OpenAPI contract (`docs/api/ai_precision_fit_api.yaml`).
- [ ] 50 sản phẩm thực tế và size charts được lưu trữ đầy đủ trong Supabase PostgreSQL.
- [ ] REST API Garments và Profiles hoạt động ổn định trên FastAPI (port 8000).

---

### Phase 4B: AI Vision Microservice (`vision-service`), Benchmark & Fit Scoring Pipeline
*(Chi tiết đặc tả kỹ thuật & Khung Benchmark: `docs/plans/VISION_SERVICE_MICROSERVICE_AND_BENCHMARK_PLAN.md`)*  
*(Chi tiết 16 granular tasks cho agent implement: [`tasks/plan.md`](file:///home/aiuser4/nttduong/ai-fitting/tasks/plan.md) & [`tasks/todo.md`](file:///home/aiuser4/nttduong/ai-fitting/tasks/todo.md))*

- [ ] **Task BE-4.3 [AI/BE]:** Vision Microservice Architecture & Ground Truth Benchmark Harness (`vision-service`)
  - *Files:* `vision-service/Dockerfile`, `vision-service/app/main.py`, `vision-service/benchmark/run_benchmark.py`, `vision-service/benchmark/datasets/ground_truth.json`, `docker-compose.yml`
  - *DoD:* Tách riêng microservice `vision-service` chạy trên port 8002 (CPU isolated). Xây dựng bộ test harness tự động `run_benchmark.py` đối chiếu với tập dữ liệu ground truth đo thước dây thực tế, xuất báo cáo F1-Score, MAE, MAPE và chặn suy giảm chỉ số (Ratchet Guard). Cập nhật `docker-compose.yml`.
  - *Verification:* `cd vision-service && pytest tests/ -v` pass; `python benchmark/run_benchmark.py --check-ratchet` thực thi thành công.

- [ ] **Task BE-4.4 [AI/BE]:** Chuyên sâu 5-Layer Quality Gate Engine (`/api/v1/quality-check`)
  - *Files:* `vision-service/app/services/quality_gate_engine.py`, `vision-service/app/api/v1/quality_check.py`, `backend/app/services/quality_check_service.py`
  - *DoD:* Xử lý 5 lớp: Tenengrad + Laplacian blur trên Body ROI, phát hiện đúng 1 người (MediaPipe Pose + Face), ước tính đỉnh đầu và mốc ngón chân phát hiện cắt mép ảnh (kèm normalized bounding box lỗi), phân loại tư thế Front vs Side, kiểm tra ánh sáng HSV histogram. Backend gọi sang `vision-service:8002` qua HTTP client.
  - *Verification:* Chạy benchmark Quality Gate đạt **F1-Score $\ge 96\%$** trên lỗi cắt đầu/chân, **Blur Accuracy $\ge 92\%$**, False Rejection $\le 3\%$.

- [ ] **Task BE-4.5 [AI/BE]:** Hybrid 2-View Stereometry & Smart Fit Notes Engine (`/api/v1/measure`)
  - *Files:* `vision-service/app/services/measurement/`, `vision-service/app/engines/hybrid_stereometry.py`, `vision-service/app/api/v1/measure.py`, `backend/app/services/anthropometric_service.py`
  - *DoD:* Input nhận `known_height_cm`, `weight_kg`, `age`, `gender` và 2 ảnh (front + side 90°). Trích xuất P2M scale (Crown to Heel), tính Bi-acromial shoulder width, chu vi ngực/eo/hông theo công thức Ramanujan elip 2 góc chụp tích hợp tiền nghiệm Tuổi (Age Drift sau 25) và BMI, tự động phân loại vóc dáng (Quả lê, Đồng hồ cát, Quả táo, Chữ nhật, Tam giác ngược) và sinh Smart Fit Notes may mặc. Backend gọi sang `vision-service:8002` qua HTTP client.
  - *Verification:* Chạy benchmark đối chiếu ground truth đạt **MAE Vai $\le 1.5\text{cm}$**, **Eo $\le 2.0\text{cm}$**, **Ngực/Hông $\le 2.5\text{cm}$**, Tolerance Pass Rate $\ge 90\%$, Latency P95 $\le 45\text{ms}$.

- [ ] **Task BE-4.6 [BE]:** Backend Rule-Based Fit Engine & Template Explanation (`/size-recommend`)
  - *Files:* `backend/app/api/endpoints/size_recommend.py`, `backend/app/services/fit_engine_service.py`, `backend/tests/test_fit_engine.py`
  - *DoD:* Porting logic từ `frontend/services/fitEngine.ts` lên FastAPI: tính sai phân delta = Garment Spec - Body Measurement cho 5 vùng (Vai 35%, Ngực 35%, Eo 15%, Hông 10%, Dài 5%), bù trừ độ co giãn vải (`fabric_stretch`), điều chỉnh theo gu mặc (`slim`, `regular`, `relaxed`), xếp hạng size tốt nhất (Fit Score 0-100) và tự động sinh câu giải thích tiếng Việt theo template quy chuẩn.
  - *Verification:* `cd backend && ./.venv/bin/pytest tests/test_fit_engine.py` pass; đối chiếu kết quả trả về khớp 100% với `frontend/services/fitEngine.ts`.

#### Checkpoint 4B: AI Vision Microservice, Benchmark & Fit Pipeline Complete
- [ ] `vision-service` chạy độc lập trong Docker container (port 8002), tách biệt hoàn toàn với Web API.
- [ ] Bộ công cụ `run_benchmark.py` tự động kiểm chuẩn toàn bộ pipeline dựa trên Ground Truth thực tế.
- [ ] Quality Gate đạt F1-Score $\ge 96\%$, Measurement đạt MAE $\le 2.0\text{cm}$ và Tolerance Pass Rate $\ge 90\%$.
- [ ] Backend Fit Engine chấm điểm và giải thích size chuẩn xác theo quy tắc nhân trắc học.

---

### Phase 4C: Virtual Try-On (CatVTON) & Tích Hợp Toàn Diện

- [ ] **Task BE-4.7 [BE]:** CatVTON GPU Microservice Queue & TryOn Job Manager (`/tryon/jobs`)
  - *Files:* `vto-service/Dockerfile`, `vto-service/app/main.py`, `backend/app/api/endpoints/tryon.py`, `backend/app/services/tryon_service.py`
  - *DoD:* Xây dựng container `vto-service` độc lập chạy mô hình CatVTON (GPU CUDA); FastAPI router `/api/v1/tryon/jobs` tiếp nhận request, sinh `job_id`, hỗ trợ `Idempotency-Key`, đẩy tác vụ sang `vto-service` nền và trả về HTTP 202; endpoint polling `GET /api/v1/tryon/jobs/{id}` trả về tiến độ và link ảnh kết quả 1024x1024 trong Supabase Storage.
  - *Verification:* Gọi `POST /api/v1/tryon/jobs` trả về `status: queued` (202); polling trả về `status: completed` kèm URL ảnh mặc thử hợp lệ; xử lý lỗi `503 Service Unavailable` khi GPU bận.

- [ ] **Task BE-4.8 [FE]:** Frontend API Client Bridge (`USE_REAL_BACKEND_API` Feature Flag)
  - *Files:* `frontend/services/apiClient.ts`, `frontend/hooks/useFittingFlow.ts`, `frontend/components/fitting/WidgetContainer.tsx`, `frontend/components/fitting/VTOPreviewModal.tsx`
  - *DoD:* Bật cờ `NEXT_PUBLIC_USE_REAL_BACKEND=true` trong `frontend/.env.local`; thay thế toàn bộ mock timer/data ở các bước Quality Check, Analyzing (gọi `/measure`), Recommendation (gọi `/size-recommend`), và VTO Preview Modal (gọi polling `/tryon/jobs`) bằng `apiClient.ts`. Hỗ trợ fallback mượt mà nếu Backend offline.
  - *Verification:* `cd frontend && npm run check:task` (0 type errors, 0 lint warnings); thực hiện thử đồ trên trình duyệt, kiểm tra tab Network gọi API thật thành công 100%.

- [ ] **Task BE-4.9 [SHARED]:** E2E Smoke Test Toàn Hệ Thống Live Pipeline
  - *Files:* Toàn bộ dự án
  - *DoD:* Thực hiện trọn vẹn luồng từ Upload ảnh thật -> AI quét trích xuất số đo thật -> Backend gợi ý size -> Mặc thử ảo CatVTON -> Hiển thị kết quả. Không còn bất kỳ bước giả lập nào trong widget.
  - *Verification:* Kiểm tra toàn bộ luồng hoạt động mượt mà không lỗi console hoặc network error (`cd frontend && npm run build` pass).

#### Checkpoint 4C: Full Pipeline Live & Virtual Fitting Hoàn Chỉnh
- [ ] Toàn bộ luồng từ Upload ảnh thật -> Quét số đo AI -> Gợi ý size -> Thử đồ ảo CatVTON chạy live end-to-end.
- [ ] Không còn bất kỳ bước giả lập nào trong widget khi bật Live Mode.
