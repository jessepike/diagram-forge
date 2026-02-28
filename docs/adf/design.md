---
type: "design"
project: "Diagram Forge Web UI"
version: "0.3"
status: "review-complete"
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

Each template card shows: name, one-line description, recommended provider badge. Scrollable list, single-select. If `recommended_provider` is null, the badge is hidden.

### Provider & API Key Flow

Settings panel is the single source of truth for provider + API key configuration for the session. The left panel **Provider [Auto ▾]** defaults to `auto` (meaning: use whatever provider is configured in Settings). Users can override per-generation — useful if they have keys for multiple providers.

**Resolution rule:** The frontend always resolves `auto` to an explicit provider name before calling `POST /api/generate`. The backend never receives `"auto"`. If the left panel is set to `auto`, the frontend substitutes `Settings.provider`. This means the backend can enforce that `provider` is always one of `"gemini"` or `"openai"`.

### Content Input

Two tabs:
- **Paste** — textarea, max 50,000 characters (enforced client-side on input, server-side on POST /generate with HTTP 400)
- **Upload** — drag-and-drop or file picker, accepts .pdf/.docx/.md, max 10MB, client-side validation before upload

**File extraction flow:** On file selection, the client immediately calls `POST /api/extract`. The returned text populates the content textarea and the UI switches to the Paste tab. The user can review and edit the extracted content before clicking Generate.

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
    "recommended_provider": "gemini"   // or null — frontend hides badge when null
  },
  ...
]
```

Note: `description` covers use case context; no separate `use_case` field is needed.

**`POST /generate`**
```json
Request: {
  "template_id": "c4_container",
  "content": "...",           // max 50,000 characters; backend returns 400 if exceeded
  "provider": "gemini",       // or "openai" — frontend resolves "auto" before calling Railway; backend always receives an explicit value
  "api_key": "...",           // user's key — never logged
  "model": null               // optional override
}

Response: {
  "image_base64": "iVBORw0KGgo...",
  "provider": "gemini",
  "model": "gemini-3-pro-image-preview",
  "cost_usd": 0.04
}

**Size constraint:** Backend must enforce a maximum PNG output size of 3MB (raw bytes before base64 encoding). Base64 inflates ~33%, keeping the response under Vercel's 4.5MB serverless body limit. If the provider returns a larger image, the backend returns HTTP 413. Frontend renders this as the Error state with message "Diagram too large — try reducing input length."

**Timeout:** Railway request timeout: 120s. Vercel API route timeout: 60s (Hobby plan). Frontend should show the Error state after 60s with message "Generation timed out — try again."
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

- **API key:** Never logged server-side. FastAPI configured with `access_log=False` for `/generate`. Key in request body, not query params or headers. Exception handlers must redact `api_key` before any logging — use a custom exception handler that strips sensitive fields from request body before error output.
- **Shared secret:** Set as env var on Vercel (`RAILWAY_API_SECRET`) and Railway. Injected by Next.js API route. Never in client bundle.
- **CORS:** Railway FastAPI restricts origins to Vercel deployment URL in production.
- **File uploads:** Client-side type + size validation (PDF/DOCX/MD, ≤10MB) before any network call. Server-side: FastAPI enforces max body size and validates MIME type; PyMuPDF/python-docx parse failures return HTTP 422 (not 500).
- **No persistence:** No database, no logs of user content.
- **Request limits:** FastAPI enforces max body size on `/extract` (10MB). No rate limiting in v1 — acceptable for prototype; Railway's natural resource limits act as a soft cap.

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
| Railway deploy method | Develop | Dockerfile — nixpacks not used |
| sessionStorage vs in-memory only for API key | Develop | sessionStorage survives refresh; decide based on UX testing |
| Theme | Develop | Light theme — palette TBD from design prototype |

---

## Issue Log

