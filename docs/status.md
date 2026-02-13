# Diagram Forge — Status

## Current State: MVP Complete — Initial Release
- ADF Stage: Deliver
- Monorepo: MCP server + Claude Code plugin in single repo
- All 52 tests passing
- GitHub repo: https://github.com/jessepike/diagram-forge

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

## Next Steps
- [ ] Model and key management system — user-level config (`~/.diagram-forge/config.yaml`) that overrides defaults for provider models and API keys without editing source. Current pain: model names are hardcoded in 3 places, keys require shell env vars, no per-project override support.
- [ ] Generate sample diagram images for README
- [ ] Add bundled style reference image (enterprise-togaf/reference.png)
- [ ] Publish to PyPI (`pip install diagram-forge`)
- [ ] End-to-end test with live providers
- [ ] Test cross-client (Claude Desktop, Codex CLI)
- [ ] Community announcement
