# Implementation Plan: Vision Microservice (`vision-service`) & Quantitative Benchmark Framework

> **Tài liệu tham chiếu:**
> - Kế hoạch gốc: `docs/plans/VISION_SERVICE_MICROSERVICE_AND_BENCHMARK_PLAN.md`
> - Tiêu chuẩn chất lượng: `CONSTRAINTS.md`
> - Quy tắc agent: `AGENTS.md`
> - API Contract: `docs/api/ai_precision_fit_api.yaml`
> - Backend Models: `backend/app/models/fitting.py`

## Overview

Tách toàn bộ logic xử lý thị giác máy tính (**Quality Gate** và **Body Measurement**) ra khỏi Web Backend (`backend`) thành một microservice độc lập **`vision-service`** (FastAPI, port `8002`, CPU isolated), áp dụng kiến trúc **Pluggable Strategy Pattern** với engine mặc định `anthropometric_2d` (MediaPipe Pose + Ramanujan Ellipse 2-View), đi kèm khung kiểm chuẩn định lượng tự động (**Quantitative Benchmark Harness**) đối chiếu Ground Truth thực tế, đảm bảo các tiêu chuẩn khắt khe về độ chính xác (F1 $\ge 96\%$, MAE $\le 1.5 - 2.5\text{cm}$) và bảo vệ suy giảm chất lượng (Ratchet Guard).

---

## Architecture Decisions

1. **Microservice Tách Biệt & Cổng Giao Tiếp HTTP Nội Bộ:**
   - `vision-service` chạy trên port `8002` trong cùng Docker network `app-network`.
   - `backend` (Web Gateway port `8000`) đóng vai trò điều phối, gọi sang `vision-service` qua `httpx.AsyncClient`. Tránh việc crash hoặc memory leak từ thư viện C++ (OpenCV, MediaPipe) làm sập Web API.
2. **Single-Pass Lean Quality Gate & Shared Pose Extraction:**
   - Khởi tạo MediaPipe Pose Landmarker dạng Singleton tái sử dụng giữa các request.
   - Quality Gate được thiết kế theo triết lý Ponytail: Tận dụng tối đa kết quả 33 landmarks của Pose model để kiểm tra đồng thời Person Presence, Cut-off, Occlusion (visibility), Pose Orientation.
   - Bỏ hoàn toàn Face Landmarker phụ (tiết kiệm ~150MB RAM).
   - Kiểm tra Blur (`cv2.Laplacian(roi).var()`) và Ánh sáng (`roi.mean()`) trực tiếp bằng OpenCV nhanh gọn, đạt độ trễ $\le 35\text{ms}$ trên CPU.
3. **Pluggable Strategy Pattern & Dynamic Registry (`hybrid_stereometry_2d`):**
   - Định nghĩa `BaseQualityGateEngine` và `BaseMeasurementEngine`.
   - Engine mặc định: `hybrid_stereometry_2d` (Stereometry 2-View Front/Side 90° + P2M Calibration + Chu vi Ramanujan + Tiền nghiệm Tuổi/BMI + Phân loại vóc dáng & Smart Fit Notes).
   - **Đặc tả I/O:**
     + **Input:** `known_height_cm` (float), `weight_kg` (float), `age` (int), `gender` (str), `front_image` (bytes), `side_image` (Optional[bytes]).
     + **Output:** 6 measurements (`shoulder_cm`, `chest_cm`, `waist_cm`, `hips_cm`, `arm_length_cm`, `inseam_cm`), `body_shape` ('dong_ho_cat', 'qua_le', 'qua_tao', 'chu_nhat', 'tam_giac_nguoc'), `smart_fit_notes` (List[str]), metrics (`bmi`, `whr`, `p2m_scale`).
   - Hỗ trợ đổi engine qua biến môi trường (`VISION_MEASUREMENT_ENGINE`) hoặc request param (`?engine=...`). Adapter stubs cho `rtmpose_contour` và `shapy_3d`.
4. **Benchmark-First Validation (Test Harness & Ratchet Guard):**
   - Xây dựng benchmark harness và bộ dữ liệu Ground Truth trước/song song với core algorithms.
   - Mỗi commit/task thuật toán đều chạy qua `run_benchmark.py` để verify chỉ số định lượng so với `baseline_scores.json`. Nếu bất kỳ chỉ số nào tụt giảm, chặn tiến trình (Ratchet rule).
