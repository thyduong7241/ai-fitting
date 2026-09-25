# Authoritative Sources & Implementation Standards

> **Tuân thủ quy trình:** `source-driven-development`  
> Mọi quyết định kỹ thuật theo framework trong dự án đều được đối chiếu trực tiếp từ tài liệu chính thức (Official Documentation).

---

## 1. Stack & Version Matrix

| Công nghệ | Phiên bản thực tế | Nguồn xác định |
|---|---|---|
| **Next.js** | `14.1.0` (App Router) | `frontend/package.json` |
| **React** | `18.2.0` | `frontend/package.json` |
| **Tailwind CSS** | `3.4.1` (Tailwind v3) | `frontend/package.json` |
| **TypeScript** | `5.3.3` (Strict mode) | `frontend/package.json` & `tsconfig.json` |
| **Python FastAPI** | `0.115.*` | `backend/requirements.txt` |
| **Pydantic** | `2.6.*` (Pydantic v2) | `backend/requirements.txt` |

---

## 2. Official Documentation Citations & Verified Patterns

### 2.1. Next.js 14 Font Optimization (`Be_Vietnam_Pro`)
- **Tài liệu chính thức:** [Next.js Font Optimization — Google Fonts](https://nextjs.org/docs/app/getting-started/fonts)
- **Đặc tả áp dụng:**
  Next.js 14 cung cấp module `next/font/google` tự động tải và self-host font tại build time, loại bỏ network request tới Google, chống Layout Shift (CLS = 0).
- **Mã nguồn chuẩn:**
  ```tsx
  // frontend/app/layout.tsx
  import { Be_Vietnam_Pro } from 'next/font/google';

  const beVietnamPro = Be_Vietnam_Pro({
    weight: ['400', '500', '600', '700'],
    subsets: ['latin', 'vietnamese'],
    variable: '--font-be-vietnam-pro',
    display: 'swap',
  });

  export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
      <html lang="vi" className={beVietnamPro.variable}>
        <body className="font-sans antialiased">{children}</body>
      </html>
    );
  }
  ```

### 2.2. Tailwind CSS v3.4 Theme Configuration
- **Tài liệu chính thức:** [Tailwind CSS v3 Theme Customization](https://tailwindcss.com/docs/theme)
- **Đặc tả áp dụng:**
  Kết hợp CSS variable `--font-be-vietnam-pro` vào `fontFamily.sans` và cấu hình bộ màu Figma (Node 8:10 & 8:12) mở rộng trong `theme.extend`:
  ```js
  // frontend/tailwind.config.js
  /** @type {import('tailwindcss').Config} */
  module.exports = {
    content: [
      './app/**/*.{js,ts,jsx,tsx,mdx}',
      './components/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
      extend: {
        fontFamily: {
          sans: ['var(--font-be-vietnam-pro)', 'Inter', 'sans-serif'],
        },
        colors: {
          brand: {
            teal: '#16ABAD',
            'teal-hover': '#1AB8B8',
            'teal-subtle': '#DBF7F5',
            'teal-match': '#1F9C7A',
            navy: '#183247',
            'navy-deep': '#0E1F2E',
            slate: '#425C75',
            muted: '#5C738C',
            subtle: '#708AA5',
          },
        },
        borderRadius: {
          '14': '14px',
          '16': '16px',
          '28': '28px',
        },
      },
    },
    plugins: [],
  };
  ```

### 2.3. React 18 Hydration-Safe Client Storage Hook (`useProfiles.ts`)
- **Tài liệu chính thức:** [React Docs: Synchronizing with Effects & useSyncExternalStore](https://react.dev/reference/react/useSyncExternalStore) & [Next.js Hydration Error Guidance](https://nextjs.org/docs/messages/react-hydration-error)
- **Vấn đề tránh:** Next.js render trên server không có `window.localStorage`. Nếu đọc `localStorage` trực tiếp khi khởi tạo component state, SSR HTML và Client HTML sẽ lệch nhau dẫn đến crash hydration.
- **Mã nguồn chuẩn:**
  ```tsx
  // frontend/hooks/useProfiles.ts
  'use client';
  import { useState, useEffect } from 'react';
  import { UserProfile } from '@/types/fitting';
  import { DEFAULT_PROFILES } from '@/data/mockFittingData';

  const STORAGE_KEY = 'ai_precision_fit_profiles';

  export function useProfiles() {
    const [profiles, setProfiles] = useState<UserProfile[]>(DEFAULT_PROFILES);
    const [activeId, setActiveId] = useState<string>(DEFAULT_PROFILES[0].id);
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed) && parsed.length > 0) {
            setProfiles(parsed);
            setActiveId(parsed[0].id);
          }
        }
      } catch (err) {
        console.error('Failed to load profiles from localStorage', err);
      } finally {
        setIsLoaded(true);
      }
    }, []);

    // Đồng bộ khi profiles thay đổi sau mount
    useEffect(() => {
      if (isLoaded) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(profiles));
      }
    }, [profiles, isLoaded]);

    return { profiles, activeProfile: profiles.find(p => p.id === activeId) || profiles[0], isLoaded };
  }
  ```

### 2.4. Pydantic v2 Schema Modeling (FastAPI 0.115.*)
- **Tài liệu chính thức:** [Pydantic v2 Migration Guide & Models](https://docs.pydantic.dev/latest/migration/)
- **Đặc tả áp dụng:**
  Sử dụng cú pháp Pydantic v2:
  - Khai báo model kế thừa `BaseModel`.
  - Sử dụng `Field(..., description=...)` cho siêu dữ liệu OpenAPI.
  - Sử dụng `Literal[...]` từ `typing` cho enum validation chặt chẽ.
  - Khi export data, dùng `model.model_dump()` thay vì phương thức cũ `model.dict()`.
