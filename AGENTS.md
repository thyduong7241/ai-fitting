# AGENTS.md — AI Precision Fit

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


## Architecture Overview

- **Backend**: Python FastAPI with Supabase integration
- **Frontend**: Next.js with Tailwind CSS and TypeScript
- **Database**: Supabase PostgreSQL with migrations
- **Vector DB**: Qdrant for semantic search
- **LLM Integration**: OpenAI and Anthropic support

## Development Standards

### Code Style
- Use TypeScript for all frontend files
- Use Python type hints for all backend functions
- Follow async/await patterns consistently
- Use snake_case for Python, camelCase for TypeScript
- Include proper error handling in all functions

### Architecture Patterns
- Follow the service layer pattern for external integrations
- Use Pydantic models for API request/response validation
- Implement proper authentication on all protected endpoints
- Use the generic SupabaseDatabaseService for database operations
- Abstract LLM providers through service classes

### File Organization
- Backend: `backend/app/` with api/, models/, services/ subdirectories
- Frontend: `frontend/` with app/, components/, services/ subdirectories
- Database: `supabase/migrations/` for all schema changes
- Rules: `.cursor/rules/` for detailed development guidelines

## Common Patterns

### FastAPI Endpoints
```python
@router.post("/items", response_model=ItemResponse)
async def create_item(
    request: CreateItemRequest,
    current_user: User = Depends(get_current_user)
) -> ItemResponse:
    try:
        # Use service layer
        service = SupabaseDatabaseService("items", ItemResponse)
        result = await service.create({**request.dict(), "user_id": current_user.id})
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### React Components
```tsx
'use client'
export default function ComponentName({ title, onAction }: Props) {
  const [loading, setLoading] = useState(false)

  const handleAction = async () => {
    try {
      setLoading(true)
      await onAction?.()
    } catch (error) {
      console.error('Action failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 rounded-lg border">
      {/* Component content */}
    </div>
  )
}
```

### Database Migrations
```sql
-- Create table with RLS
CREATE TABLE public.items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own items"
  ON public.items
  USING (auth.uid() = user_id);
```

## Development Workflow

1. **Setup**: Run `./first-time.sh` for initial configuration
2. **Development**: Use `make dev` to start all services
3. **Database**: Use `make db-migration-new name=description` for schema changes
4. **Testing**: Visit http://localhost:8000/docs for API testing
5. **Frontend**: Visit http://localhost:3000 for the application

## Key Services

- **SupabaseDatabaseService**: Generic CRUD operations
- **SupabaseAuthService**: User authentication and token management
- **SupabaseStorageService**: File upload and management
- **LLMService**: Text generation with OpenAI/Anthropic
- **EmbeddingService**: Vector embeddings for semantic search
- **QdrantService**: Vector database operations

## Environment Configuration

Required environment variables:
- `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` (required)
- `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY` (for LLM features)
- `QDRANT_URL` and `QDRANT_API_KEY` (for vector database)

## Best Practices

- Always use the service layer for external API calls
- Implement proper error handling with descriptive messages
- Use authentication dependencies on protected endpoints
- Follow the established patterns for consistency
- Test API endpoints using the FastAPI docs interface
- Use database migrations for all schema changes
- Implement proper RLS policies for data security

When adding new features, follow the established patterns and maintain consistency with the existing codebase structure.