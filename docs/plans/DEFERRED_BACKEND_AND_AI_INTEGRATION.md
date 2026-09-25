# AI Precision Fit — Kế hoạch Phát triển Tầng Backend & AI Pipeline (Deferred Implementation Spec)

> **Tài liệu tham chiếu:**
> - API Contract: `docs/api/ai_precision_fit_api.yaml`
> - Tech Stack: `docs/plans/tech_stacks.md`
> - Kế hoạch Frontend hiện tại: `docs/plans/vibe_coding_first_plan.md`
> - Task Tracker: `docs/plans/tasks/todo.md`

Tài liệu này tập trung lưu trữ toàn bộ các hạng mục công việc thuộc tầng **Backend (FastAPI)**, **Database (Supabase On-prem)**, **AI Pipeline (MediaPipe & Anthropometrics)** và **Virtual Try-On Microservice (CatVTON)** cần được triển khai nối tiếp ngay sau khi hoàn tất giai đoạn dựng Frontend Mock Demo.

---

## 1. Bản đồ Kiến trúc Chuyển đổi (Mock → Live Pipeline)

Hiện tại, Frontend Widget chạy ở chế độ **Mock Contract-Compliant**:
```
[Frontend UI] ──(Gọi trực tiếp)──> [mockFittingData.ts & client-side fitEngine.ts]
```

Khi kích hoạt kế hoạch Backend này, hệ thống sẽ chuyển sang kiến trúc phân tán On-premise:
```
[Frontend UI]
     │
     ▼ (HTTP / REST qua apiClient.ts)
[FastAPI Backend :8000]
     ├── /fit-profiles & /garments ──> [Supabase PostgreSQL (Docker)]
     ├── /quality-check ────────────> [MediaPipe Pose + OpenCV Blur Check (CPU)]
     ├── /measure ──────────────────> [33 Landmarks + Anthropometric Engine (CPU)]
     ├── /size-recommend ───────────> [FastAPI Rule-based Fit Engine]
     └── /tryon/jobs ───────────────> [vto-service :8001 (CatVTON GPU Microservice)]
```

---

## 2. Chi tiết các Hạng mục Cần Phát triển (Deferred Modules)

### MODULE 1: Database & Seed Migration (Supabase Self-hosted) `[BE]`

- **Nhiệm vụ:**
  1. **Schema Update:** Cập nhật file migration `supabase/migrations/20240924000000_ai_fitting_schema.sql`:
     - Bổ sung cột `brand TEXT NOT NULL` vào bảng `garments` (`zara`, `uniqlo`, `hm`, `pullandbear`, `stradivarius`).
     - Mở rộng ràng buộc `category` thành `('jacket', 'coat', 'blazer', 'puffer', 'dress', 'shirt', 'pants')`.
     - Thêm cột `price NUMERIC(10,2)` và `available_sizes TEXT[]`.
  2. **Seed Data Script:** Viết script `backend/scripts/seed_50_garments.py` đọc từ `samples/data/products.json` và `samples/assets/products/`, insert tự động 50 sản phẩm thực tế kèm bảng size chart chuẩn vào PostgreSQL.
  3. **Storage Bucket:** Tạo Supabase storage bucket `fitting-uploads` (public read, authenticated/guest write) để lưu ảnh upload từ người dùng.
- **Tiêu chuẩn nghiệm thu (DoD):**
  - Chạy `docker compose up -d supabase` thành công.
  - Query `SELECT count(*) FROM garments;` trả về đúng 50 bản ghi.

---

### MODULE 2: FastAPI CRUD Routers & Data Contracts `[BE]`

- **Nhiệm vụ:**
  1. **Garment Endpoints:**
     - `GET /api/v1/garments`: Phân trang (`page`, `page_size`), lọc theo `brand`, `category`, `gender`, tìm kiếm theo tên.
     - `GET /api/v1/garments/{id}`: Trả về chi tiết garment kèm toàn bộ `size_charts` liên quan.
  2. **Profile Endpoints:**
     - `GET /api/v1/fit-profiles`: Lấy danh sách profiles theo header `X-Session-ID` hoặc JWT auth.
     - `POST /api/v1/fit-profiles`: Tạo mới profile và lưu vào Postgres.
     - `PATCH /api/v1/fit-profiles/{id}`: Cập nhật thông tin / số đo mới.
     - `DELETE /api/v1/fit-profiles/{id}`: Xóa profile an toàn (Idempotent).
