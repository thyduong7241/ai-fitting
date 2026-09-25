# AGENTS.md — AI Precision Fit

> **BẮT BUỘC:** Đọc `CONSTRAINTS.md` trước khi viết code. Không bao giờ nới lỏng hoặc sửa giảm các ràng buộc trong file đó để code chạy qua.

Hướng dẫn cho AI coding agent khi làm việc trong repo này.

## Project overview

AI Precision Fit — widget AI Fitting/Virtual Try-On cho e-commerce thời trang. Shopper upload 2 ảnh (front + side) → nhận size gợi ý + lý do + preview mặc thử. MVP dạng **mobile-first web widget**, chưa build native app, **deploy on-premise** (server nội bộ), toàn bộ AI model **self-host**.

Base repo: `humanstack/vibe-coding-template`.

## Tech stack

| Layer | Công nghệ |
|---|---|
| Frontend | Next.js 15 + React + Tailwind CSS (mobile-first, responsive) |
| Backend API | Python FastAPI |
| Database/Storage/Auth | Supabase **self-hosted** (Docker Compose), không dùng Supabase Cloud |
| Quality gate | MediaPipe Face/Pose Landmarker + OpenCV (Laplacian blur) |
| Body measurement | MediaPipe Pose Landmarker (33 landmarks) + công thức anthropometric |
| Body shape | 2D silhouette warping (rule-based) — chưa dùng SMPL-X/SOMA |
| Fit/size engine | Rule-based scoring, không dùng ML model |
| Explanation text | Template-based (ghép câu theo rule), không gọi LLM API |
| Virtual Try-On | CatVTON, chạy như microservice riêng (`vto-service`) |
| Deploy | Docker Compose, reverse proxy Nginx/Caddy, chạy trên LAN nội bộ |

## Repo structure

```
/frontend        # Next.js app (mobile-first widget)
/backend          # FastAPI app
  /routers         # /quality-check, /measure, /size-recommend, /tryon
  /services         # business logic từng bước pipeline
/vto-service      # CatVTON inference service (tách riêng, có GPU)
/supabase          # config self-hosted (docker-compose override, migrations)
/docker-compose.yml
CLAUDE.md / AGENTS.md
```

## Nguyên tắc code

- **Giữ đơn giản, tránh rườm rà.** Không thêm dependency/service mới nếu chưa thật sự cần cho MVP. Các phần đã chủ động cắt bỏ (xem "Ngoài phạm vi" bên dưới) — không tự ý thêm lại.
- **Quản lý file/script tạm thời:** Các script, dữ liệu test, file tải về tạm thời, dùng 1 lần, không tái sử dụng và không ảnh hưởng đến các service/pipeline chính BẮT BUỘC lưu vào thư mục `tmp/` (đã cấu hình trong `.gitignore`) để không làm nhiễu workspace.
- **Tách module theo từng bước pipeline** (quality-check → measure → fit → tryon) để dễ debug/refactor độc lập. Mỗi bước là 1 router + 1 service riêng trong `backend/`.
- `vto-service` (CatVTON) luôn là service Docker riêng biệt, gọi qua HTTP nội bộ từ `backend` — không import trực tiếp vào FastAPI app để tránh 1 lỗi GPU kéo sập cả API.
- Định nghĩa API contract (request/response schema) bằng Pydantic model trước khi code logic, để frontend có thể mock và code song song.
- Frontend mobile-first: ưu tiên test trên viewport điện thoại, dùng Tailwind responsive utilities, không giả định có bàn phím/chuột.
- Khi cần thêm UI mới, ưu tiên lấy spec từ Figma (Figma Dev Mode MCP) thay vì tự đoán style/spacing.

## Ngoài phạm vi (không code trừ khi được yêu cầu rõ)

- React Native / Expo / native mobile app
- SMPL-X, SOMA hoặc bất kỳ 3D body mesh model nào
- Gọi Claude API / LLM API cho explanation text
- Vercel, EAS Cloud, Railway, Supabase Cloud — mọi thứ deploy ngoài phải chạy on-prem qua Docker Compose

## Environment & secrets

