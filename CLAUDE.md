# Diagram Forge — MCP Server

## Project Overview
Standalone MCP server for generating enterprise-grade architecture diagrams via AI image providers (Google Gemini, OpenAI GPT Image, Replicate Flux). Pip-installable, cross-client compatible (Claude Code, Claude Desktop, Codex CLI, Gemini CLI).

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
