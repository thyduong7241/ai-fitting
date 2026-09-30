# AI Precision Fit — Kế hoạch Phát triển Microservice Thị giác (Vision Service) & Khung Benchmark Định lượng

> **Tài liệu tham chiếu:**
> - API Contract: `docs/api/ai_precision_fit_api.yaml`
> - Tiêu chuẩn chất lượng: `CONSTRAINTS.md`
> - Quy tắc agent: `AGENTS.md`
> - Task Tracker: `docs/plans/tasks/todo.md`
> - Backend Deferred Spec: `docs/plans/DEFERRED_BACKEND_AND_AI_INTEGRATION.md`

Tài liệu này đặc tả toàn diện việc tách, thiết kế chuyên sâu và kiểm chuẩn định lượng cho hai module cốt lõi: **Quality Gate** và **Body Measurement** thành một **Microservice độc lập (`vision-service`)**, đi kèm bộ công cụ **Benchmark tự động với dữ liệu Ground Truth thực tế**.

---

## 1. Lý do Kiến trúc & Mục tiêu Kỹ thuật

### 1.1. Tại sao cần tách thành Microservice riêng?

1. **Cô lập tài nguyên & Dependency (Resource & Library Isolation):**
   - MediaPipe Pose, OpenCV (`cv2`), NumPy, SciPy phụ thuộc vào nhiều thư viện C++ cấp hệ điều hành (`libGL`, `libglib`, `libgomp`) và tiêu tốn CPU/RAM đột biến khi xử lý ma trận ảnh.
   - Giữ cho `backend` (FastAPI Web Gateway) nhẹ, khởi động cực nhanh (< 2s), chỉ tập trung vào nghiệp vụ CRUD Profile, Garment Catalog, Fit Scoring, và bảo mật session.
   - Tránh hiện tượng một ngoại lệ hoặc rò rỉ bộ nhớ (memory leak) từ MediaPipe kéo sập toàn bộ REST API của hệ thống.
2. **Khả năng Mở rộng Độc lập (Independent Scalability):**
   - Tác vụ xử lý thị giác (Vision Pipeline) có chi phí CPU cao hơn gấp nhiều lần so với các thao tác đọc/ghi cơ sở dữ liệu.
   - Cho phép scale riêng `vision-service` (tăng số worker / container trên các lõi CPU chuyên dụng) theo tải thực tế mà không cần nhân bản Web Backend.
3. **Tối ưu hóa Pipeline (Single-Pass Inference):**
   - Cả hai bước **Quality Gate** và **Body Measurement** đều dùng chung MediaPipe Pose Landmarker (33 landmarks).
   - Đặt chung trong `vision-service` cho phép **chia sẻ kết quả trích xuất landmark**, giảm 50% thời gian xử lý ảnh so với việc tách thành hai service độc lập gọi riêng rẽ.

### 1.2. Vị trí Kiến trúc trong Hệ thống On-Premise

```
[ Frontend Widget (Next.js :3000) ]
                 │ (HTTP / REST)
                 ▼
[ Backend Web Gateway (FastAPI :8000) ]
        │                   │                   │
        ▼ (PostgreSQL)      ▼ (HTTP nội bộ)      ▼ (HTTP nội bộ)
[ Supabase DB :5432 ] [ vto-service :8001 ] [ vision-service :8002 ]
                      (GPU - CatVTON)       (Pluggable Vision Engines)
                                             ├── /api/v1/quality-check
                                             ├── /api/v1/measure?engine={id}
                                             └── /api/v1/benchmark/compare
```

---

## 2. Kiến trúc Đa Engine Dễ Thay đổi & So sánh (Pluggable Strategy Architecture)

Để giải quyết bài toán **dễ dàng chuyển đổi, cắm/rút (plug-and-play) và so sánh thực nghiệm giữa nhiều trường phái mô hình** mà không làm thay đổi API Contract hay ảnh hưởng tới Frontend/Backend, `vision-service` áp dụng **Strategy Pattern** và **Dynamic Engine Registry**.

### 2.1. Thiết kế Giao diện Thống nhất (Unified Engine Interface)

Mọi thuật toán hoặc mô hình (từ công thức 2D đến mô hình nơ-ron 3D) đều phải tuân thủ nghiêm ngặt Abstract Interface:

```python
# vision-service/app/engines/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.models.vision import QualityCheckResult, MeasurementResult

class BaseQualityGateEngine(ABC):
    @property
    @abstractmethod
    def engine_id(self) -> str:
        """Định danh engine: 'opencv_mediapipe' | 'rtmpose_quality'"""
        pass

    @abstractmethod
    async def evaluate(
        self, image_bytes: bytes, image_type: str = "front"
    ) -> QualityCheckResult:
        """Kiểm định chất lượng ảnh (Blur, Cut-off, Person count, Pose, Lighting)"""
        pass


class BaseMeasurementEngine(ABC):
    @property
    @abstractmethod
    def engine_id(self) -> str:
        """Định danh engine: 'hybrid_stereometry_2d' | 'rtmpose_contour' | 'shapy_3d'"""
        pass

    @abstractmethod
    async def measure(
        self,
        front_image: bytes,
        side_image: Optional[bytes],
        known_height_cm: float,
        weight_kg: float,
        age: int,
        gender: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> MeasurementResult:
        """
        Trích xuất 6 số đo nhân trắc học + Phân loại vóc dáng + Smart Fit Notes.
        Input: 2 ảnh (front + side 90°), chiều cao (cm), cân nặng (kg), tuổi, giới tính.
        Output: 6 số đo (vai, ngực, eo, hông, tay, chân), dáng người, lưu ý chọn size thông minh.
        """
        pass
```

