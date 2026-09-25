# Specification: Virtual Try-On (VTO) Modal & Experience Flow

> **Nguồn trích xuất (Source of Truth):** [Figma Node 8:12 — 09 Virtual Try-On](https://www.figma.com/design/DOGArspqs5nAybRQh5k7OL/AI-Precision-Fit---Mobile-Design-System?node-id=8-12)  
> **Tuân thủ quy trình:** `spec-driven-development`  
> **Áp dụng cho:** Task 2.9 (`VTOPreviewModal.tsx`), Task 1.1 (Theme Tokens), Task 1.3 (UI Primitives) trong `docs/plans/vibe_coding_first_plan.md`

---

## 1. Objective & User Story

- **Objective:** Cung cấp trải nghiệm Thử đồ ảo (Virtual Try-On) dạng Mobile Bottom Sheet / Modal mượt mà, minh bạch về quyền riêng tư và đồng bộ với hệ thống Fit Recommendation.
- **User Story:**
  - Người dùng sau khi nhận size khuyên dùng có thể bấm **"Thử đồ ảo"** (AI Try-On).
  - Nếu profile đã có ảnh toàn thân hợp lệ (vd: Trang), hệ thống lập tức hiển thị thông tin hồ sơ và cho phép chọn size để tạo ảnh mà không cần tải lại ảnh.
  - Nếu profile chưa có ảnh (vd: chỉ nhập tay số đo), hiển thị hướng dẫn chụp chuẩn và cho phép tải ảnh lên kèm kiểm định chất lượng (Quality Gate) tức thì.
  - Quá trình inference hiển thị tiến trình trực quan (% + thông báo trạng thái "Đang khớp trang phục...").
  - Màn hình kết quả hiển thị ảnh mặc thử, bộ đổi màu/size trực tiếp kèm đánh giá độ ôm từng vùng cơ thể và nút CTA Mua ngay/Thêm vào giỏ.
  - Xử lý đầy đủ các nhánh lỗi (Failure/Retry) và xác nhận dừng preview (CancelConfirm).

---

## 2. Design System Tokens (Figma Node 8:12 Exact Specifications)

### 2.1. Typography (`Be Vietnam Pro`)
*Lưu ý: Thiết kế sử dụng font **`Be Vietnam Pro`** (thay vì chỉ dùng Inter như giả định ban đầu), tối ưu hoàn hảo cho hiển thị tiếng Việt.*

| Vai trò | Phông & Trọng lượng | Kích thước / Line-height | Ví dụ áp dụng |
|---|---|---|---|
| **Display / Modal Title** | Be Vietnam Pro SemiBold (600) | `24px` / `30px` (hoặc `20px` / `25px`) | "Dùng ảnh đã lưu của bạn", "Chọn ảnh toàn thân" |
| **Section Header** | Be Vietnam Pro SemiBold (600) | `17px` / `22px` | "Áo khoác Cloudline", "Chưa có ảnh toàn thân" |
| **Subtitle / Strong Body**| Be Vietnam Pro SemiBold (600) | `14px` / `18px`, `15px` / `19px` | "Trang", "Tạo ảnh thử đồ", Tên sản phẩm |
| **Body Regular** | Be Vietnam Pro Regular (400) | `13px` / `16px`, `12px` / `15px` | Mô tả hướng dẫn, disclaimer bản quyền |
| **Body Medium** | Be Vietnam Pro Medium (500) | `12px` / `15px`, `13px` / `16px` | Số đo cơ thể: `165 cm · 56 kg · 86 / 70 / 92 cm` |
| **Badge / Caption / Step** | Be Vietnam Pro SemiBold (600) | `11px` / `14px` | Step `1/3`, `2/3`, `3/3`, `AI PREVIEW`, Size pills |
| **Micro Caption** | Be Vietnam Pro Regular/Medium (400/500) | `10px` / `13px` | "Thường mất khoảng 10–20 giây" |

### 2.2. Color Palette (Bảng màu chuẩn xác)

```css
/* Brand Teal Accent */
--teal-primary: #16ABAD;       /* Nút CTA chính, active state, accent highlight */
--teal-hover:   #1AB8B8;       /* Hover / Focus glow */
--teal-subtle:  #DBF7F5;       /* Pill background, light badge, progress fill */
--teal-light:   #BFF3E7;       /* Highlight tint */
--teal-match:   #1F9C7A;       /* Emerald teal: 'Ảnh đã xác minh', '✓ Ảnh đạt yêu cầu' */

/* Dark Navy & Slate (Text & Surfaces) */
--navy-primary: #183247;       /* Header chính, Primary Action dark text, icon, title */
--navy-deep:    #0E1F2E;       /* Deep surface container */
--slate-body:   #425C75;       /* Subtitle, body copy, active label */
--slate-muted:  #5C738C;       /* Secondary description, disclaimer text */
--slate-subtle: #708AA5;       /* Placeholder, timestamp, micro hints */

/* Borders & Dividers */
--border-light:  #DFEBEF;      /* Viền card, viền ảnh preview */
--border-medium: #DBE5ED;      /* Viền phân cách sections */
--border-focus:  #D1E3E8;      /* Viền khi hover hoặc active */

/* Backgrounds & Canvas */
--surface-white: #FFFFFF;      /* Sheet container, card trắng */
--canvas-tint:   #F6FBFA;      /* Nền modal sheet, tinted container */
--canvas-card:   #F7FBFC;      /* Background card phụ */
```

### 2.3. Corner Radii & Shadows
- **Modal Sheet Top Radius:** `28px` (hoặc `22px`)
- **Card Containers:** `16px`, `14px`, `12px`
- **Pills / Badges / Circular Buttons:** `9999px` (full rounded)
- **Small Badges / Inner Tags:** `4px`
- **Backdrop Overlay:** `rgba(14, 31, 46, 0.6)` với `backdrop-blur-sm`

---

## 3. Screen Specifications (8 State Machines in VTO Journey)

```
[Screen 1: S08/VTO/ConfirmSavedPhoto] (1/3)
       │
       ├─ (Nếu chưa có ảnh) ──→ [Screen 2: S08/VTO/NoSavedPhoto] (1/3)
       │                                     │
       │                                     ▼
       │                         [Screen 3: S08/VTO/UploadPhoto] (2/3)
       │                                     │
       │                                     ▼
       │                         [Screen 4: S08/VTO/PhotoVerified] (2/3)
       │                                     │
       └─────────────────────────────────────┘
                         │
                         ▼
             [Screen 5: S08/VTO/Processing-M] (3/3)
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
[Screen 6: S08/VTO/Result-M-Be]    [Screen 7: S08/VTO/Failure]
        │                                 │
   (Mua ngay / Giỏ)                 (Thử lại CTA)
```

### Chi tiết từng màn hình:

#### State 1: `ConfirmSavedPhoto` (Đã có ảnh trong hồ sơ)
- **Top Bar:** Back button `←`, Title "Thử đồ ảo", Step counter `1/3`.
- **Title Block:** "Dùng ảnh đã lưu của bạn" — "Hồ sơ [Tên] đã có ảnh toàn thân. Bạn không cần tải lại ảnh."
- **Profile Info Card (`r=16px`, bg: `#F7FBFC`, border: `#DFEBEF`):**
  - Tên profile (vd: "Trang"), tag "Hồ sơ dáng mặc định".
  - Thước đo: `165 cm · 56 kg · 86 / 70 / 92 cm`.
  - Badge trạng thái: `✓ Ảnh đã xác minh` (Màu xanh `#1F9C7A`, bg `#DBF7F5`).
  - Action link: `Đổi ảnh ›`.
- **Product Context:** "Hệ thống sẽ dùng ảnh này để tạo preview cho [Tên Garment]."
- **Size Selector:** "Chọn size" kèm các nút pill `[XS] [S] [M] [L] [XL]` (M được highlight với border teal).
- **Privacy Notice:** `✦ Riêng tư & có kiểm soát: Ảnh chỉ dùng cho preview và được xóa theo chính sách dữ liệu của demo.`
- **Bottom CTA:** Nút "Tạo ảnh thử đồ" (bg: `#16ABAD` hoặc `#183247`, text: `#FFFFFF`, `r=14px`, h: `50px`).

#### State 2: `NoSavedPhoto` (Chưa có ảnh toàn thân)
- **Top Bar:** Back button `←`, Title "Thử đồ ảo", Step `1/3`.
- **Title Block:** "Chưa có ảnh toàn thân" — "Bạn chỉ cần thêm một ảnh. Hệ thống sẽ kiểm tra ảnh trước khi tạo preview."
- **Status Card:** "Hồ sơ dáng · [Tên]", "Số đo đã có" (vẫn đủ để tư vấn size, chỉ thiếu ảnh để thử đồ).
- **Photo Guidelines Box (`r=14px`, bg: `#FFFFFF`, border: `#DFEBEF`):**
  - `✓ Đủ đầu đến chân`
  - `✓ Đứng thẳng, tay thả tự nhiên`
  - `✓ Ánh sáng đều, nền đơn giản`
  - `✕ Không selfie gương hoặc cắt chân`
- **Bottom CTA:** Nút "Thêm ảnh ›".

#### State 3: `UploadPhoto` (Tải ảnh mới)
- **Top Bar:** Back `←`, Title "Thêm ảnh cho thử đồ", Step `2/3`.
- **Title Block:** "Chọn ảnh toàn thân" — "Ảnh sẽ được kiểm tra chất lượng trước."
- **Reference Card:** Ảnh minh họa chuẩn mẫu ("Ảnh mẫu chuẩn: Toàn thân · đứng thẳng · đủ đầu đến chân").
- **Checkbox / Switch:** `Lưu ảnh vào hồ sơ [Tên]: Dùng lại cho lần thử đồ sau`.
- **Bottom CTA:** Input file ẩn kích hoạt qua nút "Chọn ảnh".

#### State 4: `PhotoVerified` (Ảnh đã đạt kiểm định)
- **Top Bar:** Title "Kiểm tra ảnh", Step `2/3`.
- **Card Preview:** Khung hiển thị ảnh vừa upload kèm badge `✓ Ảnh đạt yêu cầu`.
- **Ghi chú:** "Sẽ lưu vào hồ sơ [Tên]. Bạn có thể thay đổi lựa chọn này bất kỳ lúc nào."
- **Bottom CTA:** Nút "Tạo ảnh thử đồ" (kích hoạt API VTO job).

#### State 5: `Processing` (Đang sinh ảnh AI)
- **Top Bar:** Title "Tạo ảnh thử đồ", Step `3/3`.
- **Content Block:**
  - "Đang dựng [Tên Garment] trên ảnh của bạn"
  - "Giữ nguyên vóc dáng và khuôn mặt, chỉ thay trang phục."
- **Animated Progress Ring / Radar:**
  - Hiển thị tỷ lệ phần trăm (vd: `76%`), biểu tượng lấp lánh `✦`.
  - Trạng thái động: `Đang khớp trang phục · màu [Màu] · Size [Size]`.
  - Thời gian ước lượng: `Thường mất khoảng 10–20 giây`.
- **Nút Back bấm vào:** Mở dialog `CancelConfirm` ("Dừng tạo preview?").

#### State 6: `Result` (Kết quả mặc thử)
- **Header:** Title "Thử đồ ảo", Tên Garment, Size đã chọn (vd: "Áo khoác Cloudline · Size M").
- **Hero Image Container (`r=16px`, overflow hidden):**
  - Ảnh kết quả thử đồ CatVTON độ phân giải cao.
  - Tag góc trên: `AI PREVIEW` (bg: `rgba(24,50,71,0.75)`, text: `#FFFFFF`, `r=4px`).
- **Color Selector:** "Màu": các pill `[Be]` `[Xanh trời]` `[Xám than]`.
- **Size Selector:** "Size": các pill `[S]` `[M]` `[L]`. Khi đổi size, tự động chuyển ảnh preview tương ứng.
- **Fit Breakdown Callout:**
  - Vd (Size M): `Vai vừa vặn · ngực vừa vặn · eo hơi ôm` (Chấm teal).
  - Vd (Size L): `Vai hơi rộng · ngực hơi rộng · eo vừa vặn` (Chấm xanh dương).
- **CTA Actions:** Nút "Thêm vào giỏ" (Secondary: border `#DBE5ED`) + Nút "Mua ngay" (Primary: bg `#16ABAD`, text `#FFFFFF`).
- **Disclaimer Footer:** `Preview minh họa kiểu dáng và màu sắc. Tư vấn độ vừa dựa trên số đo của bạn.`

#### State 7: `Failure` (Xử lý sự cố)
- **Icon:** Dấu chấm than cảnh báo màu hổ phách/đỏ `!`.
- **Title:** "Chưa thể tạo ảnh thử đồ".
- **Body:** "Kết nối tạo ảnh đang gặp sự cố. Kết quả tư vấn size [M] của bạn vẫn được giữ nguyên."
- **CTA:** Nút "Thử lại".

#### State 8: `CancelConfirm` (Xác nhận hủy)
- **Dialog Sheet:** "Dừng tạo preview?".
- **Body:** "Bạn có thể quay lại chọn size hoặc tiếp tục chờ. Kết quả Fit Intelligence vẫn được giữ nguyên."
- **Actions:** Nút "Tiếp tục chờ" (Primary) và Link "Dừng preview và quay lại" (Secondary text).

---

## 4. Commands

```bash
# Frontend dev & type verification
cd frontend
npm run dev
npx tsc --noEmit
npm run lint

# Backend CatVTON integration test mock endpoint
curl -X POST http://localhost:8000/api/v1/tryon \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"p-trang-01","garment_id":"garment-001","person_image_url":"/mock/trang.webp","garment_image_url":"/products/coolmate/jacket-01.webp"}'
```

---

## 5. Implementation Boundaries

- **Always:**
  - Áp dụng font `Be Vietnam Pro` (fallback: `Inter`, `sans-serif`).
  - Dùng đúng mã hex: Teal `#16ABAD`, Navy `#183247`, Muted `#5C738C`, Canvas `#F6FBFA`.
  - Cho phép người dùng đóng modal bằng nút `✕`, nút `←` hoặc bấm ngoài backdrop.
  - Giữ nguyên số đo và size khuyên dùng kể cả khi VTO fail.
- **Ask First:**
  - Thay đổi flow bước 1/3, 2/3, 3/3 hoặc cắt bỏ bất kỳ màn hình cảnh báo nào.
- **Never:**
  - Gọi LLM ngoài để sinh câu disclaimer (dùng cố định các chuỗi tiếng Việt trích xuất từ Figma).
  - Tải file ảnh trực tiếp lên server đám mây của bên thứ ba.