- **Files mục tiêu:**
  - `backend/app/api/endpoints/garments.py`
  - `backend/app/api/endpoints/profiles.py`
  - `backend/app/services/garment_service.py`
  - `backend/app/services/profile_service.py`
- **Tiêu chuẩn nghiệm thu (DoD):**
  - Test qua Swagger UI `http://localhost:8000/docs` trả về status 200/201 khớp schema `docs/api/ai_precision_fit_api.yaml`.

---

### MODULE 3: AI Quality Gate Service (`/pipeline/quality-check`) `[BE]`

- **Nhiệm vụ:**
  - Tiếp nhận ảnh từ `multipart/form-data` hoặc `base64`.
  - **Laplacian Blur:** Dùng `cv2.Laplacian(gray, cv2.CV_64F).var()`. Điểm < 100 gán cảnh báo `blurry`.
  - **MediaPipe Pose Landmarker:**
    - Kiểm tra phát hiện ít nhất 1 người (`no_person` nếu count == 0; `multi_person` nếu count > 1).
    - Kiểm tra tọa độ landmarks bàn chân (27, 28, 29, 30, 31, 32): Nếu `y >= 0.98` hoặc ngoài khung hình -> Báo lỗi `feet_cut_off`.
    - Kiểm tra đỉnh đầu (landmarks 0): Nếu `y <= 0.02` -> Báo lỗi `head_cut_off`.
    - Trả về danh sách `QualityIssue` kèm normalized bounding box lỗi để frontend vẽ khung cảnh báo màu đỏ.
- **Files mục tiêu:**
  - `backend/app/api/endpoints/quality_check.py`
  - `backend/app/services/quality_check_service.py`
- **Tiêu chuẩn nghiệm thu (DoD):**
  - Chạy test suite với fixture ảnh bàn chân bị cắt -> API trả về `is_valid: false`, `code: feet_cut_off`.
  - Ảnh mẫu toàn thân đạt chuẩn -> Trả về `is_valid: true`, `confidence_score >= 0.9`.

---

### MODULE 4: Anthropometric Measurement Service (`/pipeline/measure`) `[BE]`

- **Nhiệm vụ:**
  - Nhận diện 33 mốc giải phẫu từ MediaPipe Pose.
  - Kết hợp với chiều cao do người dùng cung cấp (`known_height_cm`) để xác định hệ số quy đổi pixel-to-metric:
    $$\text{Scale Ratio} = \frac{\text{known\_height\_cm}}{\text{pixel\_distance}(\text{landmark\_0}, \text{landmark\_31\_32\_mid})}$$
  - Áp dụng các tỷ lệ nhân trắc học giải phẫu (Anthropometric Proportions):
    - **Rộng vai (Bi-acromial):** Khoảng cách giữa 2 mốc vai (11 và 12) $\times \text{Scale Ratio} \times \text{Shoulder Factor}$.
    - **Vòng ngực (Chest):** Ước lượng chu vi elip từ độ rộng ngực (front) và chiều sâu ngực (side ảnh nếu có, hoặc tỷ lệ chuẩn theo BMI).
    - **Vòng eo & Vòng hông:** Tương tự trích xuất từ khoảng cách mốc xương hông (23 và 24).
- **Files mục tiêu:**
  - `backend/app/api/endpoints/measure.py`
  - `backend/app/services/anthropometric_service.py`
- **Tiêu chuẩn nghiệm thu (DoD):**
  - Đầu ra số đo có độ lệch $\le 3\text{cm}$ so với số đo người mẫu thực tế.

---

### MODULE 5: Backend Fit & Size Recommendation Engine `[BE]`

