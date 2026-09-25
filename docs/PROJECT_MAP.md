# Project Map & Selective Context Index

> Áp dụng phương pháp **Context Engineering** để tối ưu hóa context cho agent, ngăn chặn hiện tượng "context flooding" (>5000 lines) và ảo giác (hallucination).

---

## 1. Domain Map & Key File Locations

```
ai-fitting/
├── docs/
│   ├── api/ai_precision_fit_api.yaml        # API Contract chuẩn (OpenAPI 3.0)
│   ├── plans/tech_stacks.md                 # Quyết định công nghệ & giới hạn phạm vi
│   ├── plans/vibe_coding_first_plan.md      # Chi tiết 4 Phases thực thi
│   ├── plans/tasks/todo.md                  # Checklist tiến độ nhiệm vụ (DoD)
│   └── PROJECT_MAP.md                       # Bản đồ context & gói context chọn lọc (file này)
├── frontend/
│   ├── app/
│   │   ├── globals.css                      # CSS variables & Tailwind directives
│   │   ├── layout.tsx                       # Root layout & font Be Vietnam Pro
│   │   └── page.tsx                         # Demo Catalog 50 sản phẩm + Trigger Widget
│   ├── components/
│   │   ├── ui/                              # Base primitives (Button, Badge, StepHeader, StepperInput, ...)
│   │   └── fitting/                         # 10 Screen components của Fitting Widget & WidgetContainer
│   ├── hooks/
│   │   ├── useProfiles.ts                   # Quản lý Multi-Profile (LocalStorage + sync)
│   │   └── useFittingFlow.ts                # State machine điều phối 10 bước fitting
│   ├── data/
│   │   └── mockFittingData.ts               # 50 Garments, Size Charts, Default Profiles
│   ├── services/
│   │   └── fitEngine.ts                     # Thuật toán so khớp số đo & tính fit score
│   ├── types/
│   │   └── fitting.ts                       # TypeScript schemas (1-1 với backend & OpenAPI)
│   └── public/products/                     # Static assets 50 sản phẩm (5 brands)
├── backend/
│   ├── app/
│   │   ├── api/v1/                          # Routers (/quality-check, /measure, /size-recommend, /tryon)
│   │   ├── models/fitting.py                # Pydantic v2 models (đồng bộ types/fitting.ts)
│   │   └── services/                        # Logic MediaPipe, Anthropometric, Size scoring
├── vto-service/                             # Microservice CatVTON (GPU isolated)
└── tmp/                                     # Mọi file tạm, script test, scratchpad (git-ignored)
```

---

## 2. Selective Context Packs (Dùng Khi Bắt Đầu Từng Task)

Thay vì nạp toàn bộ file kế hoạch 27KB, hãy nạp chính xác **Selective Context Pack** tương ứng với task cần làm:

### 📦 Context Pack: Phase 0 — Foundation & Data Layer

#### Task 0.1: Chuẩn hóa Type Contracts & Schemas
- **Mục tiêu:** Đồng bộ OpenAPI YAML, TypeScript FE, và Pydantic BE.
- **Files cần đọc & chỉnh sửa:**
  - `docs/api/ai_precision_fit_api.yaml` (Dòng 140-220: Garment & SizeChart schemas)
  - `frontend/types/fitting.ts`
  - `backend/app/models/fitting.py`
- **Ràng buộc:** Bổ sung `brand` ('coolmate' | 'canifa' | 'routine' | 'aristino' | 'an_phuoc'), mở rộng `category` ('jacket' | 'hoodie' | 'cardigan' | 'blazer' | 'coat' | 'trench_coat' | 'windbreaker' | 'vest').
- **Lệnh verify:** `cd frontend && npx tsc --noEmit`

#### Task 0.2: Tích hợp 50 Sản phẩm Mẫu & Mock Size Charts
- **Mục tiêu:** Seed 50 sản phẩm thực tế kèm size chart chuẩn cho 5 thương hiệu.
- **Files cần đọc & chỉnh sửa:**
  - `samples/assets/products/`
  - `frontend/public/products/`
  - `frontend/data/mockFittingData.ts`
- **Ràng buộc:** 5 brands x 10 sản phẩm = 50 items. Đầy đủ bảng số đo (XS đến XXL) cho từng sản phẩm.
- **Lệnh verify:** `ls frontend/public/products/*/*.webp | wc -l` (đạt 50)

#### Task 0.3: Multi-Profile Manager Hook (`useProfiles.ts`)
- **Mục tiêu:** Quản lý state profile không cần login (Zero-Auth), lưu trữ `localStorage`.
- **Files cần đọc & chỉnh sửa:**
  - `frontend/types/fitting.ts` (UserProfile)
  - `frontend/hooks/useProfiles.ts` [NEW]
  - `frontend/data/mockFittingData.ts` (DEFAULT_PROFILES: Trang & Minh)
- **Ràng buộc:** Hỗ trợ `addProfile`, `updateProfile`, `deleteProfile`, `setActiveProfile`, `activeProfile`.

---

### 📦 Context Pack: Phase 1 — Design Tokens & UI Primitives

- **Design Tokens (Figma Node 8:10):**
  - Primary Teal: `#0F766E` | Hover: `#115E59` | Light: `#CCFBF1` | Ring: `#14B8A6`
  - Canvas: `#0B0F19` | Surface: `#111827` | Card: `#1E293B` | Border: `#334155`
  - Text: `#F8FAFC` | Muted: `#94A3B8`
- **Files liên quan:**
  - `frontend/tailwind.config.js`
  - `frontend/app/globals.css`
  - `frontend/components/fitting/WidgetContainer.tsx` (Khung 390px x 844px)
  - `frontend/components/ui/` (`Button.tsx`, `Badge.tsx`, `StepHeader.tsx`, `SegmentedControl.tsx`, `StepperInput.tsx`, `ProfileSwitcher.tsx`)

---

### 📦 Context Pack: Phase 2 — Fitting Widget Journey (10 Screens)

- **State Machine:** `frontend/hooks/useFittingFlow.ts`
- **10 Screens:**
  1. `WelcomeScreen.tsx`
  2. `ProfileSetupScreen.tsx`
  3. `MethodSelectScreen.tsx`
  4. `UploadGuideScreen.tsx`
  5. `UploadVerifyScreen.tsx`
  6. `ManualInputScreen.tsx`
  7. `AnalyzingScreen.tsx`
  8. `RecommendationScreen.tsx` + `frontend/services/fitEngine.ts`
  9. `ProfileListScreen.tsx`
  10. `ProfileDetailScreen.tsx`
- **Try-On Modal:** `frontend/components/fitting/VTOPreviewModal.tsx`

---

## 3. Session Boundary & Context Budget Checklist

Trước khi kết thúc lượt trao đổi hoặc chuyển sang task mới:
1. **Kiểm tra file tạm:** Đảm bảo không có file script thừa ngoài `tmp/`.
2. **Cập nhật tiến độ:** Check tick `[x]` vào `docs/plans/tasks/todo.md`.
3. **Chạy Typecheck / Lint:** Đảm bảo code mới không làm gãy build.
4. **Ghi chú Handoff:** Nêu rõ file đã sửa, trạng thái hiện tại, và task tiếp theo trong checklist.
