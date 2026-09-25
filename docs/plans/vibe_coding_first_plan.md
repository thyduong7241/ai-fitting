# AI Precision Fit — Kế hoạch Triển khai Web App chi tiết cho Coding Agent (Agent-Ready Plan)

> **Tài liệu tham chiếu:**
> - Tech Stack: `docs/plans/tech_stacks.md`
> - API Contract: `docs/api/ai_precision_fit_api.yaml`
> - Figma Spec: [AI Precision Fit - Mobile Design System (Node 8:10 & 8:12)](https://www.figma.com/design/DOGArspqs5nAybRQh5k7OL/AI-Precision-Fit---Mobile-Design-System?node-id=8-10)
> - Quy ước dự án: `AGENTS.md` (Next.js 15, React 19, TypeScript strict mode, Tailwind CSS, Mobile-first, Supabase Self-hosted, Docker Compose)
> - Tài nguyên mẫu: `samples/assets/products/` & `samples/data/products.json` (50 sản phẩm thực tế: Zara, Uniqlo, H&M, Pull&Bear, Stradivarius)
> - Task Tracker Target: `docs/plans/tasks/todo.md`
> - **Kế hoạch Tích hợp Backend & AI Pipeline (Phát triển sau):** `docs/plans/DEFERRED_BACKEND_AND_AI_INTEGRATION.md`

---

## 1. Phân định Phạm vi Triển khai (Scope Boundaries)

Kế hoạch này được cấu trúc theo chiến lược **Frontend-First (Vibe Coding Mock Demo)** nhằm hoàn thiện 100% trải nghiệm người dùng trên Mobile Web Widget theo đúng thiết kế Figma trước khi kết nối trực tiếp vào server AI:

* **`[SHARED]`:** Hợp đồng dữ liệu chung giữa Frontend và Backend (TypeScript Interfaces & Pydantic Schemas đồng bộ 1-1 với OpenAPI spec).
* **`[FE]`:** Toàn bộ giao diện Next.js, Layout responsive, 10 màn hình của Fitting Widget, VTO Modal 8 trạng thái, State machine, và Bộ dữ liệu giả lập 50 sản phẩm thực tế.
* **`[BE]` (Deferred / Phát triển sau):** FastAPI Endpoints, Supabase PostgreSQL, MediaPipe Pose / Laplacian Blur, Anthropometric Measurement, CatVTON GPU Service được quy hoạch tập trung tại tài liệu: [docs/plans/DEFERRED_BACKEND_AND_AI_INTEGRATION.md](file:///home/nttduong1/projects/ai-fitting/docs/plans/DEFERRED_BACKEND_AND_AI_INTEGRATION.md).

```
                  ┌───────────────────────────────────────────────┐
                  │          DEMO SHOPPER (Single User)           │
                  │  (Lưu LocalStorage key ai_precision_fit_prof) │
                  └──────────────────────┬────────────────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
       ┌──────────────────────┐                     ┌──────────────────────┐
       │   Profile 1: "Trang" │                     │   Profile 2: "Minh"  │
       │   • Nữ, 162cm, 50kg  │                     │   • Nam, 175cm, 68kg │
       │   • Fit: Vừa vặn     │                     │   • Fit: Rộng rãi    │
       │   • Ảnh mẫu của Trang│                     │   • Ảnh mẫu của Minh │
       └───────────┬──────────┘                     └───────────┬──────────┘
                   │                                            │
        (Active: Đang chọn Trang)                    (Active: Đang chọn Minh)
                   │                                            │
         ┌─────────┴─────────┐                        ┌─────────┴─────────┐
         ▼                   ▼                        ▼                   ▼
    AI Fitting          Virtual Try-On           AI Fitting          Virtual Try-On
   (Gợi ý Size S/M     (Mặc thử CatVTON         (Gợi ý Size L/XL     (Mặc thử CatVTON
    cho dáng Trang)     với ảnh Trang)           cho dáng Minh)       với ảnh Minh)
```

---

## 2. Danh mục Dữ liệu Mẫu (50 Sản Phẩm Thực Tế)

Dữ liệu sản phẩm trích xuất đầy đủ từ thư mục `samples/assets/products/` và `samples/data/products.json`, gồm 5 thương hiệu hàng đầu:

| Thương hiệu | Số lượng | Danh mục chính | Link thư mục ảnh |
|---|---|---|---|
| **Zara** | 10 | Biker jacket da, Trench coat măng tô, Blazer may đo, Áo gió | `frontend/public/products/zara/` |
| **Uniqlo** | 10 | Ultra Light Down, Fluffy Fleece lông cừu, Parka Blocktech, Stretch Denim | `frontend/public/products/uniqlo/` |
| **H&M** | 10 | Áo khoác dạ pha len, Áo phao cổ đứng, Varsity bóng chày, Biker da lửng | `frontend/public/products/hm/` |
| **Pull&Bear** | 10 | Denim trucker vintage, Corduroy sherpa, Bomber MA-1, Phao gile | `frontend/public/products/pullandbear/` |
| **Stradivarius** | 10 | Aviator jacket lót lông, Crop trench coat, Houndstooth blazer | `frontend/public/products/stradivarius/` |

---

## 3. Cấu trúc Thư mục Mục tiêu (Frontend Target Directory)

```
frontend/
├── app/
│   ├── layout.tsx                   # Root layout (Be Vietnam Pro font, viewport meta, body)
│   ├── page.tsx                     # Product Catalog Demo (50 sản phẩm, brand filter, PDP widget trigger)
│   └── globals.css                  # Design tokens, custom scrollbar, animations
├── public/
│   └── products/                    # 50 ảnh sản phẩm (zara, uniqlo, hm, pullandbear, stradivarius)
├── types/
│   └── fitting.ts                   # TypeScript schemas khớp OpenAPI spec
├── data/
│   └── mockFittingData.ts           # 50 Garments, Size Charts, Default Profiles
├── hooks/
│   ├── useFittingFlow.ts            # State machine điều hướng 10 màn hình
│   └── useProfiles.ts               # Quản lý đa profile, active profile, LocalStorage sync
└── components/
    ├── ui/                          # Atomic Primitives
    │   ├── Button.tsx               # Primary, Secondary, Ghost, Icon buttons
    │   ├── Badge.tsx                # Status badge (Perfect fit, Tight, Loose, Tag)
    │   ├── StepHeader.tsx           # Header thanh tiến trình (Back button, Title, Close)
    │   ├── StepperInput.tsx         # Input tăng giảm số đo (+ / -)
    │   ├── SegmentedControl.tsx     # Bộ chọn Tab (Nữ / Nam, cm / inch, Gu mặc)
    │   └── ProfileSwitcher.tsx      # Dropdown chuyển nhanh hồ sơ người dùng
    └── fitting/                     # Feature Screens & Containers
        ├── WidgetContainer.tsx      # Khung mobile 390px x 844px căn giữa responsive
        ├── WelcomeScreen.tsx        # Screen 1: Giới thiệu tính năng AI Precision Fit
        ├── ProfileSetupScreen.tsx   # Screen 2: Tạo nhanh hồ sơ (Tên, Giới tính, Gu mặc)
        ├── MethodSelectScreen.tsx   # Screen 3: Chọn phương thức (AI Chụp ảnh vs Nhập tay)
        ├── UploadGuideScreen.tsx    # Screen 4: Hướng dẫn tư thế đứng chụp toàn thân
        ├── UploadVerifyScreen.tsx   # Screen 5: Kiểm định ảnh (Báo lỗi cắt chân / Đạt chuẩn)
        ├── ManualInputScreen.tsx    # Screen 6: Form nhập số đo 3 vòng kèm toggle cm/inch
        ├── AnalyzingScreen.tsx      # Screen 7: Radar scan animation giả lập AI tính toán
        ├── RecommendationScreen.tsx # Screen 8: Kết quả gợi ý size, breakdown 5 vùng cơ thể
        ├── ProfileListScreen.tsx    # Screen 9: Quản lý danh sách hồ sơ (chuyển / xóa / thêm)
        ├── ProfileDetailScreen.tsx  # Screen 10: Xem chi tiết và chỉnh sửa số đo hồ sơ
        └── VTOPreviewModal.tsx      # Modal xem kết quả mặc thử Virtual Try-On (8 trạng thái)
```

---

## 4. Kế hoạch Chi tiết từng Task theo Chuẩn Agent-Ready

### PHASE 0: Foundation & Multi-Profile Data Layer

#### [TASK-0.1][SHARED] Chuẩn hóa Type Contracts & Schema
- **Description:** Cập nhật `frontend/types/fitting.ts` và `backend/app/models/fitting.py` để bổ sung trường `brand`, mở rộng enum `category` (`jacket`, `coat`, `blazer`, `puffer`, `dress`, `shirt`, `pants`), đồng bộ 100% với file OpenAPI spec `docs/api/ai_precision_fit_api.yaml`.
- **Acceptance criteria:**
  - [ ] `Garment` interface có trường `brand: 'zara' | 'uniqlo' | 'hm' | 'pullandbear' | 'stradivarius'` và danh mục đầy đủ.
  - [ ] Thêm các kiểu dữ liệu cho `FlowStep`, `UserProfile`, `PartFitEvaluation`, `SizeRecommendResponse`.
  - [ ] Không có type error khi import vào toàn bộ frontend và backend.
- **Verification:**
  - [ ] Build: `cd frontend && npx tsc --noEmit` thoát mã 0.
  - [ ] Python syntax: `python3 -m py_compile backend/app/models/fitting.py` thoát mã 0.
- **Dependencies:** None
- **Files likely touched:**
  - `frontend/types/fitting.ts`
  - `backend/app/models/fitting.py`
- **Estimated scope:** Small (2 files)

#### [TASK-0.2][FE] Tích hợp 50 Sản phẩm Mẫu & Mock Size Charts
- **Description:** Sao chép 50 ảnh sản phẩm từ `samples/assets/products/` vào `frontend/public/products/` theo từng thương hiệu, đồng thời khởi tạo dữ liệu danh mục 50 sản phẩm kèm bảng size charts outerwear chi tiết trong `frontend/data/mockFittingData.ts`.
- **Acceptance criteria:**
  - [ ] Toàn bộ 50 file ảnh nằm đúng tại `frontend/public/products/{zara,uniqlo,hm,pullandbear,stradivarius}/`.
  - [ ] `mockFittingData.ts` export danh sách 50 `mockGarments` kèm size chart chuẩn cho từng size (S, M, L, XL).
  - [ ] Khởi tạo sẵn 2 profile mẫu (`Trang` - Nữ và `Minh` - Nam) kèm ảnh và số đo tiêu chuẩn.
- **Verification:**
  - [ ] Kiểm tra tồn tại ảnh: `ls frontend/public/products/*/*.webp | wc -l` trả về 50.
  - [ ] Build: `cd frontend && npx tsc --noEmit` thành công.
- **Dependencies:** Task 0.1
- **Files likely touched:**
  - `frontend/data/mockFittingData.ts`
  - `frontend/public/products/`
- **Estimated scope:** Medium (1 data file + assets)

#### [TASK-0.3][FE] Multi-Profile Manager State Hook
- **Description:** Xây dựng hook `frontend/hooks/useProfiles.ts` quản lý state danh sách `profiles`, `activeProfile`, lưu trữ bền vững qua `localStorage` (key: `ai_precision_fit_profiles`), hỗ trợ chuyển đổi profile, thêm, sửa, xóa profile.
- **Acceptance criteria:**
  - [ ] Tự động seed 2 profiles mẫu (`Trang`, `Minh`) nếu `localStorage` trống.
  - [ ] Cung cấp các hàm: `setActiveProfile(id)`, `addProfile(profile)`, `updateProfile(id, data)`, `deleteProfile(id)`.
  - [ ] Đồng bộ tức thì mọi thao tác vào `localStorage`.
- **Verification:**
  - [ ] Unit check: Kiểm tra typecheck `npx tsc --noEmit` không báo lỗi.
- **Dependencies:** Task 0.1, Task 0.2
- **Files likely touched:**
  - `frontend/hooks/useProfiles.ts`
- **Estimated scope:** Small (1 file)

#### Checkpoint 0: Foundation & Data Layer
- [ ] TypeScript check qua 100% không cảnh báo lỗi (`npx tsc --noEmit`).
- [ ] 50 ảnh sản phẩm có thể truy cập được từ server.
- [ ] Hook `useProfiles` sẵn sàng cho việc kết nối vào UI.

---

### PHASE 1: Design Tokens & Base UI Primitives

#### [TASK-1.1][FE] Cấu hình Tailwind Theme & Design Tokens
- **Description:** Cập nhật `frontend/tailwind.config.js` và `frontend/app/globals.css` với bảng màu và typography chuẩn Figma (Node `8:10` & `8:12`): Font chính `Be Vietnam Pro` (fallback `Inter`), Primary Teal `#16ABAD` / `#1AB8B8`, Dark Navy `#183247`, Deep Surface `#0E1F2E`, Muted Slate `#5C738C`, Secondary `#425C75`, Light Teal `#DBF7F5`, Match Green `#1F9C7A`, Border `#DFEBEF` / `#DBE5ED`, Canvas Tint `#F6FBFA`.
- **Acceptance criteria:**
  - [ ] Khai báo đầy đủ palette màu `brand` và status colors trong `tailwind.config.js`.
  - [ ] Cấu hình font `Be Vietnam Pro` từ `next/font/google` trong `layout.tsx`.
  - [ ] Thiết lập các lớp bo tròn chuẩn Figma (`rounded-[14px]`, `rounded-[16px]`, `rounded-[28px]`, `rounded-full`).
- **Verification:**
  - [ ] Build: `cd frontend && npm run build` thành công không cảnh báo.
- **Dependencies:** None
- **Files likely touched:**
  - `frontend/tailwind.config.js`
  - `frontend/app/globals.css`
  - `frontend/app/layout.tsx`
- **Estimated scope:** Small (3 files)

#### [TASK-1.2][FE] Mobile Layout Shell (`WidgetContainer.tsx`)
- **Description:** Xây dựng khung hiển thị `frontend/components/fitting/WidgetContainer.tsx` mô phỏng màn hình điện thoại kích thước `390px x 844px` căn giữa màn hình trên Desktop và mở rộng full màn hình trên thiết bị di động.
- **Acceptance criteria:**
  - [ ] Hiển thị thanh status bar giả lập tinh tế (giờ, sóng, pin).
  - [ ] Tích hợp khu vực header linh hoạt hỗ trợ nút đóng, nút quay lại, và khu vực nội dung cuộn mượt không lộ thanh scrollbar ngang.
- **Verification:**
  - [ ] Component render sạch, không vỡ layout khi co kéo màn hình từ 360px đến 1920px.
- **Dependencies:** Task 1.1
- **Files likely touched:**
  - `frontend/components/fitting/WidgetContainer.tsx`
- **Estimated scope:** Small (1 file)

#### [TASK-1.3][FE] Bộ Atomic UI Primitives (Button, Badge, StepHeader)
- **Description:** Tạo các component giao diện cơ bản tái sử dụng trong `frontend/components/ui/`: `Button.tsx` (primary, secondary, ghost, icon), `Badge.tsx` (fit status, size tag), `StepHeader.tsx` (tiêu đề bước, nút back).
- **Acceptance criteria:**
  - [ ] `Button`: Hỗ trợ prop `variant`, `size`, `isLoading`, `icon`, hiệu ứng bấm active mượt mà.
  - [ ] `Badge`: Hiển thị chuẩn màu theo trạng thái (`perfect` xanh teal, `tight` cam, `loose` xanh dương nhạt).
  - [ ] `StepHeader`: Nhận `title`, `subtitle`, callback `onBack`, `onClose`.
- **Verification:**
  - [ ] Typecheck `npx tsc --noEmit` pass 100%.
- **Dependencies:** Task 1.1
- **Files likely touched:**
  - `frontend/components/ui/Button.tsx`
  - `frontend/components/ui/Badge.tsx`
  - `frontend/components/ui/StepHeader.tsx`
- **Estimated scope:** Medium (3 files)

#### [TASK-1.4][FE] Bộ Form & Selection Controls (SegmentedControl, StepperInput, ProfileSwitcher)
- **Description:** Xây dựng các component nhập liệu và điều khiển lựa chọn trong `frontend/components/ui/`: `SegmentedControl.tsx` (chuyển đổi Nữ/Nam, cm/inch), `StepperInput.tsx` (tăng giảm số đo +/-), và `ProfileSwitcher.tsx` (pill chuyển đổi nhanh profile trên header).
- **Acceptance criteria:**
  - [ ] `SegmentedControl`: Chuyển tab mượt với animation nền trượt nhẹ.
  - [ ] `StepperInput`: Hỗ trợ bấm giữ để tăng nhanh, có hiển thị đơn vị đo kèm theo.
  - [ ] `ProfileSwitcher`: Hiển thị tên và giới tính profile đang chọn; bấm vào mở dropdown chọn đổi profile hoặc nút thêm profile mới.
- **Verification:**
  - [ ] Thao tác chuyển đổi kích hoạt đúng event handler onChange.
- **Dependencies:** Task 1.1, Task 0.3
- **Files likely touched:**
  - `frontend/components/ui/SegmentedControl.tsx`
  - `frontend/components/ui/StepperInput.tsx`
  - `frontend/components/ui/ProfileSwitcher.tsx`
- **Estimated scope:** Medium (3 files)

#### Checkpoint 1: Base Primitives & Container Ready
- [ ] Tất cả atomic components có type definition chặt chẽ.
- [ ] Layout shell và các form control render chuẩn xác với design system.

---

### PHASE 2: Core User Journey Screens (Fitting Widget Flow)

#### [TASK-2.1][FE] Fitting Flow State Machine Hook
- **Description:** Xây dựng `frontend/hooks/useFittingFlow.ts` điều phối lịch sử chuyển đổi giữa 10 màn hình của Fitting Widget (`welcome` -> `profile_setup` -> `method_select` -> `upload_guide` / `manual_input` -> `upload_verify` -> `analyzing` -> `recommendation` -> `profile_list` -> `profile_detail`).
- **Acceptance criteria:**
  - [ ] Quản lý state `currentStep`, `historyStack`, hàm `goToStep(step)`, `goBack()`, `resetFlow()`.
  - [ ] Lưu giữ dữ liệu tạm thời trong phiên đo (ảnh đã upload, số đo vừa nhập, garment đang xét).
- **Verification:**
  - [ ] Thử gọi chuỗi chuyển bước và `goBack()` quay lại chính xác bước trước đó.
- **Dependencies:** Task 0.1
- **Files likely touched:**
  - `frontend/hooks/useFittingFlow.ts`
- **Estimated scope:** Small (1 file)

#### [TASK-2.2][FE] Screen 1 & 2 — WelcomeScreen & ProfileSetupScreen
- **Description:** Xây dựng màn hình giới thiệu tính năng AI Precision Fit (`WelcomeScreen.tsx`) và màn hình tạo nhanh hồ sơ cho người mới (`ProfileSetupScreen.tsx`) gồm chọn Giới tính, nhập Tên và chọn Gu ăn mặc (Ôm / Vừa / Rộng).
- **Acceptance criteria:**
  - [ ] `WelcomeScreen`: Hiển thị visual thương hiệu, nút CTA `Bắt đầu trải nghiệm`. Nếu đã có profile sẵn, hiển thị nút `Tiếp tục với [Tên Profile]`.
  - [ ] `ProfileSetupScreen`: Form nhập liệu trực quan, bấm `Tiếp tục` sẽ lưu profile vào `useProfiles` và chuyển sang bước chọn phương thức đo.
- **Verification:**
  - [ ] Bấm tạo profile mới lưu thành công vào LocalStorage và cập nhật `activeProfile`.
- **Dependencies:** Task 1.2, Task 1.3, Task 1.4, Task 2.1
- **Files likely touched:**
  - `frontend/components/fitting/WelcomeScreen.tsx`
  - `frontend/components/fitting/ProfileSetupScreen.tsx`
- **Estimated scope:** Small (2 files)

#### [TASK-2.3][FE] Screen 3 — MethodSelectScreen (Chọn Phương Thức Đo)
- **Description:** Xây dựng `frontend/components/fitting/MethodSelectScreen.tsx` cho phép người dùng lựa chọn giữa 2 phương thức: "AI Chụp ảnh quét toàn thân" (Khuyên dùng) hoặc "Nhập thủ công số đo 3 vòng".
- **Acceptance criteria:**
  - [ ] Thẻ lựa chọn có badge `Khuyên dùng · Nhanh 30s` cho phương thức AI.
  - [ ] Chọn AI chuyển sang `upload_guide`; chọn nhập tay chuyển sang `manual_input`.
- **Verification:**
  - [ ] Click vào mỗi lựa chọn điều hướng chính xác đến màn hình tương ứng.
- **Dependencies:** Task 2.1
- **Files likely touched:**
  - `frontend/components/fitting/MethodSelectScreen.tsx`
- **Estimated scope:** Small (1 file)

#### Checkpoint 2: Onboarding & Profile Setup Flow Verified
- [ ] Người dùng có thể đi từ Welcome -> Setup Profile -> Chọn phương thức đo liền mạch.

#### [TASK-2.4][FE] Screen 4 & 5 — UploadGuideScreen & UploadVerifyScreen (AI Photo Path)
- **Description:** Xây dựng màn hình hướng dẫn chụp toàn thân (`UploadGuideScreen.tsx`) và màn hình kiểm định ảnh (`UploadVerifyScreen.tsx`) tích hợp toggle mô phỏng cả 2 trạng thái: Ảnh lỗi (`! Cụt bàn chân`) và Ảnh đạt chuẩn (`✓ Đã xác minh`).
- **Acceptance criteria:**
  - [ ] `UploadGuideScreen`: Minh họa 3 quy tắc chụp (đứng thẳng, đủ sáng, lùi xa thấy hết người) kèm input upload ảnh.
  - [ ] `UploadVerifyScreen`: Hiển thị bounding box đỏ cảnh báo khi ảnh lỗi và nút chụp lại; hiển thị tick xanh và nút `Bắt đầu quét vóc dáng` khi ảnh hợp lệ.
- **Verification:**
  - [ ] Người dùng có thể chuyển đổi qua lại giữa ảnh đạt chuẩn và ảnh lỗi để kiểm tra UX.
- **Dependencies:** Task 2.1, Task 1.3
- **Files likely touched:**
  - `frontend/components/fitting/UploadGuideScreen.tsx`
  - `frontend/components/fitting/UploadVerifyScreen.tsx`
- **Estimated scope:** Small (2 files)

#### [TASK-2.5][FE] Screen 6 — ManualInputScreen (Nhập Số Đo Thủ Công)
- **Description:** Xây dựng `frontend/components/fitting/ManualInputScreen.tsx` gồm các trường nhập Chiều cao, Cân nặng, Vòng ngực, Vòng eo, Vòng hông, Rộng vai bằng StepperInput kèm bộ toggle đổi đơn vị `cm / inch`.
- **Acceptance criteria:**
  - [ ] Tự động chuyển đổi hiển thị giữa hệ mét (cm, kg) và hệ inch/lbs khi toggle.
  - [ ] Validate giới hạn hợp lý theo Pydantic schema (Chiều cao 100-250cm, Cân nặng 30-200kg).
  - [ ] Bấm `Hoàn tất & Tính toán` chuyển tiếp sang màn hình `analyzing`.
- **Verification:**
  - [ ] Điền số đo và kiểm tra dữ liệu lưu vào profile chuẩn xác.
- **Dependencies:** Task 1.4, Task 2.1
- **Files likely touched:**
  - `frontend/components/fitting/ManualInputScreen.tsx`
- **Estimated scope:** Small (1 file)

#### [TASK-2.6][FE] Screen 7 — AnalyzingScreen (Scanning Radar Animation)
- **Description:** Xây dựng màn hình quét cơ thể `frontend/components/fitting/AnalyzingScreen.tsx` với hiệu ứng vòng tròn quét radar màu Teal, hiển thị 3 bước phân tích tuần tự (Xác định khung xương -> Đo nhân trắc học -> So khớp bảng size) và tự động chuyển sang `recommendation` sau 2.5s.
- **Acceptance criteria:**
  - [ ] Hiệu ứng radar mượt mà bằng CSS keyframes.
  - [ ] Dòng trạng thái cập nhật từng bước với icon tick xanh.
  - [ ] Tự động cleanup timer khi component unmount tránh memory leak.
- **Verification:**
  - [ ] Màn hình chạy tự động và chuyển sang kết quả gợi ý đúng thời gian.
- **Dependencies:** Task 2.1
- **Files likely touched:**
  - `frontend/components/fitting/AnalyzingScreen.tsx`
- **Estimated scope:** Small (1 file)

#### Checkpoint 3: Photo & Manual Measurement Paths Verified
- [ ] Cả 2 luồng (chụp ảnh và nhập tay) đều dẫn đến màn hình quét và sẵn sàng nhận kết quả.

#### [TASK-2.7][FE] Fit Engine Service & RecommendationScreen
- **Description:** Xây dựng thuật toán tính toán độ vừa vặn rule-based tại `frontend/services/fitEngine.ts` và giao diện kết quả `frontend/components/fitting/RecommendationScreen.tsx` hiển thị size đề xuất tối ưu (XS/S/M/L/XL), phân tích 5 vùng cơ thể (Vai, Ngực, Eo, Hông, Dài áo) và dải hotspot so sánh độ chật/rộng giữa các size.
- **Acceptance criteria:**
  - [ ] Thuật toán tính độ chênh lệch giữa số đo active profile và size chart của garment, xét kèm độ co giãn vải và fit preference.
  - [ ] RecommendationScreen hiển thị badge kích thước khuyên dùng (ví dụ: `Size M - 95% Phù hợp`).
  - [ ] Có nút `Xem mặc thử (Virtual Try-On)` mở modal mặc thử.
  - [ ] Khi đổi active profile qua ProfileSwitcher, màn hình lập tức tính toán lại kết quả cho người mới.
- **Verification:**
  - [ ] Profile Trang (Nữ 162cm) gợi ý Size S/M; đổi sang profile Minh (Nam 175cm) gợi ý Size L/XL cho cùng 1 sản phẩm.
- **Dependencies:** Task 0.2, Task 0.3, Task 2.1
- **Files likely touched:**
  - `frontend/services/fitEngine.ts`
  - `frontend/components/fitting/RecommendationScreen.tsx`
- **Estimated scope:** Medium (2 files)

#### [TASK-2.8][FE] Screen 9 & 10 — Profile Management (List & Detail)
- **Description:** Xây dựng màn hình danh sách hồ sơ `frontend/components/fitting/ProfileListScreen.tsx` và màn hình chi tiết/chỉnh sửa số đo `frontend/components/fitting/ProfileDetailScreen.tsx`.
- **Acceptance criteria:**
  - [ ] `ProfileListScreen`: Xem danh sách profiles, chọn profile active chỉ với 1 click, nút thêm mới hồ sơ người thân, nút xóa profile.
  - [ ] `ProfileDetailScreen`: Xem và cập nhật số đo từng vòng, cập nhật gu mặc hoặc ảnh đại diện.
- **Verification:**
  - [ ] Chỉnh sửa số đo trong màn hình detail phản ánh ngay vào kết quả khuyến nghị size.
- **Dependencies:** Task 0.3, Task 2.1
- **Files likely touched:**
  - `frontend/components/fitting/ProfileListScreen.tsx`
  - `frontend/components/fitting/ProfileDetailScreen.tsx`
- **Estimated scope:** Small (2 files)

#### [TASK-2.9][FE] Virtual Try-On Preview Modal (`VTOPreviewModal.tsx`)
- **Description:** Xây dựng modal trải nghiệm thử đồ ảo `frontend/components/fitting/VTOPreviewModal.tsx` theo đặc tả chi tiết `docs/specs/SPEC-vto-modal.md` (trích xuất từ Figma Node `8:12`). Quản lý chuỗi 8 trạng thái: Xác nhận ảnh đã lưu (1/3), Hướng dẫn khi chưa có ảnh (1/3), Tải ảnh lên (2/3), Kiểm định ảnh thành công (2/3), Radar xử lý AI (3/3), Màn hình kết quả thử đồ kèm đổi size/màu và đánh giá độ ôm, Màn hình sự cố (Failure/Retry), và Hộp thoại xác nhận hủy (CancelConfirm).
- **Acceptance criteria:**
  - [ ] Hỗ trợ profile đã có ảnh (như Trang) đi thẳng tới bước xác nhận tạo preview hoặc chọn size.
  - [ ] Hỗ trợ profile chưa có ảnh hiển thị checklist chụp chuẩn và cho phép tải ảnh lên.
  - [ ] Animation xử lý % và thông báo "Đang khớp trang phục · màu [Màu] · Size [Size]".
  - [ ] Màn hình kết quả hiển thị ảnh CatVTON với badge `AI PREVIEW`, selector màu sắc/kích thước, dòng tư vấn độ ôm từng vùng cơ thể (Vai/Ngực/Eo) và nút "Thêm vào giỏ" / "Mua ngay".
  - [ ] Nút Back và nút Cancel kích hoạt hộp thoại `CancelConfirm` ("Dừng tạo preview?").
- **Verification:**
  - [ ] Mở modal từ màn hình Recommendation chuyển đổi mượt mà qua các bước theo đúng Figma Node `8:12`.
- **Dependencies:** Task 1.3, Task 2.7, `docs/specs/SPEC-vto-modal.md`
- **Files likely touched:**
  - `frontend/components/fitting/VTOPreviewModal.tsx`
  - `frontend/components/fitting/VTOProcessingState.tsx`
  - `frontend/components/fitting/VTOResultView.tsx`
- **Estimated scope:** Medium (3 files)

#### Checkpoint 4: Complete Fitting & Try-On Journey Verified
- [ ] 10 màn hình hoạt động trơn tru theo state machine.
- [ ] Kết quả fitting và try-on cập nhật tương ứng theo từng profile được chọn.

---

### PHASE 3: Product Catalog Demo Integration

#### [TASK-3.1][FE] Xây dựng Catalog Demo Page (`frontend/app/page.tsx`)
- **Description:** Refactor trang chủ `frontend/app/page.tsx` thành sàn thương mại điện tử demo tích hợp 50 sản phẩm thực tế, có bộ lọc theo 5 thương hiệu (Zara, Uniqlo, H&M, Pull&Bear, Stradivarius) và danh mục (Jacket, Coat, Blazer, Puffer), trên header hiển thị Profile Switcher và mỗi sản phẩm có nút kích hoạt Fitting Widget.
- **Acceptance criteria:**
  - [ ] Lưới sản phẩm hiển thị ảnh rõ nét (50 items), tên tiếng Việt, giá tiền VND và huy hiệu thương hiệu.
  - [ ] Header trang chủ có chỉ báo: `Đang chọn size cho: [ 👤 Trang ▼ ]`.
  - [ ] Bấm nút `✦ AI Chọn Size & Mặc Thử` trên sản phẩm bất kỳ sẽ mở Fitting Widget với đúng context của sản phẩm đó.
- **Verification:**
  - [ ] Mở trình duyệt tại `http://localhost:3000`, lọc thử các brand và click mở widget hoạt động chuẩn xác.
- **Dependencies:** Task 0.2, Task 0.3, Task 1.2, Task 2.7
- **Files likely touched:**
  - `frontend/app/page.tsx`
- **Estimated scope:** Medium (1-2 files)

#### [TASK-3.2][FE] E2E Smoke Test & Linter Verification
- **Description:** Kiểm thử toàn bộ hành trình đa profile trên trình duyệt, chạy build production và kiểm tra linter không còn bất kỳ lỗi nào.
- **Acceptance criteria:**
  - [ ] Lệnh `npm run build` thành công 100% không cảnh báo lỗi.
  - [ ] Kịch bản test: Người dùng chọn Trang -> thử áo Zara -> gợi ý Size S -> đổi sang Minh -> tự động cập nhật gợi ý Size L -> refresh trang dữ liệu vẫn bảo toàn.
- **Verification:**
  - [ ] `cd frontend && npm run build` -> Exit code 0.
- **Dependencies:** Task 3.1
- **Files likely touched:**
  - Toàn bộ codebase frontend nếu có lỗi syntax/type.
- **Estimated scope:** Small (Testing & Fixes)

#### Checkpoint 5: Web App Ready for Presentation
- [ ] 50 sản phẩm mẫu duyệt qua mượt mà.
- [ ] Cơ chế Multi-Profile không cần auth hoạt động ổn định trên cả desktop và điện thoại di động qua mạng LAN.