| # | Issue | Source | Severity | Status | Resolution |
|---|---|---|---|---|---|
| 1 | Provider shown in both left panel and Settings — relationship undefined; developer won't know which drives the API call | Ralph-Design | High | Resolved | Added "Provider & API Key Flow" section: Settings = session config, left panel = per-generation override (default auto = Settings provider). Frontend always resolves before API call. |
| 2 | "auto" provider value behavior undefined — backend unspecified | Ralph-Design | High | Resolved | "auto" is frontend-resolved only; backend always receives explicit "gemini" or "openai". Clarified in POST /generate request spec and Provider & API Key Flow section. |
| 3 | File extraction timing unspecified — /extract called on file selection or deferred to Generate? | Ralph-Design | High | Resolved | Added to Content Input section: on file selection, client calls /extract immediately, populates textarea, switches to Paste tab for user review before Generate. |
| 4 | Template "use case" field in Brief not present in GET /templates response | Ralph-Design | Low | Resolved | "description" field covers use case context. Added note to GET /templates spec. |
| 5 | recommended_provider null case not handled in template card rendering | Ralph-Design | Low | Resolved | Badge hidden when null. Noted in Template List spec. |
| 6 | Base64 response path — ~33% inflation risks hitting Vercel 4.5MB serverless body limit; no timeout specified | GPT | High | Resolved | Added size constraint (3MB raw PNG max, 413 on exceed) and timeout spec (60s Vercel, 120s Railway) to POST /generate |
| 7 | "Unlimited input" for Paste conflicts with provider token/size limits — no max defined | GPT | High | Resolved | Capped at 50,000 chars; enforced client-side + server-side (400); noted in Content Input and POST /generate request |
| 8 | No abuse/DoS protection on Railway via Vercel proxy | GPT | Medium | Resolved | Added to Security: no rate limiting in v1; Railway resource limits as soft cap; FastAPI max body size on /extract |
| 9 | "Never logged" guarantee underspecified — exception traces can capture api_key from request body | GPT | Medium | Resolved | Added to Security: custom exception handler required that strips api_key before logging |
| 10 | /extract relies on client-side validation only — malformed files can crash PyMuPDF/python-docx workers | GPT | Medium | Resolved | Added to Security: server-side MIME validation + 422 on parse failure |

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
| File extraction UX | On file selection → call `POST /api/extract` immediately → populate textarea content → switch to Paste tab |
| PyMuPDF for PDF | `import fitz; doc = fitz.open(stream=...); text = chr(12).join([p.get_text() for p in doc])` |

### Capabilities Needed
- Node.js 20+, npm/pnpm
- Python 3.11+, pip
- Vercel CLI (for deploy)
- Railway CLI (for deploy)
- Env vars: `RAILWAY_API_SECRET` (both), `RAILWAY_API_URL` (Vercel)

### Open Questions for Develop
1. Railway deploy: Dockerfile
2. sessionStorage vs in-memory — default to sessionStorage, revisit if security concern
3. Light theme — palette and visual direction from design prototype (Google Stitch)

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

### Phase 1: Internal Review

**Date:** 2026-02-27
**Mechanism:** Manual (Ralph Loop unavailable — system crash)
**Cycle:** 1
**Issues Found:** 0 Critical, 3 High, 2 Low
**Actions Taken:**
- Auto-fixed (5 issues): All High and Low issues resolved in this cycle
**Outcome:** All Critical and High issues resolved. Proceeding to Cycle 2.

### Cycle 2

**Date:** 2026-02-27
**Issues Found:** 0 Critical, 0 High, 0 Low
**Actions Taken:**
- Added file extraction UX to Develop Handoff Key Decisions (Low — convenience)
**Outcome:** Exit criteria met. Ready for Phase 2 (external review).

### Phase 2: External Review

**Date:** 2026-02-27
**Reviewers:** GPT (gpt-5.2) — Kimi timed out, Gemini rate-limited, gpt-pro non-chat model
**Issues Found:** 2 High, 3 Medium
**Actions Taken:**
- Auto-fixed (5 issues): All High and Medium issues resolved
**Cross-Reviewer Note:** Single reviewer only (infrastructure limitations) — GPT flagged base64 payload limits and input size constraint as top concerns, both confirmed as real implementation risks
**Outcome:** 0 open Critical or High issues. Design ready for Develop handoff.

## Revision History

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-02-27 | Initial draft from Design intake |
| 0.2 | 2026-02-27 | Internal review — clarified provider/auto flow, specified file extraction timing, pinned recommended_provider null handling; 3 High + 2 Low issues resolved |
| 0.3 | 2026-02-27 | External review (GPT) — added base64 size constraint + timeout spec, capped input at 50k chars, hardened security spec (exception redaction, server-side /extract validation); 2 High + 3 Medium resolved |
