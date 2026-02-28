# Diagram Forge — Backlog

## Web UI (Active — Develop Stage)

Work items for `web/` monorepo. Build in order.

| ID | Item | Priority | Status | Notes |
|---|---|---|---|---|
| WUI-01 | FastAPI skeleton — `web/api/` with `/health`, `/templates`, `/generate` (mock response), `/extract` | P0 | Pending | Dockerfile for Railway; X-API-Secret auth on all routes |
| WUI-02 | Next.js scaffold — `web/frontend/` layout, left panel, right panel, Settings component | P0 | Pending | Tailwind CSS 4, light theme; Settings as slide-out panel |
| WUI-03 | Wire generate end-to-end — real diagram-forge call, base64 response, provider resolution | P0 | Pending | Frontend resolves "auto" before API call; 3MB PNG cap; 60s timeout |
| WUI-04 | File upload + `/extract` — multipart upload, PyMuPDF (PDF) + python-docx (DOCX), extract-on-select flow | P0 | Pending | On file selection → call /extract → populate textarea → switch to Paste tab |
| WUI-05 | Error states, loading states, polish — all 4 states (initial/generating/success/error), char counter, provider badges | P1 | Pending | 50k char limit enforced client + server; skeleton during generation |
| WUI-06 | Deploy — Railway (Dockerfile) + Vercel; env vars; CORS locked to Vercel URL | P1 | Pending | `RAILWAY_API_SECRET` on both; `RAILWAY_API_URL` on Vercel |
| WUI-07 | Visual polish — apply Stitch palette and component patterns | P2 | Pending | Reference: `docs/diagram_forge_main_dashboard/`, `docs/diagram_forge_settings_panel/` |

## MCP Server Backlog

| ID | Item | Priority | Status | Notes |
|---|---|---|---|---|
| B01 | Restore `recommended_provider` / `model` fields to new templates (product_roadmap, workstreams, kanban, brand_infographic) | P1 | Pending | Added in B17/B18 without these fields |
| B02 | Test remaining templates — architecture, component, sequence, integration, infographic | P1 | Pending | Visual QA pass |
| B13 | Publish to PyPI — `pip install diagram-forge` | P2 | Pending | Requires pyproject.toml version + twine setup |
| B15 | Prompt preview / dry-run mode — show rendered prompt without generating | P2 | Pending | Useful for debugging templates |