5. **Đồng bộ Tuyệt đối API Contract:**
   - Mọi request/response schema của `vision-service` kế thừa hoặc đồng bộ 100% với Pydantic models trong `backend/app/models/fitting.py` và OpenAPI spec `docs/api/ai_precision_fit_api.yaml`.

---

## Dependency Graph

```
Phase 1: Foundation (Tasks 1 - 3)
   │
   ├── Pydantic Schemas & Service Skeleton
   ├── Pluggable Engine Strategy Interfaces & Registry
   └── Dockerfile & Docker Compose Setup
   │
Phase 2: Benchmark Harness & Dataset (Tasks 4 - 5)
   │
   ├── Ground Truth Schema & Image Fixtures Generator
   └── Benchmark Runner (Metrics, Confusion Matrix, Ratchet Guard)
   │
Phase 3: Quality Gate Engine (Tasks 6 - 9)
   │
   ├── MediaPipe Detector Singleton & ROI Blur (Layer 1 & 2)
   ├── Edge Cut-off: Crown & Heel Bounding Boxes (Layer 3)
   ├── Pose Orientation (Front/Side) & Illumination (Layer 4 & 5)
   └── Quality Check API Endpoint & Benchmark Tuning (F1 >= 96%)
   │
Phase 4: Anthropometric Measurement Engine (Tasks 10 - 13)
   │
   ├── P2M Scale Calibration & Slices Extraction
   ├── Ramanujan Circumference & 2-View Fusion (Front + Side)
   ├── Hybrid Fallback Regression (Front Only + BMI)
   └── Measurement API Endpoint & Benchmark Tuning (MAE <= 1.5 - 2.5cm)
   │
Phase 5: Multi-Engine Extensions & Benchmark Comparison (Task 14)
   │
   └── Stubs / Pluggable Adapters & Side-by-Side Comparison Tool
   │
Phase 6: Gateway Integration & E2E Verification (Tasks 15 - 16)
   │
   ├── Backend HTTP Client, Circuit Breaker & Fallback
   └── End-to-End Live Verification & Final Report
```

---

## Task List

### Phase 1: Service Skeleton, Data Schemas & Container Infrastructure
- [x] **Task 1:** Khởi tạo cấu trúc `vision-service`, dependencies & Pydantic Data Models
- [x] **Task 2:** Xây dựng Strategy Base Interfaces & Dynamic Engine Registry
- [x] **Task 3:** Cấu hình Dockerfile & Tích hợp `docker-compose.yml` (Port 8002)

#### Checkpoint 1: Foundation
- [x] `vision-service` khởi động thành công, endpoint `/health` trả về status 200.
- [x] Container build sạch, kết nối vào mạng `app-network`.

### Phase 2: Quantitative Benchmark Harness & Test Fixture Dataset
- [x] **Task 4:** Xây dựng Test Fixture Dataset & Ground Truth Schema (`ground_truth.json`)
- [x] **Task 5:** Phát triển Benchmark Runner & Ratchet Guard Engine (`run_benchmark.py`)

#### Checkpoint 2: Benchmark Harness Ready
- [x] `python benchmark/run_benchmark.py --dry-run` chạy thành công không crash.
- [x] Đọc đúng tập dữ liệu ground truth và sinh khung báo cáo `baseline_scores.json`.

### Phase 3: Single-Pass Quality Gate Engine Tinh gọn
- [x] **Task 6:** Singleton MediaPipe Pose Detector, Resolution Gate ($800\times 600$) & Person Presence
- [x] **Task 7:** Boundary Cut-Off (Đỉnh đầu, Gót/Ngón chân) & Occlusion Check (Visibility $< 0.60$)
- [x] **Task 8:** Pose Orientation & Fast OpenCV ROI Blur / Lighting Check (`quality_gate.py`)
- [x] **Task 9:** Quality Gate Router (`/api/v1/quality-check`) & Benchmark Tuning (F1 $\ge 96\%$, Latency P95 $\le 35\text{ms}$)

#### Checkpoint 3: Quality Gate Validated
- [x] `python benchmark/run_benchmark.py --suite quality` vượt qua toàn bộ ngưỡng KPI:
  - F1-Score (Cut-off) $\ge 96.0\%$
  - Blur Accuracy $\ge 92.0\%$
  - False Rejection Rate $\le 3.0\%$
  - Latency P95 $\le 35\text{ms}$ (CPU)

