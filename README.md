# AI Precision Fit 👗📏

> **Virtual Fitting Room & AI Precision Size Recommendation Widget for Fashion E-Commerce**  
> Giải pháp phòng thử đồ ảo và gợi ý size thông minh, tích hợp liền mạch vào các sàn thương mại điện tử thời trang. Tự động đề xuất kích cỡ tối ưu, phân tích độ vừa vặn đa vùng cơ thể và mô phỏng mặc thử trang phục thực tế (Virtual Try-On).

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20Self--Hosted-3ECF8E?logo=supabase)](https://supabase.com/)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript%20Strict-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🌟 Điểm Nổi Bật (Key Features)

- 📱 **Mobile-First Fitting Widget:** Thiết kế chuẩn viewport di động (390px x 844px) căn giữa trên desktop, tối ưu hóa trải nghiệm vuốt chạm, tuân thủ chặt chẽ Figma Design System (Node 8:10 & 8:12).
- 👥 **Zero-Auth Multi-Profile:** Lưu trữ và quản lý đa hồ sơ vóc dáng (người dùng, người thân, bạn bè) trực tiếp trên Client (`localStorage` + Supabase sync) mà không bắt buộc tạo tài khoản rườm rà.
- 🛍️ **50 Sản Phẩm Thực Tế & Size Charts:** Sàn diễn thời trang tích hợp sẵn 50 sản phẩm outerwear thực tế kèm size chart chi tiết từ 5 thương hiệu hàng đầu: **Zara, Uniqlo, H&M, Pull&Bear, Stradivarius**.
- 📐 **Dual Measurement Inputs:**
  - **AI Chụp ảnh:** Hướng dẫn tạo dáng đứng chuẩn, kiểm định chất lượng ảnh (Quality Gate kiểm tra cắt chân, độ mờ) và trích xuất số đo nhân trắc học 33 landmarks.
  - **Nhập tay thủ công:** Form nhập linh hoạt 6 số đo (Chiều cao, Cân nặng, Vòng 1, Vòng 2, Vòng 3, Rộng vai) hỗ trợ chuyển đổi cm / inch.
- 🎯 **Multi-Zone Fit Engine:** Thuật toán tính điểm vừa vặn đa chiều (ngực, eo, hông, vai, dài áo) so với bảng size thực tế của từng sản phẩm; tự động điều chỉnh theo gu mặc (Ôm sát / Vừa vặn / Rộng rãi).
- 🪞 **CatVTON Virtual Try-On:** Mô phỏng mặc thử đồ ảo với 8 trạng thái tương tác trực quan, cho phép nhấn giữ để so sánh ảnh gốc và ảnh mặc thử.
- 🛡️ **100% Self-Hosted & Bảo mật:** Triển khai On-Premise, toàn bộ mô hình AI (MediaPipe, CatVTON) tự chạy nội bộ, cam kết bảo mật quyền riêng tư ảnh vóc dáng của khách hàng.

---

## 🏗️ Kiến Trúc Hệ Thống (Tech Stack & Architecture)

```
[ Khách hàng / Shopper ]
          │
          ▼
┌────────────────────────────────────────────────────────┐
│  Next.js 14 Frontend (Mobile-First Widget)             │
│  - React, Tailwind CSS, TypeScript (Strict)           │
│  - State Machine 10 Màn hình (useFittingFlow)         │
│  - Multi-Profile Management (useProfiles)              │
│  - Realtime Fit Engine Client-Side Calculation        │
└──────────────────────────┬─────────────────────────────┘
                           │ (HTTP REST API / JSON)
                           ▼
┌────────────────────────────────────────────────────────┐
│  Python FastAPI Backend (/api/v1)                      │
│  - MediaPipe Pose 33-Landmarks + OpenCV Blur Check    │
│  - Anthropometric Measurement Extraction               │
│  - Rule-Based Size Recommendation & Explanation       │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────────┐ ┌──────────────────────┐
│  CatVTON Microservice        │ │  Supabase On-Prem    │
│  (Isolated GPU Inference)    │ │  (PostgreSQL + S3)   │
└──────────────────────────────┘ └──────────────────────┘
```

| Tầng | Công nghệ sử dụng | Vai trò |
|---|---|---|
| **Frontend** | Next.js 14 (App Router), React, Tailwind CSS, TypeScript | Giao diện Catalog & Widget thử đồ 10 bước |
| **Backend API** | Python 3.10+, FastAPI, Pydantic v2 | Xử lý nghiệp vụ, API định dạng OpenAPI 3.1 |
| **Quality Gate & Pose** | MediaPipe Pose Landmarker, OpenCV (Laplacian) | Kiểm tra độ nét, toàn thân và trích xuất landmarks |
| **Fit Engine** | Rule-Based Scoring Service (Client & Backend sync) | Đánh giá độ vừa vặn từng vùng cơ thể theo size chart |
| **Virtual Try-On** | CatVTON (GPU Microservice riêng biệt) | Ghép đồ ảo lên ảnh người dùng |
| **Database & Storage** | Supabase Self-Hosted (Docker Compose) | Lưu trữ profiles, garments, size charts và ảnh |

---

## 📁 Cấu Trúc Thư Mục (Repository Structure)

```
ai-fitting/
├── frontend/                     # Ứng dụng Next.js (Widget & Catalog Demo)
│   ├── app/                      # App router: page.tsx (Catalog 50 sản phẩm), layout.tsx
│   ├── components/
│   │   ├── ui/                   # Atomic primitives: Button, Badge, StepHeader, StepperInput...
│   │   └── fitting/              # 10 Screen components của luồng Fitting & WidgetContainer
│   ├── data/                     # mockFittingData.ts (50 Garments, Size Charts, Default Profiles)
│   ├── hooks/                    # useProfiles.ts (Multi-profile), useFittingFlow.ts (State machine)
│   ├── services/                 # fitEngine.ts (Tính fit score), apiClient.ts (HTTP client)
│   ├── types/                    # fitting.ts (Type definitions khớp OpenAPI spec)
│   └── public/products/          # 50 ảnh sản phẩm thực tế theo 5 thương hiệu
├── backend/                      # Python FastAPI Backend
│   ├── app/
│   │   ├── api/v1/               # Routers: /quality-check, /measure, /size-recommend, /tryon
│   │   ├── models/               # fitting.py (Pydantic models đồng bộ với frontend)
│   │   └── services/             # MediaPipe, Anthropometric, Size scoring services
├── vto-service/                  # Microservice suy luận CatVTON tách biệt (hỗ trợ GPU)
├── supabase/                     # Config Supabase On-Premise, migrations SQL và seed data
├── docs/                         # Tài liệu kỹ thuật, API specs, bản đồ dự án
│   ├── api/ai_precision_fit_api.yaml  # OpenAPI 3.1 Specification
│   ├── plans/                    # Kế hoạch phát triển chi tiết từng giai đoạn
│   └── PROJECT_MAP.md            # Bản đồ context & module
├── CONSTRAINTS.md                # Bản cam kết chất lượng kỹ thuật bắt buộc
├── AGENTS.md                     # Hướng dẫn quy chuẩn cho AI coding agents
└── docker-compose.yml            # Khởi động toàn bộ stack On-Premise
```

---

## 🚀 Hướng Dẫn Khởi Chạy (Getting Started)

### 1. Yêu cầu hệ thống (Prerequisites)
- **Node.js**: phiên bản `>= 18.17.0` (khuyên dùng Node 20 LTS)
- **Python**: phiên bản `>= 3.10`
- **Docker & Docker Compose**: dùng cho Supabase On-Premise và VTO Service

---

### 2. Chạy Frontend Widget & Demo Catalog

```bash
# 1. Đi tới thư mục frontend
cd frontend

# 2. Cài đặt các gói phụ thuộc
npm install

# 3. Khởi động máy chủ phát triển
npm run dev
```

Mở trình duyệt tại [http://localhost:3000](http://localhost:3000) để trải nghiệm:
- **Catalog 50 sản phẩm** với bộ lọc thương hiệu (`Zara`, `Uniqlo`, `H&M`, `Pull&Bear`, `Stradivarius`).
- Nhấn **"Thử Đồ & Chọn Size AI"** trên bất kỳ sản phẩm nào để mở Fitting Widget.
- Sử dụng **ProfileSwitcher** trên thanh Header để chuyển nhanh giữa các hồ sơ (Trang, Minh).

---

### 3. Chạy Backend API (FastAPI)

```bash
# 1. Đi tới thư mục backend
cd backend

# 2. Tạo và kích hoạt môi trường ảo (venv)
python3 -m venv .venv
source .venv/bin/activate

# 3. Cài đặt dependencies từ pyproject.toml
pip install -e ".[dev]"

# Hoặc cài đặt nhanh qua Makefile:
# make install

# 4. Khởi động API server
./.venv/bin/uvicorn app.main:app --reload --port 8000
# hoặc: make dev
```

- Swagger UI tương tác trực tiếp: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI Specification JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

### 4. Khởi chạy toàn bộ hạ tầng On-Premise (Docker)

```bash
# Khởi động Supabase, Backend API và VTO Microservice
docker compose up -d
```

---

## 🧪 Kiểm Chuẩn Chất Lượng (Quality Gate & Constraints)

Dự án áp dụng tiêu chuẩn phát triển khắt khe theo tài liệu [CONSTRAINTS.md](file:///home/nttduong1/projects/ai-fitting/CONSTRAINTS.md):

```bash
cd frontend

# 1. Kiểm tra Typecheck và Linter nghiêm ngặt (0 lỗi, 0 cảnh báo)
npm run check:task

# 2. Kiểm tra đóng gói toàn diện Production Bundle
npm run build
```

- **Zero Suppression Comments:** Tuyệt đối không dùng `@ts-ignore`, `eslint-disable`, `# noqa`.
- **Zero Secrets in Source:** Mọi khóa truy cập và cấu hình dịch vụ quản lý qua biến môi trường.
- **Contract Synchronization:** Định nghĩa Type TypeScript và Pydantic Model luôn đồng bộ 100% với file thiết kế `docs/api/ai_precision_fit_api.yaml`.

---

## 📚 Tài Liệu Tham Khảo (Documentation Links)

- 📋 [Task Tracking & Checklist](docs/plans/tasks/todo.md): Theo dõi tiến độ từng tính năng.
- 📐 [OpenAPI 3.1 Contract](docs/api/ai_precision_fit_api.yaml): Chi tiết thông số các endpoints API.
- 🗺️ [Project Map & Context Index](docs/PROJECT_MAP.md): Hướng dẫn kiến trúc và bản đồ gói ngữ cảnh.
- 🎨 [Figma Design System Spec (Node 8:10 & 8:12)](https://www.figma.com/design/DOGArspqs5nAybRQh5k7OL/AI-Precision-Fit---Mobile-Design-System?node-id=8-10): Quy chuẩn giao diện gốc.
- ⚙️ [Deferred Backend & AI Integration Plan](docs/plans/DEFERRED_BACKEND_AND_AI_INTEGRATION.md): Lộ trình chi tiết tích hợp Backend và AI Service.

---

## 📄 Bản Quyền (License)

Dự án được phân phối dưới giấy phép mã nguồn mở **MIT License**.
