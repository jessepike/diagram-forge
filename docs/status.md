# Diagram Forge — Status

## Current State: Web UI — Design Stage
- ADF Stage: O&I (MCP server); **Design** (Web UI)
- Monorepo: MCP server + Claude Code plugin in single repo
- All 52 tests passing
- GitHub repo: https://github.com/jessepike/diagram-forge
- Templates: 13 (up from 9) — added product_roadmap, workstreams, kanban, brand_infographic

## Discover Stage — Complete (2026-02-27)

**Produced:**
- `docs/adf/intent.md` — North Star: open diagram-forge to non-MCP users via web UI
- `docs/adf/discover-brief.md` — v0.3, passed internal (2 cycles) + external review (GPT + Kimi)

**Key decisions locked:**
- BYOK API keys (Gemini/OpenAI), passed per-request, never persisted
- Next.js (Vercel) + FastAPI (Railway) — reuse existing Python code
- Anonymous v1, no auth, no persistence
- PNG output, 10MB file upload limit

**Read order for Design:** `intent.md` → `discover-brief.md` → this file

## What's Done
- [x] Project structure (src layout, pyproject.toml, MIT license)
- [x] Pydantic v2 models — 14 models/enums (models.py)
- [x] Config system — YAML + env vars + validation (config.py)
- [x] Provider abstraction — BaseImageProvider ABC (base.py)
- [x] Gemini provider (google-genai SDK)
- [x] OpenAI provider (openai SDK, GPT Image)
- [x] Replicate provider (replicate SDK, Flux)
- [x] Template engine + 7 YAML templates
- [x] Style manager for reference images
- [x] SQLite cost tracker with reporting
- [x] FastMCP server with 7 MCP tools
- [x] Full test suite — 52 tests across 7 files
- [x] Claude Code plugin — commands, context-gatherer agent, skill
- [x] ADF docs (intent.md, design.md)
- [x] README with badges, architecture section, plugin docs
- [x] .gitignore
- [x] Initial git + GitHub push

## Session Log
- 2026-02-27: Committed 4 new templates (B17, B18), updated README to 13 templates, started Web UI Discover planning
- 2026-02-27: Completed Web UI Discover exploration + internal review (2 cycles, 0 open Critical/High issues)
- 2026-02-27: Design review complete — internal (2 cycles) + external (GPT); design.md v0.3, 0 open Critical/High
- 2026-02-28: Recovered from crash; ran design review; fixed Dockerfile/light theme; Vercel plugin installed; Stitch prototypes reviewed

## Next Steps
- [ ] Incorporate Stitch visual direction into design.md (palette, component patterns from main dashboard + settings)
- [ ] Correct generated-result screen (no sidebar nav, no projects/history/PRO — just diagram + Regenerate + Download)
- [ ] Web UI — Develop stage: build web/ monorepo (FastAPI skeleton → Next.js scaffold → wire → deploy)
- [ ] B1: Restore recommended_provider/model fields to new templates
- [ ] B2: Test remaining templates (architecture, component, sequence, integration, infographic)
- [ ] B13: Publish to PyPI (`pip install diagram-forge`)
- [ ] B15: Prompt preview / dry-run mode