- **Nhiệm vụ:**
  - Chuyển toàn bộ logic tính toán từ `frontend/services/fitEngine.ts` lên xử lý phía server tại `POST /api/v1/pipeline/size-recommend`.
  - Tính điểm khớp (Fit Score) cho từng kích thước (XS, S, M, L, XL, XXL) theo công thức sai phân:
    $$\Delta = \text{Garment Spec} - \text{Body Measurement}$$
    - Đối chiếu theo từng bộ phận: Vai, Ngực, Eo, Hông, Dài áo.
    - Áp dụng trọng số ưu tiên: Vai (35%), Ngực (35%), Eo/Hông (20%), Dài áo (10%).
    - Bù trừ theo độ co giãn (`fabric_stretch`: none = 0cm, low = +2cm, medium = +4cm, high = +6cm).
    - Điều chỉnh theo gu mặc (`slim`: ưu tiên $\Delta \approx 1-3\text{cm}$, `regular`: $\Delta \approx 4-7\text{cm}$, `relaxed`: $\Delta \approx 8-12\text{cm}$).
  - Tự động sinh `summary_explanation` bằng template tiếng Việt (không dùng LLM ngoài để đảm bảo độ trễ < 20ms).
- **Files mục tiêu:**
  - `backend/app/api/endpoints/size_recommend.py`
  - `backend/app/services/fit_engine_service.py`

---

### MODULE 6: CatVTON Microservice Integration (`vto-service`) `[BE]`

- **Nhiệm vụ:**
  1. **Container tách biệt:** Xây dựng `vto-service/Dockerfile` chạy môi trường PyTorch + CUDA, tải checkpoint CatVTON (899M params).
  2. **FastAPI Job Manager (`/api/v1/tryon/jobs`):**
     - Endpoint nhận request, sinh `job_id`, lưu bản ghi vào bảng `tryon_jobs` với `status: queued`, trả về HTTP `202 Accepted` ngay lập tức.
     - Hỗ trợ header `Idempotency-Key` để tránh tạo trùng job trên GPU.
     - Background Worker đẩy tác vụ sang `vto-service` qua HTTP nội bộ (`http://vto-service:8001/infer`).
     - Khi GPU hoàn thành sinh ảnh, lưu ảnh kết quả vào Supabase Storage `fitting-tryon-results`, cập nhật `status: completed` và `result_image_url`.
  3. **Polling Endpoint:** `GET /api/v1/tryon/jobs/{job_id}` trả về tiến độ xử lý.
- **Tiêu chuẩn nghiệm thu (DoD):**
  - Thời gian xử lý CatVTON nội bộ < 15 giây trên GPU NVIDIA (>= 8GB VRAM).
  - Nếu GPU quá tải hoặc crash, trả về mã lỗi `503 Service Unavailable`, không làm sập server chính.

---

### MODULE 7: Frontend-to-Backend Bridge (Cầu Nối Đồng Bộ) `[FE]`

- **Nhiệm vụ:**
  - Xây dựng file `frontend/services/apiClient.ts` cấu hình Axios/Fetch wrapper chuẩn hóa header `X-Session-ID`.
  - Thay thế các lời gọi dữ liệu tĩnh từ `mockFittingData.ts` sang gọi API thật thông qua một Feature Flag duy nhất:
    ```typescript
    // frontend/config/features.ts
    export const USE_REAL_BACKEND_API = process.env.NEXT_PUBLIC_USE_BACKEND === 'true';
    ```
  - Khi bật flag, toàn bộ dữ liệu Garments, Quality Check, Measurements, Recommendation và VTO sẽ gọi trực tiếp về FastAPI.

---

## 3. Thứ tự Triển khai Dự kiến (Execution Roadmap)

```
[Hoàn thành Frontend Mock Demo]
               │
               ▼
[MODULE 1: Database & Seed 50 Sản phẩm vào Supabase]
               │
               ▼
[MODULE 2: FastAPI CRUD Endpoints (Garments & Profiles)]
               │
               ▼
[MODULE 5: Backend Fit Recommendation Engine]
               │
               ▼
[MODULE 3 & 4: MediaPipe Quality Gate & Anthropometric Measurement]
               │
               ▼
[MODULE 6: CatVTON Microservice GPU Container & Try-On Queue]
               │
               ▼
[MODULE 7: Chuyển đổi Feature Flag trên Frontend sang Live API]
```
