# AI Precision Fit — Tech Stack (Final)

**Phạm vi:** Mobile-first web widget, chưa build native app, deploy on-premise (server nội bộ), self-host toàn bộ AI model, tối ưu cho vibe coding với Claude Code + Figma.

---

## 1. Frontend — Mobile-first Web Widget

| Thành phần | Lựa chọn | Ghi chú |
|---|---|---|
| Framework | **Next.js 15 + React + Tailwind** | Responsive mobile-first, chạy trực tiếp trên browser điện thoại qua LAN nội bộ, không cần build native/simulator |
| Camera/Upload | **HTML `<input capture>` / MediaDevices API** | Mở camera trực tiếp qua browser |
| Design → Code | **Figma Dev Mode MCP Server** | Claude Code đọc token/spec component từ Figma, sinh thẳng React/Tailwind component đúng design |

> Mở rộng sau: nếu cần native app thật, wrap UI hiện tại bằng Expo/Capacitor mà không phải viết lại từ đầu.

---

## 2. Backend

| Thành phần | Lựa chọn | Ghi chú |
|---|---|---|
| API framework | **Python FastAPI** | Async, Swagger UI tự sinh giúp debug nhanh, dễ tách module theo từng bước pipeline để refactor độc lập |
| Database + Storage + Auth | **Supabase self-hosted (Docker Compose)** | 1 lệnh `docker compose up`, giữ nguyên SDK/dev experience quen thuộc nhưng chạy 100% nội bộ |

---

## 3. AI Pipeline (self-host, không tốn phí API)

| Bước | Model/Công nghệ | VRAM/Yêu cầu | Ghi chú |
|---|---|---|---|
| Quality Gate | **MediaPipe Face/Pose Landmarker** + OpenCV Laplacian blur | CPU | Check đủ người/pose/ánh sáng, blur detection <50ms |
| Body Measurement | **MediaPipe Pose Landmarker** (33 landmarks) + công thức anthropometric | CPU | Đủ chính xác cho MVP (~2-3cm sai số) |
| Body Shape (nếu cần hiển thị hình dạng) | **2D silhouette warping** từ landmarks (rule-based) | CPU | Ưu tiên hướng nhẹ; nâng cấp lên SOMA (Apache 2.0, parametric 3D) sau nếu cần mesh 3D thật |
| Fit/Size Recommendation | **Rule-based fit scoring** (tự code) | — | Không cần model, 0 phụ thuộc |
| Explanation text | **Template-based** (ghép câu theo rule) | — | Cắt LLM khỏi core flow; có thể thêm Ollama local (Qwen2.5-3B) sau nếu cần câu tự nhiên hơn |
| Virtual Try-On | **CatVTON** | <8GB VRAM | Model nhẹ nhất (899M params), tách thành microservice riêng để dễ restart/debug/scale. ⚠️ License research-only — phù hợp PoC/demo nội bộ |

---

## 4. Deploy — On-premise Docker Compose

```
services:
  web          # Next.js frontend
  api          # FastAPI backend
  supabase     # Self-hosted Postgres + Storage + Auth
  vto-service  # CatVTON microservice (GPU)
  nginx/caddy  # Reverse proxy
```

- Truy cập demo qua IP LAN từ điện thoại.
- `vto-service` tách riêng khỏi `api` để 1 service lỗi không kéo sập toàn hệ thống.

---

## 5. Dev Workflow

- **Claude Code** + file `CLAUDE.md` ở root repo (mô tả stack, quy ước code, cấu trúc folder).
- **Figma Dev Mode MCP** đã setup để sinh UI khớp design.
- Monorepo (frontend + backend chung repo) cho dễ quản lý trong phạm vi team nhỏ/1 người.

---

## 6. Đã cắt bỏ để giảm rườm rà (mở rộng sau nếu cần)

- ❌ React Native/Expo — chưa cần native app ở giai đoạn này
- ❌ SMPL-X/SOMA (3D body mesh) — dùng 2D silhouette trước
- ❌ Claude API cho explanation — template-based đủ cho demo
- ❌ Vercel/EAS Cloud/Railway — toàn bộ chạy on-prem qua Docker Compose

---

## 7. Chuẩn bị trước khi bắt đầu code

1. Export design tokens (màu, typography, spacing) từ Figma.
2. Note các state UI còn thiếu trong Figma (loading, error, ảnh reject, empty state).
3. Định nghĩa API contract trước (`/quality-check`, `/measure`, `/size-recommend`, `/tryon`) — mock để FE/BE code song song.
4. Chuẩn bị data test: ảnh người mẫu (front+side), size chart mẫu, ảnh garment flat-lay.
5. Tải sẵn MediaPipe model files (.task) và CatVTON checkpoint (HuggingFace) — test chạy thử trước khi tích hợp.
6. Setup `.env` template, Supabase project local, GPU instance nội bộ.