### 2.2. Danh mục 3 Trường phái Approach Hỗ trợ (Pluggable Approaches)

Hệ thống thiết kế sẵn 3 Adapter tương ứng với 3 trường phái công nghệ:

| Approach ID | Tên Mô hình / Thuật toán | Input / Output | Cơ chế hoạt động | Ưu điểm cốt lõi | Yêu cầu phần cứng |
|---|---|---|---|---|---|
| `hybrid_stereometry_2d` *(Default)* | **Hybrid 2-View Stereometry + Anthropometric Prior** | **Input:** Height, Weight, Age, Gender + 2 ảnh Front/Side<br>**Output:** 6 số đo + Dáng người + Smart Fit Notes | MediaPipe Pose (33 landmarks) + Hiệu chuẩn P2M + Chu vi elip Ramanujan 2 góc chụp + Tiền nghiệm Tuổi/BMI | Siêu nhẹ, giải thích được 100%, không bản quyền, có phân tích vóc dáng | Thuần CPU (< 45ms) |
| `rtmpose_contour` *(SOTA 2.5D)* | **RTMPose + MobileSAM + Residual MLP** | **Input:** 2 ảnh + Metadata<br>**Output:** 6 số đo | 133 Keypoints + Bóc tách Silhouette mặt nạ + Mạng nơ-ron bù sai số theo BMI | Khắc phục sai số quần áo rộng, keypoint cực nhạy | CPU (< 200ms) hoặc GPU nhẹ |
| `shapy_3d` *(SOTA 3D Mesh)* | **SHAPY (SMPL 3D Parametric Mesh)** | **Input:** 1-2 ảnh + Metadata<br>**Output:** 6 số đo + 3D Mesh | Dự đoán Mesh 3D người trần (Under-clothes) $\rightarrow$ Cắt lát 3D polygon đo chu vi thực | Độ chính xác đỉnh cao ($\le 1\text{cm}$), chuẩn quốc tế | Cần GPU (VRAM $\ge 2\text{GB}$) |

### 2.3. Cơ chế Chuyển đổi Động (Dynamic Switching Mechanism)

Việc chuyển đổi approach diễn ra linh hoạt ở **3 cấp độ** mà không cần sửa code hay rebuild container:

1. **Cấp độ Cấu hình Môi trường (`.env`):**
   ```env
   # Chọn engine mặc định phục vụ toàn hệ thống
   VISION_MEASUREMENT_ENGINE=anthropometric_2d
   # Hoặc chuyển sang: rtmpose_contour / shapy_3d
   ```
2. **Cấp độ Từng Request (A/B Testing & Evaluation):**
   Frontend hoặc Backend Gateway có thể ghi đè engine theo từng cuộc gọi thông qua Query Param hoặc Header:
   - `POST /api/v1/measure?engine=rtmpose_contour`
   - Hoặc header: `X-Vision-Engine: shapy_3d`
3. **Phản hồi Kèm Metadata Đo đạc:**
   Response luôn trả về rõ metadata thuật toán nào đã được sử dụng và thời gian thực thi:
   ```json
   {
     "measurements": { "shoulder_cm": 37.2, "chest_cm": 84.1, "waist_cm": 66.3, "hips_cm": 90.2 },
     "confidence_percent": 94,
     "method": "ai_vision",
     "engine_metadata": {
       "engine_id": "rtmpose_contour",
       "inference_time_ms": 142.5,
       "device": "cpu"
     }
   }
   ```

### 2.4. Công cụ So sánh Đối đầu (Side-by-Side Comparison Benchmark Tool)

Để trả lời khách quan *"Approach nào tốt hơn trên tập dữ liệu thực tế?"*, script benchmark hỗ trợ cờ so sánh đa engine đồng thời:

```bash
# Lệnh so sánh đối đầu cùng lúc 3 approaches trên cùng tập Ground Truth
cd vision-service
python benchmark/run_benchmark.py --compare --engines anthropometric_2d,rtmpose_contour,shapy_3d
```

**Bảng báo cáo so sánh tự động xuất ra (`comparison_report.md`):**
```
| Tiêu chí Đánh giá          | anthropometric_2d | rtmpose_contour   | shapy_3d (GPU)   | Winner         |
|----------------------------|-------------------|-------------------|------------------|----------------|
| MAE Rộng vai (cm)          | 1.8 cm            | 1.3 cm            | 0.9 cm           | shapy_3d       |
| MAE Vòng ngực (cm)         | 2.6 cm            | 1.7 cm            | 1.2 cm           | shapy_3d       |
| MAE Vòng eo (cm)           | 2.4 cm            | 1.6 cm            | 1.1 cm           | shapy_3d       |
| MAE Vòng hông (cm)         | 2.7 cm            | 1.8 cm            | 1.2 cm           | shapy_3d       |
| MAPE Trung bình (%)        | 2.9 %             | 1.9 %             | 1.3 %            | shapy_3d       |
| Tỷ lệ lọt chuẩn (±3cm)     | 91.2 %            | 96.5 %            | 98.8 %           | shapy_3d       |
| Độ trễ P95 (Latency)       | 85 ms (CPU)       | 165 ms (CPU)      | 420 ms (GPU)     | anthropometric |
| Tiêu thụ Tài nguyên        | 250MB RAM         | 650MB RAM         | 2.1GB VRAM       | anthropometric |
| Rào cản Bản quyền          | Miễn phí / Mở     | Miễn phí / Mở     | Cần mua SMPL     | anthropo/rtm   |
```

