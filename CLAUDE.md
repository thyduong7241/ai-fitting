# CLAUDE.md — AI Precision Fit

> **MANDATORY:** Read `CONSTRAINTS.md` before writing code. Do not weaken it to make a change pass.

## Project Overview
AI Precision Fit is a mobile-first Virtual Fitting / Size Recommendation widget for fashion e-commerce.
Shoppers upload 2 photos (front + side) or enter measurements -> receive fit recommendation + body hotspot breakdown + CatVTON virtual try-on preview.
Deployment is **on-premise** (internal server via Docker Compose), with self-hosted AI models.

## Tech Stack
- **Frontend**: Next.js 14/15, React 18, Tailwind CSS, TypeScript
- **Backend**: Python FastAPI (async, Pydantic v2)
- **Database/Storage**: Supabase Self-Hosted (Docker Compose)
- **Quality Gate**: MediaPipe Face/Pose Landmarker + OpenCV Laplacian blur
- **Body Measurement**: MediaPipe Pose Landmarker (33 landmarks) + Anthropometric formulas
- **Fit Recommendation**: Rule-based fit scoring against garment size charts (0 external ML/LLM calls)
- **Virtual Try-On**: CatVTON running as an isolated microservice container (`vto-service`)

## Common Commands

### Frontend (`frontend/`)
- Install: `cd frontend && npm install`
- Dev server: `cd frontend && npm run dev`
- Type check: `cd frontend && npx tsc --noEmit`
- Production build: `cd frontend && npm run build`
- Linter: `cd frontend && npm run lint`

### Backend (`backend/`)
- Run API server: `cd backend && uvicorn app.main:app --reload --port 8000`
- API Docs: `http://localhost:8000/docs`

### Temporary Files
- **MUST** store all temporary scripts, test outputs, one-off download files in `tmp/` (already in `.gitignore`). Never create scratch files in root or app folders.

## Coding Conventions
- **TypeScript**: Strict mode, interfaces in `frontend/types/fitting.ts`.
- **Python**: Type annotations, Pydantic models in `backend/app/models/fitting.py`.
- **API Contract**: Defined in `docs/api/ai_precision_fit_api.yaml`.
- **Mobile-first UI**: Viewport 390px x 844px centered on desktop; full screen on mobile.
- **Design Tokens (Figma Node 8:10)**:
  - Primary Teal: `#0F766E` (Dark: `#115E59`, Light: `#CCFBF1`, Glow: `#14B8A6`)
  - Background Canvas: `#0B0F19`, Dark Surface: `#111827`, Card: `#1E293B`
  - Text Primary: `#F8FAFC`, Muted: `#94A3B8`, Border: `#334155`

## Out of Scope (Do Not Add)
- No React Native / Expo
- No SMPL-X / SOMA 3D mesh
- No OpenAI / Anthropic / Claude API calls in core flow
- No Supabase Cloud / Vercel deployment (strictly on-prem Docker)
