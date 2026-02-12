# Diagram Forge

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)

**Turn natural language into enterprise-grade architecture diagrams.** Diagram Forge is an MCP server that combines template-driven prompt engineering with swappable AI image providers to generate professional diagrams from any MCP-compatible client.

Instead of wrestling with diagramming tools or manually crafting image generation prompts, describe your system in plain English and let Diagram Forge handle the rest — template selection, prompt engineering, style application, and cost tracking.

![Example: Enterprise architecture diagram generated with Diagram Forge](docs/examples/sample-architecture.png)

## Features

- **7 diagram templates** — Architecture (TOGAF), data flow, component, sequence, integration, infographic, and generic
- **3 image providers** — Google Gemini, OpenAI (GPT Image), Replicate (Flux)
- **Template-driven prompts** — YAML templates with style defaults, color systems, and variable substitution
- **Style references** — Apply consistent visual styles with reference images
- **Cost tracking** — SQLite-backed usage and cost reporting
- **Cross-client** — Works with Claude Code, Claude Desktop, Codex CLI, Gemini CLI via stdio transport

## Quick Start

### 1. Install

```bash
pip install diagram-forge
```

Or from source:

```bash
git clone https://github.com/jessepike/diagram-forge.git
cd diagram-forge
pip install -e ".[dev]"
```

### 2. Configure a provider

Set at least one API key:

```bash
export GEMINI_API_KEY="your-key"       # Google Gemini (recommended)
export OPENAI_API_KEY="your-key"       # OpenAI GPT Image
export REPLICATE_API_TOKEN="your-key"  # Replicate Flux
```

### 3. Add to your MCP client

**Claude Code** (`.mcp.json` in your project):
```json
{
  "diagram-forge": {
    "command": "python",
    "args": ["-m", "diagram_forge.server"]
  }
}
```

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "diagram-forge": {
      "command": "python",
      "args": ["-m", "diagram_forge.server"]
    }
  }
}
```

**Codex CLI / Gemini CLI** — same `.mcp.json` format as Claude Code.

### 4. Generate a diagram

Ask your AI client naturally:

> "Generate an architecture diagram of a three-tier web app with a React frontend, Node.js API layer, and PostgreSQL database"

Or be more specific:

> "Create a TOGAF-style architecture diagram showing our microservices. Use the architecture template, Gemini provider, 16:9 aspect ratio."

## MCP Tools

| Tool | Description |
|------|-------------|
| `generate_diagram` | Generate a diagram from a text prompt with template and style support |
| `edit_diagram` | Edit an existing diagram with natural language instructions |
| `list_templates` | List available diagram templates and their variables |
| `list_providers` | Show configured providers, API key status, and supported features |
| `list_styles` | List available style reference images |
| `get_usage_report` | View generation costs and usage stats by provider, type, or day |
| `configure_provider` | Set up an API key for a provider (session-only) |

## Diagram Types

| Type | Template | Best For |
|------|----------|----------|
| `architecture` | Enterprise Architecture (TOGAF) | System architecture, layered designs |
| `data_flow` | Data Flow Diagram | ETL pipelines, data movement |
| `component` | Component Detail View | Service internals, module structure |
| `sequence` | Sequence Diagram | Request flows, protocol interactions |
| `integration` | Integration Map | System connections, API landscape |
| `infographic` | Infographic / Learning Card | Concept explanations, overviews |
| `generic` | Custom / Freeform | Anything else |

## Claude Code Plugin

This repo includes a Claude Code plugin in `diagram-forge-plugin/` that adds a guided UX layer on top of the MCP server:

- `/diagram:create` — Guided diagram creation with context gathering
- `/diagram:iterate` — Refine an existing diagram
- `/diagram:usage` — View cost report
- `/diagram:templates` — Browse available templates
- **Context-gatherer agent** — Automatically explores your project to understand what to diagram
- **Diagram intelligence skill** — Auto-triggers when you mention diagrams

To use, install the plugin or add the `.mcp.json` from the plugin directory.

## How It Works

1. **Template selection** — Matches your request to one of 7 YAML templates, each encoding proven prompt patterns (color systems, layer organization, legibility rules)
2. **Prompt rendering** — Merges your description with the template, substituting variables and applying style defaults
3. **Provider dispatch** — Sends the engineered prompt to your chosen provider (Gemini, OpenAI, or Replicate)
4. **Image handling** — Saves the generated image, records cost and metadata to SQLite
5. **Iteration** — Edit existing diagrams with natural language instructions via providers that support image editing

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (52 tests)
python -m pytest tests/ -v --cov=diagram_forge

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Test MCP tools interactively
npx @modelcontextprotocol/inspector python -m diagram_forge.server
```

## Architecture

```
src/diagram_forge/
  server.py              # FastMCP server — 7 tools, stdio transport
  models.py              # Pydantic v2 models
  config.py              # YAML + env var config loading
  template_engine.py     # Template loading and prompt rendering
  style_manager.py       # Style reference image management
  cost_tracker.py        # SQLite usage/cost tracking
  providers/
    base.py              # BaseImageProvider ABC
    gemini.py            # Google Gemini
    openai_provider.py   # OpenAI GPT Image
    replicate_provider.py # Replicate Flux
  templates/             # 7 YAML prompt templates
```

## License

MIT