---

## 3. Thiết kế Kỹ thuật Chi tiết Từng Engine

### 3.1. Quality Gate Engine — Tiếp cận Tinh gọn Đơn lượt (Lean Single-Pass Quality Gate)

Áp dụng nguyên tắc tối giản (Ponytail / YAGNI): **Tận dụng 1 lượt suy luận MediaPipe Pose Landmarker duy nhất** (chia sẻ trực tiếp với bước đo đạc) kết hợp các phép tính ma trận OpenCV cơ bản. Không nạp thêm model phụ (như Face Landmarker), không dùng phép toán phức tạp (Tenengrad/HSV histogram) để giữ độ trễ **$\le 35\text{ms}$** trên CPU và tiết kiệm tối đa RAM.

```
                      [ Upload Image (Front / Side) ]
                                     │
                 [ 1. Image Resolution Check (Fast Guard) ]
                 - h < 800 or w < 600 -> low_resolution (< 1ms)
                                     │
                 [ 2. Single MediaPipe Pose Inference ]
                 - Không thấy mốc người -> no_person
                 - Tái sử dụng kết quả 33 landmarks cho toàn bộ các bước sau
                                     │
      ┌──────────────────────────────┼──────────────────────────────┐
      ▼                              ▼                              ▼
[ 3. Boundary Cut-Off ]    [ 4. Occlusion Check ]       [ 5. Pose Orientation ]
- Đỉnh đầu: y_crown <= 0.02 - 8 mốc cốt lõi:            - Front: |Z11 - Z12| < 0.20
- Bàn chân: y_toe >= 0.98     visibility < 0.60         - Side: vai co hẹp chiếu ngang
  hoặc toe.vis < 0.5          -> body_occluded
      │                              │                              │
      └──────────────────────────────┼──────────────────────────────┘
                                     ▼
                 [ 6. Fast Body ROI Blur & Lighting (OpenCV) ]
                 - Crop thô vùng thân (vai mốc 11 -> gối mốc 25)
                 - Lighting: gray_roi.mean() < 40 hoặc > 225 -> bad_lighting
                 - Sharpness: cv2.Laplacian(gray_roi).var() < 100.0 -> blurry_image
                                     │
                                     ▼
                      [ Output: QualityCheckResponse ]
```

1. **Resolution Gate (Độ phân giải tối thiểu):**
   - Kiểm tra nhanh kích thước ma trận ảnh: $H \ge 800\text{px}$ và $W \ge 600\text{px}$. Loại bỏ ảnh vỡ hạt ngay trước khi đưa vào pipeline suy luận.
2. **Person Presence (Phát hiện người):**
   - Tận dụng `pose_landmarks`. Nếu không phát hiện khung xương $\rightarrow$ Báo lỗi `no_person`.
3. **Boundary Cut-off Detection (Cắt đầu / Cắt chân):**
   - **Đỉnh đầu (Head cut-off):** Tính vị trí ước lượng đỉnh đầu từ mốc 0 (mũi) và mốc 7, 8 (tai):
     $$y_{\text{crown}} = y_{\text{nose}} - 1.2 \times |y_{\text{ear}} - y_{\text{nose}}|$$
     Nếu $y_{\text{crown}} \le 0.02$ $\rightarrow$ Báo lỗi `head_cut_off`.
   - **Bàn chân (Feet cut-off):** Kiểm tra mốc 29, 30 (gót chân) và 31, 32 (ngón chân). Nếu $y_{\text{toe}} \ge 0.98$ hoặc điểm tin cậy mốc 31, 32 $< 0.5$ $\rightarrow$ Báo lỗi `feet_cut_off`.
4. **Occlusion & Keypoint Visibility (Vật thể lạ che khuất):**
   - Kiểm tra điểm `visibility` của 6 mốc giải phẫu cốt lõi: 11, 12 (vai), 23, 24 (hông), 25, 26 (gối).
   - Nếu bất kỳ mốc nào có $\text{visibility} < 0.60$ (do túi xách, tay cầm điện thoại trước ngực che lấp) $\rightarrow$ Báo lỗi `body_occluded`.
5. **Phân loại & Kiểm tra Tư thế (Pose Orientation):**
   - **Ảnh chính diện (Front):** Độ chênh lệch trục sâu $Z$ giữa 2 vai $|Z_{11} - Z_{12}| \le 0.20$.
   - **Ảnh góc nghiêng (Side):** Khoảng cách chiếu ngang giữa 2 mốc vai co lại $< 35\%$ so với ảnh Front.
