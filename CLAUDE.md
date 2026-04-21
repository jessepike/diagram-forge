# Diagram Forge — MCP Server

## Project Overview
Standalone MCP server for generating enterprise-grade architecture diagrams via AI image providers (Google Gemini, OpenAI GPT Image). Pip-installable, cross-client compatible (Claude Code, Claude Desktop, Codex CLI, Gemini CLI).

## Architecture
- **Framework:** FastMCP (mcp>=1.0.0) with stdio transport
- **Layout:** src/diagram_forge/ — standard src layout
- **Providers:** Swappable via BaseImageProvider ABC (providers/)
- **Templates:** YAML-based prompt templates (templates/)
- **Styles:** Reference image management (styles/)
- **Cost tracking:** SQLite-backed usage/cost database
- **Config:** YAML + env vars + Pydantic validation

## Conventions
- Python 3.11+, Pydantic v2 with ConfigDict
- Async throughout (provider calls, MCP tools)
- Type hints on all public APIs
- Tests in tests/ with pytest-asyncio
- Ruff for linting, mypy for type checking

## Key Files
- `src/diagram_forge/server.py` — FastMCP tool registration (entry point)
- `src/diagram_forge/models.py` — All Pydantic models
- `src/diagram_forge/config.py` — Config loading + validation
- `src/diagram_forge/providers/base.py` — Provider ABC
- `config/default_config.yaml` — Default configuration
- `config/pricing.yaml` — Provider pricing rates

## Claude Code Plugin
The `diagram-forge-plugin/` directory contains a Claude Code plugin with:
- Commands: `/diagram:create`, `/diagram:iterate`, `/diagram:usage`, `/diagram:templates`
- Agent: `context-gatherer` — explores project architecture
- Skill: `diagram-intelligence` — auto-triggers on diagram requests

## Style System

Styles live in two places:
- **Bundled:** `src/diagram_forge/styles/<name>/` — checked into repo
- **User:** `~/.diagram-forge/styles/<name>/` — personal styles, not in repo

Each style dir needs: `reference.png` (visual reference) + `style.yaml` (name, display_name, description, tags).

The `description` field is injected as text into every prompt when the style is used by name. The `reference.png` is passed visually via `images.edit` for OpenAI or as image input for Gemini.

### agent-capabilities-card (user style)
Canonical style for Pike Agents / Krypton capability cards. White background, green (#3ECF74) accent bars, three-column layout, monospace command badges, PEER HANDOFFS, SOURCE OF TRUTH footer.

Invocation:
```python
generate_diagram(
    style_reference="agent-capabilities-card",
    provider="openai",
    model="gpt-image-2-2026-04-21",
    temperature=0.3   # lower = more consistent layout
)
```

### GPT style transfer mechanics
- `images.generate` is text-only — cannot receive image input
- `images.edit` accepts image input as visual context
- When `style_reference` is a file path, `openai_provider.generate()` routes to `edit()` automatically
- Named styles use both: text description in prompt + image via edit routing
- `edit_diagram` MCP tool only supports `dall-e-2` — use `generate_diagram` with `style_reference` instead

## Commands
```bash
# Run server
python -m diagram_forge.server

# Run tests
python -m pytest tests/ -v --cov=diagram_forge

# Lint
ruff check src/ tests/

# Type check
mypy src/
```
