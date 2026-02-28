# Diagram Forge — Status

## Current State: Web UI — Develop Stage
- ADF Stage: O&I (MCP server); **Develop** (Web UI)
- Monorepo: MCP server + Claude Code plugin + `web/` (to be built)
- All 52 tests passing
- GitHub repo: https://github.com/jessepike/diagram-forge
- Templates: 13 — architecture, c4_container, component, data_flow, sequence, integration, exec_infographic, brand_infographic, product_roadmap, workstreams, kanban + 2 more

## Design Stage — Complete (2026-02-28)

### What Was Produced
- `docs/adf/design.md` — v0.3, status: review-complete
- `docs/BACKLOG.md` — 7 Web UI items (WUI-01–07) + 4 MCP server items (B01, B02, B13, B15)
- Stitch design prototypes — main dashboard, settings panel, generated result (reference in `docs/diagram_forge_*/`)

### Key Decisions Locked
- Monorepo `web/` subdir — `web/frontend/` (Next.js) + `web/api/` (FastAPI)
- Next.js API routes as proxy — shared secret server-side only, never in browser
- BYOK — user's API key passed per-request, in-memory only, never logged; exception handlers redact `api_key`
- base64 PNG response — 3MB cap (Vercel 4.5MB limit with 33% base64 inflation); 60s Vercel / 120s Railway timeout
- 50,000 char input cap — enforced client + server (HTTP 400)
- Provider "auto" resolved by frontend — backend always receives explicit `"gemini"` or `"openai"`
- File extraction on selection — `/extract` called immediately, populates textarea, switches to Paste tab
- Server-side `/extract` validation — MIME check + 422 on parse failure
- Railway: Dockerfile (not nixpacks)
- Theme: light — palette from Stitch prototype
- sessionStorage for API key — cleared on tab close

### What Was Archived
- `docs/_archive/2026-02-11-mcp-server-design.md` — MCP server design (O&I era)
- `docs/_archive/2026-02-12-mcp-server-design-architecture.md` — MCP server architecture detail

### Known Limitations / Trade-offs
- No rate limiting in v1 — Railway resource limits as soft cap; acceptable for prototype
- Single external reviewer (GPT only — Kimi timed out, Gemini rate-limited) for design review
- Stitch generated-result screen doesn't match spec (shows sidebar nav / PRO upsell) — disregard that screen, use main dashboard + settings panel only as visual reference

### Read Order for Develop
1. `docs/adf/intent.md` — North Star
2. `docs/adf/discover-brief.md` — Scope and success criteria
3. `docs/adf/design.md` — Architecture and all decisions
4. `docs/BACKLOG.md` — Work items (start WUI-01)
5. `docs/status.md` — This file

## Discover Stage — Complete (2026-02-27)

**Produced:**
- `docs/adf/intent.md` — North Star: open diagram-forge to non-MCP users via web UI
- `docs/adf/discover-brief.md` — v0.3, passed internal (2 cycles) + external review (GPT + Kimi)

**Key decisions locked:**
- BYOK API keys (Gemini/OpenAI), passed per-request, never persisted
- Next.js (Vercel) + FastAPI (Railway) — reuse existing Python code
- Anonymous v1, no auth, no persistence
- PNG output, 10MB file upload limit

## What's Done (MCP Server — O&I)
- [x] Project structure (src layout, pyproject.toml, MIT license)
- [x] Pydantic v2 models — 14 models/enums (models.py)
- [x] Config system — YAML + env vars + validation (config.py)
- [x] Provider abstraction — BaseImageProvider ABC (base.py)
- [x] Gemini provider (google-genai SDK)
- [x] OpenAI provider (openai SDK, GPT Image)
- [x] Replicate provider (replicate SDK, Flux)
- [x] Template engine + 13 YAML templates
- [x] Style manager for reference images
- [x] SQLite cost tracker with reporting
- [x] FastMCP server with 7 MCP tools
- [x] Full test suite — 52 tests across 7 files
- [x] Claude Code plugin — commands, context-gatherer agent, skill
- [x] README with badges, architecture section, plugin docs

## Session Log
- 2026-02-27: Committed 4 new templates (B17, B18), updated README to 13 templates, started Web UI Discover planning
- 2026-02-27: Completed Web UI Discover exploration + internal review (2 cycles, 0 open Critical/High issues)
- 2026-02-27: Design review complete — internal (2 cycles) + external (GPT); design.md v0.3, 0 open Critical/High
- 2026-02-28: Recovered from crash; ran design review; fixed Dockerfile/light theme; Vercel plugin installed; Stitch prototypes reviewed
- 2026-02-28: Design stage closed — BACKLOG.md created, artifacts archived, transitioned to Develop

## Next Steps
- [ ] WUI-01: FastAPI skeleton — web/api/ (/health, /templates, /generate mock, /extract)
- [ ] WUI-02: Next.js scaffold — layout, panels, Settings component
- [ ] WUI-03: Wire generate end-to-end
- [ ] WUI-04: File upload + /extract
- [ ] WUI-05: Error/loading states + polish
- [ ] WUI-06: Deploy (Railway Dockerfile → Vercel)
- [ ] WUI-07: Visual polish from Stitch