6. **Fast ROI Blur & Lighting (Độ mờ & Ánh sáng tối ưu):**
   - Crop nhanh vùng thân (từ vai mốc 11 xuống gối mốc 25) để loại trừ hậu cảnh.
   - **Ánh sáng:** Dùng trực tiếp giá trị trung bình mức xám $\text{mean}(\text{gray\_roi})$. Quá tối ($< 40$) hoặc cháy sáng ($> 225$) $\rightarrow$ Báo lỗi `bad_lighting`.
   - **Độ sắc nét:** Tính phương sai toán tử Laplacian $\text{Var}(\text{Laplacian}(\text{gray\_roi})) < 100.0 \rightarrow$ Báo lỗi `blurry_image`.
7. **Các thành phần lược bỏ (YAGNI):**
   - *Bỏ MediaPipe Face model riêng:* Tận dụng các mốc mặt có sẵn trong Pose model (tiết kiệm ~150MB RAM).
   - *Bỏ phân tích hậu cảnh phức tạp & đo độ phồng áo:* Tránh false positives làm phiền người dùng; sai số quần áo được bù trừ ở Fit Engine.

---

### 3.2. Approach 1: Hybrid 2-View Stereometry with Anthropometric Prior (`hybrid_stereometry_2d`)

Tiếp cận cốt lõi kết hợp **Hình học Lập thể 2 góc chụp (Stereometry Front + Side 90°)** từ MediaPipe Pose sẵn có với **Tiền nghiệm Nhân trắc học giải phẫu theo Tuổi & BMI**, tối ưu hóa cho ứng dụng Mobile Web Widget chạy trên CPU Server nội bộ.

#### 3.2.1. Đặc tả Đầu vào & Đầu ra (Input & Output Specification)

```
┌────────────────────────────────────────────────────────────────────────┐
│ INPUT:                                                                 │
│ 1. Metadata người dùng:                                                │
│    - known_height_cm: float (Chiều cao thực tế, ví dụ: 165.0)           │
│    - weight_kg: float (Cân nặng thực tế, ví dụ: 52.0)                  │
│    - age: int (Độ tuổi, ví dụ: 28)                                     │
│    - gender: str ('female' | 'male')                                   │
│ 2. Dữ liệu hình ảnh:                                                   │
│    - front_image: bytes (Ảnh chính diện toàn thân)                     │
│    - side_image: Optional[bytes] (Ảnh nghiêng 90° toàn thân)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ OUTPUT (MeasurementResponse):                                          │
│ 1. measurements: (6 số đo cơ thể tính bằng cm, làm tròn 1 chữ số)      │
│    - shoulder_cm: float (Rộng vai mỏm cùng + bù cơ delta)              │
│    - chest_cm: float (Vòng ngực ngang nách)                            │
│    - waist_cm: float (Vòng eo hẹp nhất / ngang rốn)                    │
│    - hips_cm: float (Vòng hông ngang mấu chuyển xương đùi)             │
│    - arm_length_cm: float (Dài tay từ mỏm vai đến cổ tay)             │
│    - inseam_cm: float (Dài chân từ đũng quần đến mắt cá trong)         │
│ 2. body_shape: str ('dong_ho_cat' | 'qua_le' | 'qua_tao' |             │
│                     'chu_nhat' | 'tam_giac_nguoc')                     │
│ 3. smart_fit_notes: List[str] (Gợi ý/lưu ý thông minh khi chọn size)   │
│ 4. metrics:                                                            │
│    - bmi: float, whr: float (waist-to-hip ratio)                       │
│    - p2m_scale: float (cm/pixel), inference_time_ms: float             │
│ 5. confidence_percent: int (85 - 95%)                                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

#### 3.2.2. Chi tiết Thuật toán 4 Tầng

```
[ Front Image ] + [ Side Image 90° ] + [ Height, Weight, Age, Gender ]
                           │
                           ▼
          [ Tầng 1: P2M Metric Scale Calibration ]
          - y_crown = y_nose - 1.2 * |y_ear - y_nose|
          - y_heel = (y_29 + y_30) / 2
          - Scale S (cm/pixel) = known_height_cm / |y_heel - y_crown|
                           │
                           ▼
          [ Tầng 2: Đo Tuyến tính Xương Khớp (Vai, Tay, Chân) ]
          ├── Vai: dist(P11, P12) * S * 1.10 (Bù nở cơ delta)
          ├── Dài tay: [dist(P11, P13) + dist(P13, P15)] * S
          └── Dài chân (Inseam): [dist(P_crotch, P25) + dist(P25, P27)] * S
                           │
                           ▼
          [ Tầng 3: Đo 3 Vòng (Ngực, Eo, Hông) qua Lập thể 2-View + Prior ]
          - Lát cắt Ngực, Eo, Hông: lấy bán trục ngang 'a' (Front) & sâu 'b' (Side)
          - Chu vi Elip Ramanujan: C_geo ≈ π * [3(a+b) - sqrt((3a+b)(a+3b))]
          - Bù trừ Nhân trắc học theo Tuổi & BMI:
            C_waist = C_geo * [1.0 + max(0, age - 25) * 0.0025 + (BMI - 21.5) * 0.008]
                           │
                           ▼
          [ Tầng 4: Phân loại Vóc dáng & Sinh Smart Fit Notes ]
          - Tính WHR = Waist / Hips và SHR = Shoulder / Hips
          - Phân loại hình thái: Quả lê, Đồng hồ cát, Quả táo, Chữ nhật, Tam giác ngược
          - Sinh khuyến nghị chọn size áo vs size quần theo từng vùng cơ thể