### Phase 4: Hybrid 2-View Stereometry & Smart Fit Notes Engine (`hybrid_stereometry_2d`)
- [x] **Task 10:** Pixel-to-Metric (P2M) Calibration & Đo tuyến tính xương khớp (Vai bù delta 1.10, Dài tay 3 khớp, Dài chân Inseam)
- [x] **Task 11:** Chu vi 3 Vòng (Ngực, Eo, Hông) qua Lập thể 2-View (Ramanujan Ellipse) tích hợp Tiền nghiệm Tuổi & BMI
- [x] **Task 12:** Hybrid Fallback Regression cho trường hợp chụp 1 ảnh (Front Only + Tỷ lệ nhân trắc học giải phẫu)
- [x] **Task 13:** Bộ Phân loại Vóc dáng & Sinh Smart Fit Notes, Router `/api/v1/measure` & Benchmark Tuning (MAE $\le 1.5 - 2.5\text{cm}$)

#### Checkpoint 4: Measurement Engine Validated
- [x] `python benchmark/run_benchmark.py --suite measurement` vượt qua toàn bộ ngưỡng KPI:
  - MAE Rộng vai $\le 1.5\text{cm}$
  - MAE Vòng eo $\le 2.0\text{cm}$
  - MAE Vòng ngực/hông $\le 2.5\text{cm}$
  - MAPE $\le 2.8\%$
  - Tolerance Pass Rate ($\pm 3\text{cm}$) $\ge 90\%$
  - Latency P95 $\le 45\text{ms}$ (CPU)
  - Phân loại đúng vóc dáng và sinh Smart Fit Notes may mặc chuẩn xác.

### Phase 5: Multi-Engine Pluggability & Comparison Tooling
- [x] **Task 14:** Triển khai Adapter Stubs (`rtmpose_contour`, `shapy_3d`) & Công cụ Benchmark Đối Đầu (`--compare`)

#### Checkpoint 5: Multi-Engine Comparison
- [x] `python benchmark/run_benchmark.py --compare --engines anthropometric_2d,rtmpose_contour,shapy_3d` xuất bảng Markdown so sánh đối đầu tự động.

### Phase 6: Tích hợp Gateway Backend & Nghiệm thu Toàn diện
- [x] **Task 15:** Cập nhật Backend Gateway (`quality_check_service.py`, `anthropometric_service.py`), HTTP Client & Circuit Breaker
- [x] **Task 16:** E2E Integration Testing & Xuất Báo cáo Nghiệm thu Tổng kết (`FINAL_BENCHMARK_REPORT.md`)

#### Checkpoint 6: End-to-End System Verified
- [x] Web Backend gọi xuyên suốt sang `vision-service` thành công với thời gian E2E $< 1.5\text{s}$ cho 2 ảnh.
- [x] Không có lỗi lint/type/test nào bị bỏ qua.
- [x] Báo cáo nghiệm thu `FINAL_BENCHMARK_REPORT.md` chứng minh 100% KPI đạt chuẩn.

---

## Risks and Mitigations

| Rủi ro (Risk) | Mức độ | Biện pháp giảm thiểu (Mitigation) |
|---|---|---|
| MediaPipe Pose không nhận diện được chân/đầu khi người đứng quá gần mép | High | Dùng công thức ngoại suy hình học: mốc 0 (mũi) + 7,8 (tai) ước lượng đỉnh đầu; mốc 27,28 (mắt cá) ước lượng chân khi ngón chân bị khuất. Trả về bounding box vùng lỗi. |
| Người dùng chỉ tải lên 1 ảnh Front (thiếu Side) | High | Tích hợp thuật toán hồi quy phi tuyến nhân trắc học dựa trên tương quan BMI, WHR và kích thước khung xương mặt trước để suy luận chiều sâu lồng ngực và bụng. |
| Tải tính toán MediaPipe làm tăng CPU Latency > 200ms | Medium | Chạy MediaPipe model complexity 1 (balanced), reuse singleton instance, crop ảnh về kích thước chuẩn (tối đa 1280px chiều dài nhất) trước khi suy luận. |
| Mạng nội bộ chập chờn giữa Backend và Vision Service | Low | Thiết lập Circuit Breaker với timeout 3s, retry tối đa 1 lần, trả về lỗi chi tiết theo schema Pydantic thay vì làm crash Backend. |

---

## Open Questions

- *Bộ ảnh benchmark:* Trong môi trường phát triển ban đầu, có thể tự động tạo ảnh synthetic test fixtures kết hợp ảnh chụp thực tế có sẵn trong repo để chạy benchmark mà không phụ thuộc dữ liệu bên ngoài.
