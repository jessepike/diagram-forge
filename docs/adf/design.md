---
type: "design"
project: "Diagram Forge Web UI"
version: "0.1"
status: "draft"
brief_ref: "./discover-brief.md"
intent_ref: "./intent.md"
created: "2026-02-27"
updated: "2026-02-27"
---

# Design: Diagram Forge Web UI

## Summary

A single-page web app that exposes diagram-forge's 13 templates through a browser UI. Left panel: template selection + content input. Right panel: generated diagram + download. Settings panel for BYOK API key. Backend is a thin FastAPI wrapper around the existing Python diagram-forge library, deployed on Railway. Frontend is Next.js on Vercel. Monorepo under `web/` in the existing diagram-forge repo.

References `discover-brief.md` for scope, constraints, and success criteria.

---

## Architecture

### System Overview

```
Browser (Next.js SPA on Vercel)
  │
  │ HTTPS — user's browser
  ▼
Next.js API Routes (Vercel serverless functions)
  │ HTTPS + X-API-Secret header (server-side only)
  ▼
FastAPI (Railway)
  │ Python — instantiates diagram-forge providers per request
  ▼
Gemini / OpenAI image generation APIs
  │
  ▼
PNG bytes → base64 → returned through chain → rendered in browser
```

**Key principle:** Next.js API routes act as a secure proxy. The Railway shared secret never reaches the browser. The user's API key travels browser → Next.js route → Railway in-memory only, never logged.

### Repo Structure

```
diagram-forge/
  src/diagram_forge/        # existing MCP server — unchanged
  web/
    frontend/               # Next.js app
      src/app/
        page.tsx            # single-page layout
        api/
          generate/route.ts # proxy: forward to Railway + inject secret
          templates/route.ts
          extract/route.ts  # file text extraction proxy
      package.json
      tailwind.config.ts
      next.config.ts
    api/                    # FastAPI wrapper
      main.py
      routers/
        generate.py
        templates.py
        extract.py
      requirements.txt
      Dockerfile            # for Railway
  src/diagram_forge/        # unchanged
  tests/                    # existing tests unchanged
```

---

## Tech Stack

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| Frontend framework | Next.js (App Router) | 15.x | User preference, Vercel-native, RSC + API routes |
| Styling | Tailwind CSS | 4.x | Utility-first, fast iteration |
| Language (frontend) | TypeScript | 5.x | Type safety |
| Backend framework | FastAPI | 0.115.x | Async, Python 3.11+, matches existing codebase |
| Backend runtime | Python | 3.11+ | Matches diagram-forge requirement |
| PDF extraction | PyMuPDF (fitz) | latest | Fast, reliable PDF text extraction |
| DOCX extraction | python-docx | latest | Standard DOCX parsing |
| Frontend hosting | Vercel | — | Free tier, Vercel-native for Next.js |
| Backend hosting | Railway | — | Simple Python deploy, ~$5/month |

---

## Interface Specification