- Dùng `.env` local, không commit secrets.
- Supabase self-hosted: URL + anon/service key lấy từ container nội bộ, không phải project cloud.
- Model weights (MediaPipe `.task`, CatVTON checkpoint) không commit vào git — tải thủ công theo hướng dẫn trong README, hoặc dùng Git LFS nếu cần versioning.

## Testing/Debug

- FastAPI: dùng Swagger UI (`/docs`) để test từng endpoint độc lập.
- Test AI pipeline bằng fixture ảnh mẫu trong `backend/tests/fixtures/` (ảnh người front+side, size chart mẫu, ảnh garment flat-lay).
- Khi sửa `vto-service`, test riêng qua HTTP call trước khi tích hợp lại vào `backend`.

## Coding conventions

- Python: type hints đầy đủ, Pydantic cho schema, format bằng `ruff`/`black`.
- TypeScript: strict mode, component nhỏ gọn theo Figma spec, tránh over-engineering state management (dùng React state/context, chưa cần Redux/Zustand ở MVP này).
- Branch: `main` + feature branches, không cần quy trình phức tạp cho giai đoạn 21 ngày.


## Architecture Details

- **Frontend**: Next.js 14/15 with Tailwind CSS and TypeScript
  - Mobile-first widget design (viewport 390px x 844px centered on desktop, full-width on mobile)
  - Zero-Auth Multi-Profile support (`useProfiles` via `localStorage` + Supabase sync)
  - Fit Engine (`frontend/services/fitEngine.ts`) evaluates user measurements against garment size charts
- **Backend API**: Python FastAPI (`backend/app/`)
  - Modular routers: `/api/v1/quality-check`, `/api/v1/measure`, `/api/v1/size-recommend`, `/api/v1/tryon`
  - Pipeline services: MediaPipe Pose Landmarker, OpenCV blur check, Anthropometric calculation, Rule-based fit scoring
- **VTO Service**: CatVTON inference container (`vto-service/`) running on local GPU
- **Database & Storage**: Supabase Self-Hosted via Docker Compose (`supabase/`)

## Design System Tokens (Figma Node 8:10)

- **Primary Brand**: Teal `#0F766E` (Dark teal: `#115E59`, Light teal: `#CCFBF1`, Glow/Focus: `#14B8A6`)
- **Neutral Dark / Navy**: Canvas/Background `#0B0F19`, Dark Surface `#111827`, Dark Card `#1E293B`
- **Text & Accents**: Text Primary `#F8FAFC`, Text Muted `#94A3B8`, Border `#334155`
- **Fit Status Colors**:
  - Perfect / Vừa vặn: Emerald/Teal (`#10B981` / `#0F766E`)
  - Tight / Hơi ôm: Amber/Orange (`#F59E0B`)
  - Loose / Hơi rộng: Sky Blue (`#0EA5E9`)
  - Extreme (Quá chật / Quá rộng): Rose/Red (`#EF4444`)

## Development Commands

### Frontend (`frontend/`)
```bash
cd frontend
npm install              # Initial setup
npm run dev              # Dev server on http://localhost:3000
npm run build            # Production build check
npm run lint             # ESLint check
npx tsc --noEmit         # TypeScript type check (strict)
```

### Backend (`backend/`)
```bash
cd backend
uvicorn app.main:app --reload --port 8000   # Run API server
# Swagger docs: http://localhost:8000/docs
```

### Docker Services
```bash
docker compose up -d                        # Start all on-prem services
```

## Key Workflows & Boundary Rules

1. **Keep context lean**: Do not load entire monolithic plans when implementing individual tasks. Refer to `docs/PROJECT_MAP.md` for task-focused context slices.
2. **Strict temporary file hygiene**: Any scratch script, test run, or intermediate artifact MUST go into `tmp/` (git-ignored).
3. **Pydantic & TypeScript Sync**: Always sync changes between `frontend/types/fitting.ts` and `backend/app/models/fitting.py` to match `docs/api/ai_precision_fit_api.yaml`.
4. **No External LLM / Cloud Dependencies**: Do not introduce OpenAI, Claude API, Anthropic, or external vector DB calls into the core fitting flow.