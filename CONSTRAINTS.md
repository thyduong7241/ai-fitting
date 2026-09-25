# CONSTRAINTS.md — AI Precision Fit Quality Bar

> Bản cam kết chất lượng kỹ thuật bắt buộc cho toàn bộ coding agents và con người khi phát triển AI Precision Fit.  
> Được thiết lập theo quy chuẩn `constraint-driven-development`.  
> **Nguyên tắc cốt lõi:** Không bao giờ hạ thấp ngưỡng chất lượng để làm code chạy qua (Do not weaken this file to make a change pass).

---

## 1. The Floor (Bắt buộc 100%, tự động Chặn / Block nếu vi phạm)

Bất kỳ vi phạm nào ở tầng này đều **BUỘC PHẢI DỪNG LẠI VÀ SỬA NGAY**, không được phép commit hoặc chuyển sang task tiếp theo:

- ❌ **Cấm thêm suppression comments:** Không dùng `@ts-ignore`, `@ts-expect-error`, `eslint-disable`, `# noqa`, `# type: ignore` để che giấu lỗi.
- ❌ **Cấm stub dở dang:** Không để lại `throw new Error("Not implemented")`, hàm rỗng không xử lý, hoặc khối `catch (e) {}` nuốt lỗi im lặng.
- ❌ **Cấm bỏ qua test:** Không thêm `.skip`, không xóa bỏ test assertions để pass kiểm thử.
- ❌ **Cấm lộ bí mật (Zero Secrets in Source):** Tuyệt đối không commit API keys, token, passwords vào git repository. Mọi cấu hình phải đi qua `.env`.
- ❌ **Cấm tự ý nới lỏng file này:** File này không được phép sửa giảm chỉ số để làm một tính năng pass qua.

---

## 2. Enforced Dimensions (Có số liệu cụ thể)

| Chiều kiểm soát | Quy tắc chuẩn | Lệnh kiểm tra (`Checked by`) | Thời điểm chạy | Cơ chế xử lý |
|---|---|---|---|---|
| **TypeScript (FE)** | 0 lỗi type (`Zero type errors`) | `cd frontend && npx tsc --noEmit` | Sau mỗi edit / task end | **BLOCK** |
| **Linting (FE)** | 0 lỗi linter từ cấu hình dự án | `cd frontend && npm run lint` | Cuối mỗi task | **BLOCK** |
| **API Contract Sync** | 100% đồng bộ Pydantic BE, TS FE & OpenAPI YAML | Đối chiếu `docs/api/ai_precision_fit_api.yaml` | Khi sửa model/type | **BLOCK** |
| **Secrets & Hygiene** | Không có secret trong source, file tạm lưu đúng `tmp/` | `git status` + kiểm tra `.gitignore` | Trước khi bàn giao | **BLOCK** |
| **Dependencies Security** | 0 lỗ hổng nghiêm trọng (High / Critical) | `cd frontend && npm audit` | Task end / CI | **BLOCK** |
| **Logic Test Coverage** | Core modules (`fitEngine`, `useProfiles`) ≥ 80% | `cd frontend && npm run test` (Vitest) | Cuối Phase / Task | **WARN** (Phase 0-1) → **BLOCK** (Phase 2+) |

---

## 3. Measured, Not Yet Enforced (Chỉ số đo lường Ratchet)

*Quy tắc Ratchet: Số liệu hiện tại được ghi nhận làm baseline; code mới có thể nâng cao chỉ số nhưng tuyệt đối không được làm tụt giảm.*

| Chỉ số theo dõi | Baseline hiện tại | Hướng phát triển | Mục tiêu hoàn thiện |
|---|---|---|---|
| **Lỗi Type TypeScript** | 2 lỗi ban đầu (đang fix ở Task 0.1) | Phải về 0 và giữ vững ở mức 0 | 0 lỗi |
| **Unit Test Coverage (fitEngine)** | 0% (Chưa cài Vitest) | Tăng dần qua từng phase | ≥ 80% khi hoàn thành Task 2.7 |
| **Thời gian Fast Check Loop** | ~15 giây (`tsc`) | Giữ dưới 60 giây | ≤ 30-45 giây |
| **Tải lượng ảnh sản phẩm** | 50 sản phẩm WebP | Không vượt quá 10MB tổng public assets | Tối ưu nén WebP |

---

## 4. Lifecyle Execution Budget

Để đảm bảo tốc độ phản hồi nhanh (**30 - 60 giây** feedback loop) mà không làm chậm nhịp độ Vibe Coding:

1. **Sau mỗi file edit (Fast Loop < 10s):**
   - Chỉ chạy typecheck cục bộ: `cd frontend && npx tsc --noEmit`
2. **Khi hoàn thành 1 Task (Task Verification 30 - 60s):**
   - Chạy: `cd frontend && npx tsc --noEmit && npm run lint`
   - Chạy unit tests cho component/service vừa sửa (nếu có).
3. **Khi kết thúc 1 Checkpoint / Phase (Review Gate 60 - 90s):**
   - Chạy: `cd frontend && npm run build` (kiểm tra toàn diện Next.js build).

---

## 5. Exceptions (Bảng ngoại lệ được phê duyệt)

*Mọi ngoại lệ phải có ID, lý do chính đáng, người sở hữu và thời hạn hết hạn. Tuyệt đối không thêm ngoại lệ ẩn.*

| ID | Quy tắc ngoại lệ | Đường dẫn file | Lý do kỹ thuật | Người sở hữu | Hạn chót |
|---|---|---|---|---|---|
| **EX-01** | `auth/LoginForm.tsx` type mismatch | `frontend/components/auth/LoginForm.tsx` | Boilerplate auth cũ từ starter template, sẽ dọn dẹp hoặc thay thế | @lead | Task 3.2 |
| **EX-02** | Test coverage chưa bắt buộc chặn | `frontend/components/fitting/*` | Tập trung hoàn thiện giao diện Vibe Coding 10 màn hình trước | @lead | Phase 2 Checkpoint |
