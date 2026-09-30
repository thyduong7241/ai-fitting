# Tasks: Vision Microservice (`vision-service`) & Quantitative Benchmark Framework

> **Plan Document:** [plan.md](file:///home/aiuser4/nttduong/ai-fitting/tasks/plan.md)  
> **Master Spec:** [VISION_SERVICE_MICROSERVICE_AND_BENCHMARK_PLAN.md](file:///home/aiuser4/nttduong/ai-fitting/docs/plans/VISION_SERVICE_MICROSERVICE_AND_BENCHMARK_PLAN.md)  
> **Repository Constraints:** [CONSTRAINTS.md](file:///home/aiuser4/nttduong/ai-fitting/CONSTRAINTS.md)

---

## Phase 1: Service Skeleton, Data Schemas & Container Infrastructure

### Task 1: Khởi tạo cấu trúc `vision-service`, dependencies & Pydantic Data Models

**Description:** Thiết lập khung sườn microservice FastAPI cho `vision-service`, cấu hình cấu trúc thư mục chuẩn (`app/`, `tests/`, `benchmark/`), file `requirements.txt` với các dependencies cần thiết (`mediapipe`, `opencv-python-headless`, `scipy`, `numpy`, `fastapi`, `uvicorn`, `pydantic`), và định nghĩa đầy đủ các Pydantic schema cho request/response khớp với OpenAPI spec và `backend/app/models/fitting.py`.

**Acceptance criteria:**
- [x] Cấu trúc thư mục `vision-service/app/{api,core,engines,models,services}` được tạo đầy đủ.
- [x] `requirements.txt` liệt kê rõ phiên bản tương thích: `mediapipe>=0.10.14`, `opencv-python-headless>=4.9.0`, `scipy>=1.11.0`, `numpy>=1.26.0`, `fastapi>=0.110.0`, `uvicorn[standard]>=0.28.0`, `pydantic>=2.6.0`, `httpx>=0.27.0`, `pytest>=8.0.0`.
- [x] `vision-service/app/models/vision.py` định nghĩa đầy đủ `QualityCheckRequest`, `QualityCheckResponse`, `MeasurementRequest`, `MeasurementResponse`, `EngineMetadata` đồng bộ 100% với `backend/app/models/fitting.py`.
- [x] Endpoint `/health` trả về `{"status": "healthy", "service": "vision-service"}`.

**Verification:**
- [x] Tests pass: `cd vision-service && pytest tests/test_models.py`
- [x] Build succeeds: `python -c "import app.models.vision; print('Models valid')"` trong môi trường ảo
- [x] Manual check: Khởi chạy `uvicorn app.main:app --port 8002` và kiểm tra `http://localhost:8002/health` trả về status 200.

**Dependencies:** None

**Files likely touched:**
- `vision-service/requirements.txt`
- `vision-service/app/main.py`
- `vision-service/app/core/config.py`
- `vision-service/app/models/vision.py`
- `vision-service/tests/test_models.py`

**Estimated scope:** Medium (4-5 files)

---

### Task 2: Xây dựng Strategy Base Interfaces & Dynamic Engine Registry

**Description:** Cài đặt kiến trúc Strategy Pattern cho phép cắm/rút nhiều trường phái mô hình thị giác. Xây dựng hai abstract class `BaseQualityGateEngine` và `BaseMeasurementEngine` với chữ ký phương thức chuẩn, kèm theo `EngineRegistry` để đăng ký, tìm nạp và tự động kích hoạt engine theo cấu hình môi trường (`VISION_MEASUREMENT_ENGINE`) hoặc theo request parameter/header.

**Acceptance criteria:**
- [x] `vision-service/app/engines/base.py` cung cấp đầy đủ `BaseQualityGateEngine` và `BaseMeasurementEngine` kế thừa `abc.ABC`.
- [x] `vision-service/app/engines/registry.py` quản lý danh mục engine đăng ký qua decorator hoặc registry dict, hỗ trợ tìm nạp engine mặc định hoặc theo `engine_id`.
- [x] Hỗ trợ fallback an toàn nếu `engine_id` không tồn tại (ném exception có thông điệp rõ ràng).
- [x] Có unit test kiểm thử cơ chế đăng ký và chuyển đổi engine.

**Verification:**
- [x] Tests pass: `cd vision-service && pytest tests/test_engine_registry.py -v`
- [x] Build succeeds: Không phát sinh lỗi cú pháp hay typing.

**Dependencies:** Task 1

**Files likely touched:**
- `vision-service/app/engines/base.py`
- `vision-service/app/engines/registry.py`
- `vision-service/app/engines/__init__.py`
- `vision-service/tests/test_engine_registry.py`

**Estimated scope:** Medium (3-4 files)

---

### Task 3: Cấu hình Dockerfile & Tích hợp `docker-compose.yml` (Port 8002)

**Description:** Xây dựng `Dockerfile` tối ưu hóa cho `vision-service` trên nền `python:3.11-slim`, cài đặt các thư viện hệ thống C++ cần cho OpenCV/MediaPipe (`libgl1-mesa-glx`, `libglib2.0-0`, `libgomp1`), chạy dưới quyền non-root user. Thêm service `vision-service` vào `docker-compose.yml` lắng nghe trên port `8002` trong mạng `app-network`.

**Acceptance criteria:**
- [x] `vision-service/Dockerfile` build thành công không lỗi, kích thước image được tối ưu.
- [x] `docker-compose.yml` khai báo service `vision-service`, expose port `8002:8002`, kết nối cùng `app-network` với `backend` và `supabase`.
- [x] Healthcheck được cấu hình trong docker-compose ping `/health` định kỳ.

**Verification:**
- [x] Build succeeds: `docker compose build vision-service` hoặc `docker build -t vision-service:dev vision-service/`
- [x] Manual check: `docker compose up -d vision-service && curl -s http://localhost:8002/health` trả về status 200.

**Dependencies:** Task 1, Task 2

**Files likely touched:**
- `vision-service/Dockerfile`
- `vision-service/.dockerignore`
- `docker-compose.yml`

**Estimated scope:** Small (2-3 files)

---

### Checkpoint 1: Foundation Checkpoint
- [x] `vision-service` khởi động sạch trên port 8002 và response endpoint `/health`.
- [x] Pydantic Schemas khớp 100% với backend models.
- [x] Engine Registry sẵn sàng cho việc cắm các implementation cụ thể.

---

## Phase 2: Quantitative Benchmark Harness & Test Fixture Dataset

### Task 4: Xây dựng Test Fixture Dataset & Ground Truth Schema (`ground_truth.json`)

**Description:** Thiết lập cấu trúc thư mục dữ liệu kiểm định `benchmark/datasets/` với 15 bộ dữ liệu đo chuẩn có số đo thước dây thực tế trong `ground_truth.json` (đa dạng vóc dáng, giới tính, BMI) và 25 ảnh kiểm thử các lỗi Quality Gate (cắt chân, cắt đầu, ảnh mờ, thiếu sáng, sai tư thế). Cung cấp script tự động tạo/tải synthetic fixture ảnh phục vụ CI/CD tự động khi chưa có đủ ảnh thật.

**Acceptance criteria:**
- [x] `benchmark/datasets/ground_truth.json` chứa ít nhất 15 đối tượng chuẩn có số đo: vai, ngực, eo, hông, arm length, inseam, chiều cao và cân nặng.
- [x] Thư mục `benchmark/datasets/images/` được phân nhóm rõ ràng: `valid/`, `blurry/`, `cut_feet/`, `cut_head/`, `bad_lighting/`, `bad_pose/`.
- [x] Cung cấp script `benchmark/datasets/generate_fixtures.py` để tự động khởi tạo fixture placeholder ảnh hợp lệ và ảnh lỗi khi chạy trong môi trường dev/CI.

**Verification:**
- [x] Tests pass: `cd vision-service && python benchmark/datasets/generate_fixtures.py --verify`
- [x] Build succeeds: Kiểm tra tính hợp lệ cú pháp JSON của `ground_truth.json`.

**Dependencies:** Task 1

**Files likely touched:**
- `vision-service/benchmark/datasets/ground_truth.json`
- `vision-service/benchmark/datasets/generate_fixtures.py`
- `vision-service/benchmark/datasets/schema.py`

**Estimated scope:** Small (2-3 files)

---

### Task 5: Phát triển Benchmark Runner & Ratchet Guard Engine (`run_benchmark.py`)

**Description:** Xây dựng CLI test runner `benchmark/run_benchmark.py` thực hiện đánh giá định lượng tự động cho toàn bộ hệ thống: đo Latency (P50/P95), tính Confusion Matrix, Precision, Recall, F1-Score cho Quality Gate; tính MAE, MAPE, Repeatability ($\sigma$), Tolerance Pass Rate ($\pm 3\text{cm}$) cho Measurement. Tích hợp cơ chế Ratchet Guard đối chiếu với `baseline_scores.json` và throw error nếu có bất kỳ chỉ số nào bị suy giảm.

**Acceptance criteria:**
- [x] `run_benchmark.py` hỗ trợ các cờ lệnh: `--suite [all|quality|measurement]`, `--check-ratchet`, `--save-baseline`, `--compare`, `--output-report`.
- [x] Tính toán chính xác các công thức thống kê theo đúng Mục 3.1 của tài liệu kiến trúc.
- [x] Khi chạy `--check-ratchet`, script tự động exit code 1 nếu F1-Score < 96% hoặc MAE > ngưỡng cam kết hoặc tụt so với `baseline_scores.json`.
- [x] Xuất báo cáo Markdown chi tiết vào `benchmark/reports/` hoặc stdout.

**Verification:**
- [x] Tests pass: `cd vision-service && python benchmark/run_benchmark.py --dry-run`
- [x] Manual check: Kiểm tra cờ `--check-ratchet` kích hoạt đúng khi cố tình giảm ngưỡng giả lập.

**Dependencies:** Task 4

**Files likely touched:**
- `vision-service/benchmark/run_benchmark.py`
- `vision-service/benchmark/metrics.py`
- `vision-service/benchmark/baseline_scores.json`
- `vision-service/benchmark/generate_report.py`

**Estimated scope:** Medium (3-4 files)

---

### Checkpoint 2: Benchmark Harness Ready
- [x] `run_benchmark.py` chạy độc lập, đọc dữ liệu ground truth và tính toán chỉ số thống kê chuẩn xác.
- [x] Ratchet Guard sẵn sàng kiểm soát chất lượng cho các task cài đặt thuật toán tiếp theo.

---

## Phase 3: Single-Pass Quality Gate Engine Tinh gọn

### Task 6: Singleton MediaPipe Pose Detector, Resolution Gate ($800\times 600$) & Person Presence

**Description:** Xây dựng `MediaPipePoseDetector` dạng Singleton nạp model Pose Landmarker một lần duy nhất trong lifecycle của `vision-service` (CPU optimized). Triển khai Resolution Gate (kiểm tra nhanh $H \ge 800$ và $W \ge 600$ trước khi đưa vào model) và Person Presence (suy luận 1 lượt Pose, nếu không phát hiện khung xương trả về lỗi `no_person`). Tái sử dụng mốc Pose 33 landmarks cho toàn bộ các bước kiểm định và đo đạc sau đó.

**Acceptance criteria:**
- [x] `MediaPipePoseDetector` quản lý session an toàn luồng, không khởi tạo lại model ở mỗi request; không dùng model Face riêng.
- [x] Kiểm tra nhanh độ phân giải ảnh: $H < 800$ hoặc $W < 600 \rightarrow$ thêm lỗi `low_resolution`.
- [x] Trả về `is_valid: False` kèm lỗi `no_person` nếu không nhận diện được khung xương người.
- [x] Unit tests kiểm tra cả ảnh hợp lệ, ảnh độ phân giải thấp và ảnh không có người.

**Verification:**
- [x] Tests pass: `cd vision-service && pytest tests/test_pose_and_presence.py -v`
- [x] Build succeeds: Thời gian suy luận Pose đơn lượt $< 25\text{ms}$ trên CPU.

**Dependencies:** Task 1, Task 2

**Files likely touched:**
- `vision-service/app/core/mediapipe_detector.py`
- `vision-service/tests/test_pose_and_presence.py`

**Estimated scope:** Small (2 files)

---

### Task 7: Boundary Cut-Off Detection & Occlusion Keypoint Visibility Check

**Description:** Cài đặt hàm kiểm tra cắt viền ảnh và vật thể lạ che khuất cơ thể: ước lượng vị trí đỉnh đầu $y_{\text{crown}} = y_{\text{nose}} - 1.2 \times |y_{\text{ear}} - y_{\text{nose}}|$, báo lỗi `head_cut_off` nếu $y_{\text{crown}} \le 0.02$; kiểm tra ngón/gót chân (mốc 29-32) báo lỗi `feet_cut_off` nếu $y_{\text{toe}} \ge 0.98$ hoặc visibility $< 0.5$. Đồng thời kiểm tra điểm `visibility` của 6 mốc cốt lõi (vai 11-12, hông 23-24, gối 25-26), nếu bất kỳ mốc nào $< 0.60$ (do túi xách, tay cầm điện thoại trước ngực che lấp) $\rightarrow$ báo lỗi `body_occluded`.

**Acceptance criteria:**
- [x] Phát hiện chính xác `head_cut_off`, `feet_cut_off` và `body_occluded` trực tiếp từ dữ liệu 33 landmarks.
- [x] Trả về mảng `cut_off_boxes: List[BoundingBox]` với tọa độ chuẩn hóa `[ymin, xmin, ymax, xmax]` cho mép trên/dưới bị vi phạm.
- [x] Unit tests cho các kịch bản: ảnh toàn thân chuẩn, ảnh cắt đầu, ảnh cắt chân, ảnh bị túi xách/vật cầm tay che mốc hông/vai.

**Verification:**
- [x] Tests pass: `cd vision-service && pytest tests/test_cutoff_and_occlusion.py -v`
- [x] Build succeeds: Không thêm bất kỳ thư viện hoặc model ngoại vi nào.

**Dependencies:** Task 6

**Files likely touched:**
- `vision-service/app/services/quality_gate.py`
- `vision-service/tests/test_cutoff_and_occlusion.py`

**Estimated scope:** Small (2 files)

---

### Task 8: Pose Orientation Check & Fast OpenCV ROI Blur / Lighting Check

**Description:** Hoàn thiện hàm kiểm tra tư thế (Front: $|Z_{11} - Z_{12}| \le 0.20$; Side: bề rộng vai chiếu ngang co lại $< 35\%$) và kiểm tra nhanh ánh sáng / độ sắc nét trong cùng module `quality_gate.py`. Crop nhanh vùng thân (vai mốc 11 $\to$ gối mốc 25) để loại trừ nền: tính giá trị trung bình mức xám `gray_roi.mean() < 40 or > 225 -> bad_lighting` (< 1ms); tính phương sai Laplacian `cv2.Laplacian(gray_roi).var() < 100.0 -> blurry_image` (< 5ms).

**Acceptance criteria:**
- [x] Phân loại chính xác tư thế Front vs Side, cảnh báo nếu ảnh Front mà người đứng xoay chéo ($|Z_{11} - Z_{12}| > 0.20$).
- [x] Bắt chính xác ảnh mờ rung tay (`blurry_image`) và ảnh thiếu sáng/cháy sáng (`bad_lighting`) bằng OpenCV thuần.
- [x] Toàn bộ logic 6 tầng kiểm định nằm gọn trong 1 file `quality_gate.py` (~50-60 dòng code).

**Verification:**
- [x] Tests pass: `cd vision-service && pytest tests/test_quality_evaluator.py -v`
- [x] Build succeeds: Tổng thời gian thực thi hàm `evaluate_quality` $< 30\text{ms}$.

**Dependencies:** Task 6, Task 7

**Files likely touched:**
- `vision-service/app/services/quality_gate.py`
- `vision-service/tests/test_quality_evaluator.py`

**Estimated scope:** Small (2 files)

---

### Task 9: Quality Gate Router (`/api/v1/quality-check`) & Benchmark Tuning (F1 $\ge 96\%$, Latency P95 $\le 35\text{ms}$)

**Description:** Đóng gói engine `SinglePassQualityGateEngine` kế thừa `BaseQualityGateEngine`, đăng ký vào `EngineRegistry`. Xây dựng FastAPI Router `POST /api/v1/quality-check` nhận file ảnh qua multipart form-data. Chạy benchmark tuning trên tập dữ liệu `benchmark/datasets/` để đạt các chỉ số cam kết: F1-Score Cut-off $\ge 96\%$, Blur Accuracy $\ge 92\%$, False Rejection $\le 3\%$, Latency P95 $\le 35\text{ms}$.

**Acceptance criteria:**
- [x] `POST /api/v1/quality-check` tiếp nhận upload ảnh, gọi `evaluate_quality` và trả về `QualityCheckResponse` theo chuẩn OpenAPI.
- [x] Kết quả kiểm tra đạt toàn bộ chỉ số cam kết khi chạy suite benchmark quality.
- [x] Xử lý an toàn các lỗi giải mã ảnh (HTTP 400).

**Verification:**
- [x] Tests pass: `cd vision-service && python benchmark/run_benchmark.py --suite quality --check-ratchet`
- [x] Manual check: Dùng `curl -X POST -F "image=@benchmark/datasets/images/valid/subject_01_front.jpg" -F "image_type=front" http://localhost:8002/api/v1/quality-check` nhận `is_valid: true` trong $< 50\text{ms}$.

**Dependencies:** Task 8, Task 5

**Files likely touched:**
- `vision-service/app/engines/quality_gate.py`
- `vision-service/app/api/v1/quality_check.py`
- `vision-service/tests/test_quality_endpoint.py`

**Estimated scope:** Small (3 files)

---

### Checkpoint 3: Quality Gate Validated
- [x] Endpoint `/api/v1/quality-check` hoạt động trơn tru.
- [x] Benchmark Quality Gate vượt qua 100% KPI: F1-Score Cut-off $\ge 96.0\%$, Blur Accuracy $\ge 92.0\%$, False Rejection $\le 3.0\%$, Latency P95 $\le 35\text{ms}$ (nhanh gấp 3 lần so với kế hoạch cũ).

---

## Phase 4: Hybrid 2-View Stereometry & Smart Fit Notes Engine (`hybrid_stereometry_2d`)

### Task 10: Pixel-to-Metric (P2M) Calibration & Đo Tuyến Tính Xương Khớp (Vai, Tay, Chân)

**Description:** Cài đặt module tính toán hệ số quy đổi Pixel-to-Metric từ đỉnh đầu toán học $y_{\text{crown}} = y_{\text{nose}} - 1.2 \times |y_{\text{ear}} - y_{\text{nose}}|$ đến điểm tiếp đất giữa hai gót chân $y_{\text{heel}} = \frac{1}{2}(y_{29} + y_{30})$: $\text{Scale } S = H_{\text{known}} / |y_{\text{heel}} - y_{\text{crown}}|$ (cm/pixel). Đo tuyến tính các khớp xương: Rộng vai mỏm cùng (11-12) $\times S \times 1.10$ (bù cơ delta), Dài tay 3 khớp (Vai 11 $\to$ Khuỷu 13 $\to$ Cổ tay 15) $\times S$, và Dài chân trong Inseam (Háng $\to$ Gối 25 $\to$ Mắt cá 27) $\times S$.

**Acceptance criteria:**
- [x] Hàm `calculate_p2m_scale` tính chính xác tỷ lệ $\text{cm/pixel}$ dựa trên `known_height_cm` và tọa độ pixel đỉnh đầu/gót chân.
- [x] Đo chính xác `shoulder_cm`, `arm_length_cm`, `inseam_cm` với sai số MAE $< 1.5\text{cm}$ so với thước dây thực tế.
- [x] Tự động bù trừ góc nghiêng quang học camera nếu tỷ lệ đùi / cẳng chân lệch chuẩn.

**Verification:**
- [x] Tests pass: `cd vision-service && pytest tests/test_p2m_and_linear_bones.py -v`
- [x] Build succeeds: Tính toán trên ảnh mẫu ra hệ số P2M sai số $< 1\%$.

**Dependencies:** Task 6

**Files likely touched:**
- `vision-service/app/services/measurement/p2m_calibrator.py`
- `vision-service/app/services/measurement/linear_bones.py`
- `vision-service/tests/test_p2m_and_linear_bones.py`

**Estimated scope:** Small (3 files)

---

### Task 11: Lập Thể Chu Vi 3 Vòng (Ngực, Eo, Hông) 2-View Ramanujan + Tiền Nghiệm Tuổi & BMI

**Description:** Triển khai thuật toán đo chu vi lập thể kết hợp 2 ảnh chụp (Front + Side 90°): trích xuất bán trục ngang $a$ từ ảnh Front và bán trục sâu $b$ từ ảnh Side tại 3 lát cắt giải phẫu (Ngực: dưới nách 3cm; Eo: rốn/hẹp nhất; Hông: mấu chuyển lớn xương đùi). Tính chu vi cơ sở bằng xấp xỉ Ramanujan bậc cao $C_{\text{geo}} \approx \pi [3(a+b) - \sqrt{(3a+b)(a+3b)}]$. Tích hợp tiền nghiệm nhân trắc học theo tuổi và BMI: điều chỉnh chu vi eo dồn mỡ sau tuổi 25 ($k_{\text{waist}} = 1.0 + \max(0, \text{age} - 25) \times 0.0025 + (\text{BMI} - 21.5) \times 0.008$) và bù trừ thể tích ngực/hông.

**Acceptance criteria:**
- [x] Trích xuất chuẩn xác bán trục $a$ (Front) và $b$ (Side 90°) theo cùng hệ quy chiếu Metric.
- [x] Cài đặt công thức Ramanujan bậc cao an toàn toán học (không tràn số, không căn âm).
- [x] Tích hợp hệ số bù trừ thể tích theo `age`, `weight_kg`, `known_height_cm` (BMI) và `gender`.
- [x] Unit tests kiểm tra cả vóc dáng người trẻ (18-24) và người trưởng thành (>30 tuổi).

**Verification:**
- [x] Tests pass: `cd vision-service && pytest tests/test_stereometry_circumference.py -v`
- [x] Build succeeds: Sai số MAE đo chu vi 3 vòng $< 2.0\text{cm}$.

**Dependencies:** Task 10

**Files likely touched:**
- `vision-service/app/services/measurement/ramanujan_stereometry.py`
- `vision-service/app/services/measurement/anthropometric_prior.py`
- `vision-service/tests/test_stereometry_circumference.py`

**Estimated scope:** Small (3 files)

---

### Task 12: Hybrid Fallback Khi Thiếu Ảnh Side (Front Only + Tỷ Lệ Giải Phẫu)

**Description:** Xây dựng cơ chế fallback tự động khi người dùng chỉ cung cấp 1 ảnh Front (`side_image is None`): suy diễn bán trục sâu $b$ từ tương quan giải phẫu nhân trắc học ($b_{\text{chest}} = 0.72 \times a$, $b_{\text{waist}} = 0.68 \times a$, $b_{\text{hips}} = 0.85 \times a$), kết hợp bù trừ theo BMI và WHR quan sát được trên mặt trước. Trả về metadata ghi rõ phương pháp `ai_vision_hybrid_fallback` và giảm nhẹ `confidence_percent` xuống 85%.

**Acceptance criteria:**
- [x] Khi `side_image` là `None`, tự động suy luận chiều sâu và hoàn tất tính toán mà không bị crash.
- [x] Kết quả đo chu vi khi thiếu ảnh Side vẫn giữ sai số trong khoảng $\le \pm 2.5\text{cm}$.
- [x] Metadata trả về phản ánh chính xác trạng thái fallback.

**Verification:**
- [x] Tests pass: `cd vision-service && pytest tests/test_hybrid_fallback.py -v`
- [x] Build succeeds: Đảm bảo độ trễ không vượt quá $30\text{ms}$.

**Dependencies:** Task 11

**Files likely touched:**
- `vision-service/app/services/measurement/hybrid_fallback.py`
- `vision-service/tests/test_hybrid_fallback.py`

**Estimated scope:** Small (2 files)

---

### Task 13: Bộ Phân Loại Vóc Dáng, Sinh Smart Fit Notes & Router `/api/v1/measure`

**Description:** Xây dựng module phân loại hình thái vóc dáng (Đồng hồ cát, Quả lê, Quả táo, Chữ nhật, Tam giác ngược) dựa trên $WHR = \text{Waist} / \text{Hips}$ và $SHR = \text{Shoulder} / \text{Hips}$, sinh khuyến nghị chọn size thông minh (Smart Fit Notes: lưu ý áo vs quần/chân váy, tỷ lệ lưng/chân) theo template rule-based (0 gọi LLM bên ngoài). Đóng gói toàn bộ vào engine `HybridStereometryEngine`, đăng ký `EngineRegistry`, xây dựng router `POST /api/v1/measure` tiếp nhận `height_cm`, `weight_kg`, `age`, `gender`, ảnh và trả về `MeasurementResponse`. Chạy benchmark tuning đạt toàn bộ KPI.

**Acceptance criteria:**
- [x] `POST /api/v1/measure` nhận đầy đủ input (chiều cao, cân nặng, tuổi, giới tính, 2 ảnh) và trả về 6 số đo, `body_shape`, `smart_fit_notes`, `metrics` (bmi, whr, p2m_scale).
- [x] Sinh Smart Fit Notes hữu ích, chính xác theo từng dáng người và tỷ lệ cơ thể.
- [x] Vượt qua toàn bộ KPI đo đạc: MAE Vai $\le 1.5\text{cm}$, Eo $\le 2.0\text{cm}$, Ngực/Hông $\le 2.5\text{cm}$, Tolerance Pass Rate $\ge 90\%$, Latency P95 $\le 45\text{ms}$.

**Verification:**
- [x] Tests pass: `cd vision-service && python benchmark/run_benchmark.py --suite measurement --check-ratchet`
- [x] Manual check: Dùng `curl` test `/api/v1/measure` với fixture ảnh và kiểm tra nội dung `smart_fit_notes` trả về.

**Dependencies:** Task 12, Task 5

**Files likely touched:**
- `vision-service/app/services/measurement/smart_fit_notes.py`
- `vision-service/app/engines/hybrid_stereometry.py`
- `vision-service/app/api/v1/measure.py`
- `vision-service/tests/test_measure_endpoint.py`

**Estimated scope:** Medium (4 files)

---

### Checkpoint 4: Measurement Engine Validated
- [x] Endpoint `/api/v1/measure` hoạt động chính xác với đầy đủ 6 số đo, vóc dáng và Smart Fit Notes.
- [x] Benchmark Measurement vượt qua 100% KPI: MAE Vai $\le 1.5\text{cm}$, Eo $\le 2.0\text{cm}$, Ngực/Hông $\le 2.5\text{cm}$, Tolerance Pass Rate $\ge 90\%$, Latency P95 $\le 45\text{ms}$ trên CPU.

---

## Phase 5: Multi-Engine Pluggability & Comparison Tooling

### Task 14: Triển khai Adapter Stubs (`rtmpose_contour`, `shapy_3d`) & Công cụ Benchmark Đối Đầu (`--compare`)

**Description:** Xây dựng hai adapter stubs cho `rtmpose_contour` (SOTA 2.5D) và `shapy_3d` (SOTA 3D Mesh) tuân thủ `BaseMeasurementEngine`. Nếu môi trường thiếu GPU hoặc checkpoint mô hình chưa tải, adapter tự động báo trạng thái rõ ràng hoặc mô phỏng với dummy calibration. Nâng cấp script benchmark hỗ trợ cờ so sánh đối đầu song song đa engine: `python benchmark/run_benchmark.py --compare --engines anthropometric_2d,rtmpose_contour,shapy_3d` và xuất ra bảng so sánh `comparison_report.md`.

**Acceptance criteria:**
- [x] `RTMPoseContourEngine` và `Shapy3DEngine` được đăng ký vào `EngineRegistry`.
- [x] Hỗ trợ chuyển đổi engine động qua query parameter `?engine=...` hoặc header `X-Vision-Engine`.
- [x] Lệnh `run_benchmark.py --compare` chạy qua danh sách engine và sinh bảng so sánh Markdown theo mẫu tại Mục 2.4 của tài liệu kiến trúc.

**Verification:**
- [x] Tests pass: `cd vision-service && python benchmark/run_benchmark.py --compare --engines anthropometric_2d,rtmpose_contour`
- [x] Manual check: Kiểm tra nội dung bảng Markdown được tạo ra trong `benchmark/reports/comparison_report.md`.

**Dependencies:** Task 13, Task 5

**Files likely touched:**
- `vision-service/app/engines/rtmpose_contour.py`
- `vision-service/app/engines/shapy_3d.py`
- `vision-service/benchmark/run_benchmark.py`
- `vision-service/tests/test_multi_engines.py`

**Estimated scope:** Medium (4 files)

---

### Checkpoint 5: Multi-Engine Comparison
- [x] Kiến trúc Strategy Pattern hoạt động mượt mà cho 3 engine.
- [x] Báo cáo so sánh đối đầu Markdown được tạo tự động.

---

## Phase 6: Tích hợp Gateway Backend & Nghiệm thu Toàn diện

### Task 15: Cập nhật Backend Gateway (`quality_check_service.py`, `anthropometric_service.py`), HTTP Client & Circuit Breaker

**Description:** Cập nhật Web Backend FastAPI gọi sang `vision-service:8002` qua `httpx.AsyncClient`. Triển khai cơ chế Circuit Breaker và Graceful Fallback: nếu `vision-service` bận hoặc timeout (> 3s), trả về mã lỗi thích hợp hoặc fallback sang phương pháp ước lượng BMI cơ bản theo quy định của hệ thống.

**Acceptance criteria:**
- [x] `backend/app/services/quality_check_service.py` chuyển tiếp request kiểm tra ảnh sang `http://vision-service:8002/api/v1/quality-check`.
- [x] `backend/app/services/anthropometric_service.py` chuyển tiếp request đo cơ thể sang `http://vision-service:8002/api/v1/measure`.
- [x] Tích hợp timeout và xử lý ngoại lệ kết nối mà không làm sập tiến trình `backend`.
- [x] Unit test backend mock HTTP call sang `vision-service`.

**Verification:**
- [x] Tests pass: `cd backend && pytest tests/test_vision_integration.py -v`
- [x] Build succeeds: `backend` khởi động và kiểm tra typecheck sạch.

**Dependencies:** Task 9, Task 13

**Files likely touched:**
- `backend/app/services/quality_check_service.py`
- `backend/app/services/anthropometric_service.py`
- `backend/app/core/config.py`
- `backend/tests/test_vision_integration.py`

**Estimated scope:** Medium (4 files)

---

### Task 16: E2E Integration Testing & Xuất Báo cáo Nghiệm thu Tổng kết (`FINAL_BENCHMARK_REPORT.md`)

**Description:** Thực hiện kiểm thử tích hợp toàn diện từ Web Gateway tới `vision-service` với các kịch bản upload ảnh thực tế. Xuất báo cáo tổng kết nghiệm thu `vision-service/benchmark/reports/FINAL_BENCHMARK_REPORT.md` chứng minh toàn bộ các tiêu chuẩn chất lượng (Quality Gate F1-Score $\ge 96\%$, Measurement MAE $\le 1.5 - 2.5\text{cm}$, Tolerance Pass Rate $\ge 90\%$) đã được đáp ứng đầy đủ.

**Acceptance criteria:**
- [x] Kiểm thử E2E luồng Quality Check và Measure qua FastAPI Web Gateway thành công.
- [x] Báo cáo `FINAL_BENCHMARK_REPORT.md` được sinh ra với đầy đủ biểu đồ/bảng số liệu thực nghiệm.
- [x] Toàn bộ checklist trong `CONSTRAINTS.md` được thỏa mãn (0 lint error, 0 type error, không lộ secret).

**Verification:**
- [x] Tests pass: `cd vision-service && python benchmark/run_benchmark.py --suite all --check-ratchet`
- [x] Build succeeds: `docker compose up -d` khởi động tất cả services đồng thời và pass healthcheck.
- [x] Manual check: Đọc và xác nhận các chỉ số trong `FINAL_BENCHMARK_REPORT.md`.

**Dependencies:** Task 15, Task 14

**Files likely touched:**
- `vision-service/benchmark/reports/FINAL_BENCHMARK_REPORT.md`
- `docs/plans/tasks/todo.md`
- `README.md`

**Estimated scope:** Small (2-3 files)

---

### Checkpoint 6: End-to-End System Verified
- [x] Microservice `vision-service` chạy độc lập, ổn định trên Docker port 8002.
- [x] Backend Web Gateway tích hợp liền mạch qua HTTP.
- [x] 100% KPI chất lượng đạt chuẩn và được chứng minh bằng Benchmark Report định lượng.
