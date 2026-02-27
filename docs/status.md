# Diagram Forge — Status

## Current State: Operate & Improve — Web UI Planning Started
- ADF Stage: O&I (MCP server); Discover (Web UI — not yet started)
- Monorepo: MCP server + Claude Code plugin in single repo
- All 52 tests passing
- GitHub repo: https://github.com/jessepike/diagram-forge
- Templates: 13 (up from 9) — added product_roadmap, workstreams, kanban, brand_infographic

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

## Next Steps
- [ ] Web UI — start Discover stage (brief + intent docs)
- [ ] B1: Restore recommended_provider/model fields to new templates
- [ ] B2: Test remaining templates (architecture, component, sequence, integration, infographic)
- [ ] B13: Publish to PyPI (`pip install diagram-forge`)
- [ ] B15: Prompt preview / dry-run mode