```

1. **Tầng 1: Hiệu chuẩn Tỷ lệ Metric chuẩn (Pixel-to-Metric Scale):**
   - Xác định đỉnh đầu toán học: $y_{\text{crown}} = y_{\text{nose}} - 1.2 \times |y_{\text{ear}} - y_{\text{nose}}|$.
   - Điểm tiếp xúc mặt sàn: $y_{\text{heel}} = \frac{1}{2}(y_{29} + y_{30})$.
   - Tỷ lệ:
     $$S = \frac{H_{\text{known}}}{y_{\text{heel}} - y_{\text{crown}}} \quad (\text{cm/pixel})$$
   - Khử hoàn toàn sai số về khoảng cách đứng xa/gần camera của người dùng.

2. **Tầng 2: Đo Tuyến tính Xương khớp (Vai, Tay, Chân):**
   - **Rộng vai (Bi-acromial):** Đo khoảng cách giữa 2 mỏm cùng vai (mốc 11-12) $\times S \times 1.10$ (bù cơ delta).
   - **Dài tay (Arm Length):** Chuỗi Euclid 3 khớp: Vai (11) $\to$ Khuỷu (13) $\to$ Cổ tay (15) $\times S$.
   - **Dài chân (Inseam):** Trung điểm háng $\to$ Khớp gối (25) $\to$ Mắt cá chân trong (27) $\times S$.

3. **Tầng 3: Lập thể Chu vi 3 Vòng (Ngực, Eo, Hông) kết hợp Tuổi & BMI:**
   - **Trích xuất bán trục:**
     - Ngực: $a = \frac{1}{2} \text{Width}_{\text{chest\_front}} \times S$; $b = \frac{1}{2} \text{Depth}_{\text{chest\_side}} \times S$.
     - Eo: Lát cắt tại tiết diện hẹp nhất giữa sườn và xương chậu $\to a_{\text{waist}}$, $b_{\text{waist}}$.
     - Hông: Lát cắt ngang mấu chuyển lớn xương đùi (Trochanter) $\to a_{\text{hips}}$, $b_{\text{hips}}$.
   - **Công thức Ramanujan bậc cao:**
     $$C_{\text{geo}} \approx \pi \left[ 3(a+b) - \sqrt{(3a+b)(a+3b)} \right]$$
   - **Hiệu chuẩn theo Tuổi (Age Drift) & BMI:**
     - $\text{BMI} = \text{Weight} / (\text{Height}/100)^2$.
     - Sau tuổi 25, mô mỡ có xu hướng dồn về thành bụng ($0.25\%$/năm tuổi):
       $$C_{\text{waist}} = C_{\text{geo}} \times \left[ 1.0 + \max(0, \text{Age} - 25) \times 0.0025 + (\text{BMI} - 21.5) \times 0.008 \right]$$
   - **Fallback khi thiếu ảnh Side:** Suy diễn bán trục sâu $b$ từ tương quan nhân trắc học: $b_{\text{chest}} = 0.72 \times a$, $b_{\text{waist}} = 0.68 \times a$, $b_{\text{hips}} = 0.85 \times a$ kèm hệ số BMI.

4. **Tầng 4: Phân loại Vóc dáng & Sinh Gợi ý May mặc Thông minh (Smart Fit Notes):**
   - Dựa trên $WHR = \text{Waist} / \text{Hips}$ và chênh lệch giữa các vòng đo:
     - **Dáng quả lê ($WHR < 0.75$, Hips $-$ Chest $\ge 6\text{cm}$):** *"Dáng quả lê: Số đo hông lớn hơn vai/ngực. Nên chọn áo theo vai/ngực (Size M), nhưng Quần/Chân váy nên chọn theo vòng hông (Size L) để tránh bị chật đùi/mông."*
     - **Dáng đồng hồ cát ($WHR \le 0.73$, $|\text{Chest} - \text{Hips}| \le 4\text{cm}$):** *"Dáng đồng hồ cát cân đối: Phù hợp trang phục chiết eo tôn dáng; chọn size theo vòng ngực với áo và vòng eo với chân váy."*
     - **Dáng quả táo ($WHR > 0.85$ ở nữ hoặc $> 0.95$ ở nam):** *"Vòng bụng đầy đặn: Nên ưu tiên form relaxed-fit hoặc suông nhẹ, tránh áo bó sát gây kích bụng khi ngồi."*
     - **Tam giác ngược (Nam, Vai $\ge 43\text{cm}$, $WHR < 0.82$):** *"Khung vai rộng thể thao: Chú ý chọn áo theo số đo vai và ngực để tránh bị căng nách."*
     - **Tỷ lệ Chân/Lưng ($\text{Inseam} / \text{Height} < 0.45$):** *"Lưng dài hơn chân: Nên chọn quần cạp cao (high-rise) để tạo hiệu ứng tôn dài chân."*

---

### 3.3. Approach 2: SOTA 2.5D Silhouette + RTMPose + Residual Regressor (`rtmpose_contour`)

*Khắc phục nhược điểm lớn nhất của MediaPipe 2D:* Khi người dùng mặc đồ rộng hoặc áo phao phồng, đường viền ngoài ảnh hưởng đến số đo.

1. **RTMPose Keypoint Detector (MMPose):**
   - Thay thế MediaPipe bằng mô hình RTMPose thời gian thực (đạt mAP 75.8% trên COCO, cao hơn MediaPipe 18%).
   - Định vị chính xác các mốc giải phẫu sâu (Acromion, Trochanter, C7 Vertebrae) ngay cả khi bị vải áo che lấp.
2. **MobileSAM Silhouette Segmentation:**
   - Trích xuất Body Mask chuẩn xác đến từng pixel, tách riêng phần biên trang phục rủ xuống khỏi phần cơ thể thực tế.
3. **Mạng Nơ-ron Bù Sai số (Residual MLP Regressor):**
   - Lấy số đo hình học từ lát cắt elip làm giá trị Baseline.
   - Đưa vector đặc trưng $\mathbf{x} = [\text{Geometric Estimates}, \text{Silhouette Convexity}, \text{BMI}, \text{Gender}, \text{Waist-to-Hip Ratio}]$ qua mạng MLP nhỏ 3 tầng (hoặc XGBoost ONNX):
     $$\hat{y}_{\text{final}} = y_{\text{geometric}} + \Delta_{\text{learned}}(\mathbf{x})$$
   - Mạng học cách trừ hao độ dày vải quần áo tự động, giảm sai số MAE xuống còn **$\le 1.6\text{cm}$** mà vẫn chạy hoàn toàn trên CPU (< 180ms).

---

### 3.4. Approach 3: SOTA 3D Mesh Recovery — SHAPY (`shapy_3d`)

*Tiêu chuẩn vàng quốc tế của các nền tảng Virtual Fitting (3DLOOK, Zalando, Meshcapade).*

1. **Nguyên lý SHAPY (CVPR 2022):**
   - Mạng sâu dự đoán trực tiếp các vector tham số hình dạng $\boldsymbol{\beta} \in \mathbb{R}^{10}$ và dáng điệu $\boldsymbol{\theta}$ của mô hình tham số cơ thể người **SMPL**.
   - Được huấn luyện trên hàng chục nghìn dữ liệu quét 3D người thật (CAESAR Dataset), SHAPY có khả năng **"nhìn xuyên qua lớp quần áo" (Under-clothes body prediction)**, tái tạo cơ thể người trần thực tế bên dưới trang phục.
2. **Trích xuất Chu vi 3D (Geodesic 3D Cross-Section Slicing):**
   - Thay vì xấp xỉ elip 2D, hệ thống cắt các mặt phẳng giải phẫu trực tiếp qua 3D polygon mesh:
     - Mặt phẳng cắt ngang ngực (ngang nhũ hoa/nách) $\rightarrow$ Đo chu vi đa giác 3D.
     - Mặt phẳng cắt ngang rốn / hẹp nhất eo $\rightarrow$ Đo chu vi thực.
     - Mặt phẳng đỉnh cơ mông $\rightarrow$ Đo chu vi hông thực.
3. **Độ chính xác:** MAE đạt mức kỷ lục **$\le 1.0\text{cm}$**, nhưng yêu cầu máy chủ có GPU (VRAM $\ge 2\text{GB}$).

---

## 4. Khung Benchmark Định lượng (Evaluation & Benchmark Framework)

### 3.1. Chỉ số Đánh giá & Ngưỡng Chấp nhận (KPIs & Acceptance Gates)

Hệ thống bắt buộc vượt qua các bài test tự động với chỉ số định lượng khắt khe trước khi được coi là đạt chuẩn (DoD):

| Nhóm chức năng | Chỉ số (Metric) | Công thức định nghĩa | Ngưỡng cam kết (Target) | Cơ chế xử lý |
|---|---|---|---|---|
| **Quality Gate** | **F1-Score (Cut-off)** | $\frac{2 \cdot P \cdot R}{P + R}$ (phát hiện cắt đầu / cắt chân) | **$\ge 96.0\%$** | **BLOCK** nếu vi phạm |
| | **Blur Accuracy** | Tỷ lệ nhận diện đúng ảnh mờ vs nét | **$\ge 92.0\%$** | **BLOCK** nếu vi phạm |
| | **False Rejection Rate** | Ảnh chụp chuẩn nhưng bị từ chối | **$\le 3.0\%$** | **BLOCK** nếu vi phạm |
| | **Quality Latency (P95)** | Thời gian phản hồi kiểm tra ảnh (CPU) | **$\le 120\text{ms}$** | **WARN** nếu $> 150\text{ms}$ |
| **Measurement** | **MAE Rộng vai** | $\frac{1}{N} \sum \| \hat{y}_{\text{vai}} - y_{\text{vai}} \|$ | **$\le 1.5\text{cm}$** | **BLOCK** nếu vi phạm |
| | **MAE Vòng eo** | $\frac{1}{N} \sum \| \hat{y}_{\text{eo}} - y_{\text{eo}} \|$ | **$\le 2.0\text{cm}$** | **BLOCK** nếu vi phạm |
| | **MAE Vòng ngực / hông**| $\frac{1}{N} \sum \| \hat{y} - y \|$ | **$\le 2.5\text{cm}$** | **BLOCK** nếu vi phạm |
| | **MAPE (Toàn bộ)** | Sai số phần trăm tuyệt đối trung bình | **$\le 2.8\%$** | **BLOCK** nếu vi phạm |
| | **Tolerance Pass Rate** | Tỷ lệ mẫu có sai số $\le \pm 3.0\text{cm}$ | **$\ge 90.0\%$** | **BLOCK** nếu vi phạm |
| | **Repeatability ($\sigma$)** | Độ lệch chuẩn giữa 3 lần chụp cùng 1 người | **$\sigma \le 1.0\text{cm}$** | **BLOCK** nếu vi phạm |
| | **Measure Latency (P95)**| Thời gian đo 6 chỉ số (CPU) | **$\le 180\text{ms}$** | **WARN** nếu $> 200\text{ms}$ |

> *Ghi chú về Tolerance Pass Rate:* Trong ngành may mặc thời trang, bước nhảy giữa các size (size step) của áo sơ mi/khoác thường là $4.0\text{cm}$ vòng ngực và $4.0\text{cm}$ vòng eo. Sai số $\le 3.0\text{cm}$ đảm bảo tỷ lệ gợi ý đúng size đạt trên $95\%$.

---

### 3.2. Cấu trúc Thư mục Benchmark & Dữ liệu Ground Truth

Tất cả dữ liệu kiểm thử, script benchmark và kết quả nghiệm thu được lưu trữ tập trung tại `vision-service/benchmark/`:

```
vision-service/
├── app/
│   ├── api/v1/
│   │   ├── quality_check.py
│   │   ├── measure.py
│   │   └── benchmark_runner.py
│   ├── core/
│   │   ├── config.py
│   │   └── mediapipe_detector.py   # Singleton MediaPipe session
│   ├── services/
│   │   ├── quality_gate_engine.py  # 5-layer quality logic
│   │   └── measurement_engine.py   # P2M + Ramanujan stereometry
│   └── main.py
├── benchmark/
│   ├── datasets/
│   │   ├── ground_truth.json       # Bảng số đo thực tế đo bằng thước dây
│   │   └── images/
│   │       ├── valid/              # 15 bộ ảnh chuẩn (Front + Side)
│   │       ├── blurry/             # 5 ảnh mờ chuyển động/mất nét
│   │       ├── cut_feet/           # 5 ảnh cắt mép chân
│   │       ├── cut_head/           # 5 ảnh cắt mép đỉnh đầu
│   │       ├── bad_lighting/       # 5 ảnh ngược sáng/thiếu sáng
│   │       └── bad_pose/           # 5 ảnh bắt chéo chân/tay che ngực
│   ├── baseline_scores.json        # Snapshot điểm chuẩn hiện tại (Ratchet Guard)
│   ├── generate_report.py          # Render báo cáo Markdown/HTML
│   └── run_benchmark.py            # CLI test runner
├── Dockerfile
├── requirements.txt
└── README.md
```

#### Cấu trúc Schema `ground_truth.json`:
```json
[
  {
    "id": "subject_01",
    "gender": "female",
    "known_height_cm": 162.0,
    "weight_kg": 50.0,
    "front_image": "images/valid/subject_01_front.jpg",
    "side_image": "images/valid/subject_01_side.jpg",
    "ground_truth_cm": {
      "shoulder": 37.0,
      "chest": 84.0,
      "waist": 66.0,
      "hips": 90.0,
      "arm_length": 53.0,
      "inseam": 74.0
    }
  }
]
```

---

## 5. Kế hoạch Triển khai Chi tiết (Phased Execution Tasks)

### Phase V1: Khởi tạo Microservice & Hạ tầng Container (`vision-service`)
- [ ] **Task V1.1:** Khởi tạo thư mục `vision-service/` với cấu trúc FastAPI tiêu chuẩn, `requirements.txt` (`mediapipe>=0.10.14`, `opencv-python-headless>=4.9.0`, `scipy>=1.11.0`, `numpy>=1.26.0`, `fastapi`, `uvicorn`, `pydantic`).
- [ ] **Task V1.2:** Viết `Dockerfile` tối ưu trên nền `python:3.11-slim`, cài đặt các thư viện hệ thống cần thiết (`libgl1-mesa-glx`, `libglib2.0-0`), cấu hình non-root user.
- [ ] **Task V1.3:** Định nghĩa Router `/api/v1/quality-check` và `/api/v1/measure` khớp 100% Pydantic schema với `backend/app/models/fitting.py` và OpenAPI contract.
- [ ] **Task V1.4:** Cập nhật `docker-compose.yml`: Bổ sung service `vision-service` chạy trên port `8002`, kết nối mạng nội bộ `app-network`.

### Phase V2: Xây dựng Benchmark Harness & Dữ liệu Test Fixtures
- [ ] **Task V2.1:** Thiết lập bộ dữ liệu kiểm định `benchmark/datasets/` gồm 15 bộ ảnh mẫu đa dạng vóc dáng (Nam/Nữ, dáng đồng hồ cát, quả táo, quả lê, chữ nhật; người gầy, người đậm người) kèm số đo thước dây thực tế trong `ground_truth.json`.
- [ ] **Task V2.2:** Thu thập 25 ảnh kiểm thử các lỗi Quality Gate chuyên biệt (cắt chân, cắt đầu, rung mờ, thiếu sáng, sai tư thế).
- [ ] **Task V2.3:** Phát triển script tự động `benchmark/run_benchmark.py`:
  - Thực thi kiểm định song song, đo đạc độ trễ (Latency P50/P95).
  - Tính toán ma trận nhầm lẫn (Confusion Matrix), Precision, Recall, F1-Score cho Quality Gate.
  - Tính MAE, MAPE, $\sigma$ lặp lại và tỷ lệ Tolerance Pass Rate cho Measurement.
  - So sánh với `baseline_scores.json` (Ratchet Rule: tự động throw error nếu bất kỳ chỉ số nào bị suy giảm).

### Phase V3: Hoàn thiện Single-Pass Quality Gate Engine Tinh gọn
- [ ] **Task V3.1:** Cài đặt Singleton MediaPipe Pose Landmarker và Resolution Gate ($H \ge 800$, $W \ge 600$).
- [ ] **Task V3.2:** Triển khai Single-Pass Check: xác thực có người (Presence), ước lượng đỉnh đầu ($y_{\text{crown}}$) và ngón/gót chân bắt cắt mép ảnh.
- [ ] **Task V3.3:** Triển khai Occlusion Check (visibility mốc vai/hông/gối $< 0.60$) và Pose Orientation Check (lệch $Z$ vai).
- [ ] **Task V3.4:** Triển khai Fast ROI Blur (Laplacian variance) và Lighting (`gray_roi.mean()`) trong 1 module duy nhất `quality_gate.py`.
- [ ] **Task V3.5:** Chạy `python benchmark/run_benchmark.py --suite quality` và tinh chỉnh threshold đạt F1-Score $\ge 96\%$, Latency P95 $\le 35\text{ms}$.

### Phase V4: Hoàn thiện Hybrid 2-View Stereometry & Smart Fit Notes Engine (`hybrid_stereometry_2d`)
- [ ] **Task V4.1:** Xây dựng module tính toán hệ số quy đổi Pixel-to-Metric (P2M Scale) từ đỉnh đầu đến gót chân, đo tuyến tính Vai (bù delta 1.10), Dài tay (3 khớp) và Dài chân (Inseam).
- [ ] **Task V4.2:** Triển khai tính chu vi 3 vòng (Ngực, Eo, Hông) bằng công thức Ramanujan lập thể 2 góc chụp (Front bán trục $a$ + Side bán trục $b$), tích hợp tiền nghiệm Tuổi (Age Drift sau 25) và Cân nặng (BMI volume offset).
- [ ] **Task V4.3:** Triển khai cơ chế Fallback khi thiếu ảnh Side (suy luận chiều sâu $b$ từ tỷ lệ nhân trắc học giải phẫu).
- [ ] **Task V4.4:** Xây dựng bộ phân loại vóc dáng (Đồng hồ cát, Quả lê, Quả táo, Chữ nhật, Tam giác ngược) và sinh khuyến nghị may mặc thông minh (Smart Fit Notes) theo quy tắc rule-based.
- [ ] **Task V4.5:** Chạy `python benchmark/run_benchmark.py --suite measurement` và tinh chỉnh hệ số đạt MAE Vai $\le 1.5\text{cm}$, Eo $\le 2.0\text{cm}$, Ngực/Hông $\le 2.5\text{cm}$, Tolerance Pass Rate $\ge 90\%$.

### Phase V5: Tích hợp Hệ thống & Đóng gói Nghiệm thu
- [ ] **Task V5.1:** Cập nhật `backend/app/services/quality_check_service.py` và `backend/app/services/anthropometric_service.py` chuyển sang gọi HTTP Client (`httpx.AsyncClient`) sang `http://vision-service:8002`.
- [ ] **Task V5.2:** Xây dựng cơ chế Circuit Breaker / Fallback tự động: nếu `vision-service` bận, trả về mã lỗi rõ ràng hoặc fallback sang phương thức tính toán nhân trắc học cơ bản.
- [ ] **Task V5.3:** Xuất báo cáo tổng kết nghiệm thu `vision-service/benchmark/reports/FINAL_BENCHMARK_REPORT.md` chứng minh toàn bộ tiêu chuẩn chất lượng đã được đáp ứng.

---

## 6. Quy tắc Kiểm tra & Tiêu chuẩn Nghiệm thu (Verification & DoD)

1. **Kiểm tra cục bộ Microservice:**
   ```bash
   # Chạy test suite logic
   cd vision-service && pytest tests/ -v
   # Chạy toàn bộ benchmark định lượng
   python benchmark/run_benchmark.py --check-ratchet
   ```
2. **Kiểm tra Container & Endpoint:**
   ```bash
   docker compose up -d vision-service
   curl -s http://localhost:8002/docs | grep -q "AI Precision Fit Vision Service"
   ```
3. **Tiêu chuẩn vượt qua Checkpoint:**
   - 100% test cases trong `run_benchmark.py` vượt qua các ngưỡng KPI đã cam kết tại Mục 3.1.
   - Không xuất hiện bất kỳ lỗi linter hoặc type check nào.
   - Không làm chậm phản hồi E2E của người dùng trên Web Widget (tổng thời gian phân tích cả 2 ảnh $< 1.5\text{s}$).