### Single-Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Diagram Forge                                      [⚙ Settings] │
├──────────────────────────┬──────────────────────────────────────┤
│  LEFT PANEL              │  RIGHT PANEL                         │
│                          │                                      │
│  Template                │  [Empty state: "Your diagram         │
│  ┌────────────────────┐  │   will appear here"]                 │
│  │ ● C4 Container     │  │                                      │
│  │   Architecture     │  │  ← after generation: →              │
│  │   Data Flow        │  │  ┌──────────────────────────┐        │
│  │   Workstreams      │  │  │                          │        │
│  │   ...              │  │  │   [generated diagram]    │        │
│  └────────────────────┘  │  │                          │        │
│                          │  └──────────────────────────┘        │
│  Content                 │                                      │
│  [Paste] [Upload]        │  [Regenerate]  [↓ Download PNG]      │
│  ┌────────────────────┐  │                                      │
│  │                    │  │                                      │
│  │  (text area /      │  │                                      │
│  │   file drop zone)  │  │                                      │
│  └────────────────────┘  │                                      │
│                          │                                      │
│  Provider  [Auto ▾]      │                                      │
│                          │                                      │
│  [▶ Generate Diagram]    │                                      │
└──────────────────────────┴──────────────────────────────────────┘
```

### Settings Panel (slide-out from top-right)

```
┌───────────────────────────────┐
│ ⚙ Settings              [✕]   │
│                               │
│ Provider                      │
│ [Gemini (recommended) ▾]      │
│                               │
│ API Key                       │
│ [•••••••••••••••••] [Show]    │
│                               │
│ [Save for this session]       │
│                               │
│ ── Where do I get a key? ──   │
│ Gemini: aistudio.google.com   │
│ OpenAI: platform.openai.com   │
└───────────────────────────────┘
```

*Note: "Where do I get a key?" links address Success Criterion #1 — helping colleagues onboard without handholding.*

### Template List

Each template card shows: name, one-line description, recommended provider badge. Scrollable list, single-select.

### Content Input

Two tabs:
- **Paste** — textarea, unlimited input
- **Upload** — drag-and-drop or file picker, accepts .pdf/.docx/.md, max 10MB, client-side validation before upload

### States

| State | Left Panel | Right Panel |
|---|---|---|
| Initial | Ready | Empty state with instruction text |
| Generating | Generate button → spinner (disabled) | Skeleton/loading indicator |
| Success | Normal | Diagram image + Regenerate + Download |
| Error | Normal | Error message + Retry button |

---

## API Design

### FastAPI Endpoints (Railway)

All endpoints require `X-API-Secret: {secret}` header.

**`GET /templates`**
```json
Response: [
  {
    "id": "c4_container",
    "name": "C4 Container Diagram",
    "description": "Software system internals, C4 Level 2",
    "recommended_provider": "gemini"
  },
  ...
]
```

**`POST /generate`**
```json
Request: {
  "template_id": "c4_container",
  "content": "...",
  "provider": "gemini",       // or "openai" or "auto"
  "api_key": "...",           // user's key — never logged
  "model": null               // optional override
}

Response: {
  "image_base64": "iVBORw0KGgo...",
  "provider": "gemini",
  "model": "gemini-3-pro-image-preview",
  "cost_usd": 0.04
}
```

**`POST /extract`**
```json
Request: multipart/form-data — file field

Response: {
  "text": "extracted content...",
  "filename": "spec.pdf",
  "char_count": 4821
}
```

**`GET /health`**
```json
Response: { "status": "ok" }
```

### Next.js API Routes (Vercel)

- `GET /api/templates` — proxy to Railway, no auth required from browser
- `POST /api/generate` — proxy to Railway, injects `X-API-Secret` server-side
- `POST /api/extract` — proxy to Railway, injects `X-API-Secret` server-side

---

## Data Model

No database. All state is ephemeral:

| Data | Location | Lifetime |
|---|---|---|
| API key | React state + sessionStorage | Browser session (cleared on tab close) |
| Selected template | React state | Page session |
| Content input | React state | Page session |
| Generated image | React state (base64) | Page session |
| Templates list | React state (fetched once on load) | Page session |

---

## Security

- **API key:** Never logged server-side. FastAPI configured with `access_log=False` for `/generate`. Key in request body, not query params or headers.
- **Shared secret:** Set as env var on Vercel (`RAILWAY_API_SECRET`) and Railway. Injected by Next.js API route. Never in client bundle.
- **CORS:** Railway FastAPI restricts origins to Vercel deployment URL in production.
- **File uploads:** Client-side type + size validation (PDF/DOCX/MD, ≤10MB) before any network call.
- **No persistence:** No database, no logs of user content.

---

## Capabilities Needed

**Frontend:**
- Node.js 20+
- Next.js 15, React 19, TypeScript 5
- Tailwind CSS 4
- No additional state management library (React useState sufficient for MVP)

**Backend:**
- Python 3.11+
- FastAPI, uvicorn
- diagram-forge (installed from local path or pip)
- PyMuPDF, python-docx
- Railway deployment (Dockerfile or nixpacks)

**Infrastructure:**
- Vercel account (existing)
- Railway account (existing)
- Environment variables: `RAILWAY_API_SECRET` on both services, `RAILWAY_API_URL` on Vercel

---

## Decision Log

| Decision | Options | Chosen | Rationale |
|---|---|---|---|
| Repo structure | Separate repo / monorepo | Monorepo (`web/` subdir) | Single place to track; shared CI possible later |
| API key UX | Settings panel / inline / modal | Settings panel | Persistent in session; cleaner for repeat use |
| App layout | Single-page / wizard | Single-page (left/right split) | Power users see everything at once; faster iteration |
| Frontend → backend proxy | Direct from browser / via Next.js routes | Via Next.js API routes | Keeps shared secret server-side; standard pattern |
| Frontend state | Redux / Zustand / useState | useState | No complex state graph; MVP scope; zero dependencies |
| Output delivery | Temp file URL / base64 | base64 in response | Stateless; no file cleanup needed; fine for PNG sizes |

---

## Open Questions

| Question | Deferred To | Notes |
|---|---|---|
| Dockerfile vs nixpacks for Railway deploy | Develop | Both viable; nixpacks is zero-config for Python |
| sessionStorage vs in-memory only for API key | Develop | sessionStorage survives refresh; decide based on UX testing |
| Tailwind dark theme: which specific color palette | Develop | Linear/Zed-inspired dark — implementer picks exact hex values |

---

## Issue Log

| # | Issue | Source | Severity | Status | Resolution |
|---|---|---|---|---|---|
| — | — | — | — | — | Pending review |

## Develop Handoff

### Design Summary
Single-page web app in `web/` monorepo subdir. Next.js (Vercel) proxies to FastAPI (Railway) which wraps the existing diagram-forge Python library. BYOK — user's API key passed per-request, never persisted. No database, no auth.

### Key Decisions for Develop

| Decision | Implication |
|---|---|
| Monorepo `web/` subdir | Create `web/frontend/` and `web/api/` directories |
| Next.js API routes as proxy | All Railway calls go through `/api/*` routes; `RAILWAY_API_SECRET` env var on Vercel |
| base64 image response | No temp file handling; render as `<img src="data:image/png;base64,...">` |
| sessionStorage for API key | Use `sessionStorage.getItem/setItem('df_api_key')` — cleared on tab close |
| PyMuPDF for PDF | `import fitz; doc = fitz.open(stream=...); text = chr(12).join([p.get_text() for p in doc])` |

### Capabilities Needed
- Node.js 20+, npm/pnpm
- Python 3.11+, pip
- Vercel CLI (for deploy)
- Railway CLI (for deploy)
- Env vars: `RAILWAY_API_SECRET` (both), `RAILWAY_API_URL` (Vercel)

### Open Questions for Develop
1. Dockerfile vs nixpacks on Railway — try nixpacks first, fall back to Dockerfile
2. sessionStorage vs in-memory — default to sessionStorage, revisit if security concern
3. Dark theme palette — implement Linear-inspired: bg `#0f0f0f`, surface `#1a1a1a`, border `#2a2a2a`, text `#e5e5e5`, accent `#5b5fc7`

### Success Criteria (Verify During Implementation)
- [ ] A colleague (provided an API key) produces a usable diagram without instructions
- [ ] At least 3 people outside the creator's network discover and use the app within 30 days
- [ ] At least 1 person asks unprompted whether they can pay for it

### What Was Validated
- BYOK key flow reviewed by GPT + Kimi — architecture confirmed sound
- Per-request API key: verified that `get_provider(name, api_key)` already accepts runtime keys
- Output format: providers return PNG bytes — base64 response confirmed feasible

### Implementation Guidance
Recommended build order:
1. `web/api/` — FastAPI skeleton: `/health`, `/templates`, `/generate` (mock response first)
2. `web/frontend/` — Next.js scaffold: layout, panels, Settings component
3. Wire generate flow end-to-end with real diagram-forge call
4. Add file upload + `/extract` endpoint
5. Error states, loading states, polish
6. Deploy: Railway first, then Vercel pointing at Railway URL

### Reference Documents
- `intent.md` → `discover-brief.md` → this file → implement

## Review Log

*Pending — review not yet started.*

## Revision History

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-02-27 | Initial draft from Design intake |
