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

## Rendering Quality — Observed from Production Use

Source: EvenGround master backlog kanban (37 cards, 6 categories, 3 generations + 2 edits, 2026-03-01)
Golden example: `~/.diagram-forge/styles/minimal-kanban/examples/master-backlog-kanban.md`

| ID | Item | Priority | Status | Notes |
|---|---|---|---|---|
| RQ-01 | **Duplicate card rendering on large boards** — Gemini duplicates cards when kanban has 15+ total cards. Template has "EXACTLY ONCE" instruction but model ignores at scale. | P1 | Pending | Observed: P1-06 duplicated in Done column on first gen. Fix: add explicit per-column count enforcement + total count verification in prompt |
| RQ-02 | **Edit drift — fixing one card introduces new duplicates** — edit_diagram re-renders everything, whack-a-mole effect. Fixing P1-06 dupe caused FIX-2 dupe. Required 2 edit passes. | P1 | Pending | Fix: include full card manifest in edit prompt; add "DO NOT modify unspecified cards" instruction |
| RQ-03 | **Structured card data instead of free-text blocks** — template variables accept free text, losing structure. Callers manually format each card. | P2 | Pending | Proposed: accept JSON/YAML card arrays, template engine renders deterministically with guaranteed no dupes and correct counts |
| RQ-04 | **Golden example prompts per template** — ship example prompts alongside templates so callers know optimal input format. | P2 | In Progress | Done: kanban (`minimal-kanban/examples/`). TODO: architecture, c4, data_flow, workstreams, roadmap, exec_infographic, sequence, component, integration |
| RQ-05 | **Post-generation vision validation** — optional validation step using vision model to count elements, detect dupes, verify legend, check legibility. Return validation report alongside image. | P2 | Pending | Opt-in via `validate: true` parameter |
| RQ-06 | **Template-level card count enforcement** — auto-count from input and inject: "TO DO must have EXACTLY 19 cards, no more, no less. TOTAL: 35 unique cards." Lightweight version of RQ-05. | P2 | Pending | Pure prompt engineering, no vision model needed |
