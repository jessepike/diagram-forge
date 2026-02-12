# Diagram Forge — Design (ADF Design)

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  MCP Clients                     │
│  (Claude Code, Claude Desktop, Codex, Gemini)   │
└────────────────────┬────────────────────────────┘
                     │ stdio
┌────────────────────┴────────────────────────────┐
│              FastMCP Server (server.py)          │
│  ┌──────────┐ ┌───────────┐ ┌────────────────┐  │
│  │ 7 Tools  │ │ Serialize │ │  Error Handler │  │
│  └────┬─────┘ └───────────┘ └────────────────┘  │
│       │                                          │
│  ┌────┴──────────────────────────────────────┐   │
│  │           Template Engine                  │   │
│  │  (YAML templates + prompt rendering)       │   │
│  └────┬──────────────────────────────────────┘   │
│       │                                          │
│  ┌────┴──────────────────────────────────────┐   │
│  │         Provider Abstraction               │   │
│  │  ┌────────┐ ┌────────┐ ┌───────────┐      │   │
│  │  │ Gemini │ │ OpenAI │ │ Replicate │      │   │
│  │  └────────┘ └────────┘ └───────────┘      │   │
│  └───────────────────────────────────────────┘   │
│       │                                          │
│  ┌────┴─────────┐  ┌──────────────┐              │
│  │ Cost Tracker │  │ Style Manager│              │
│  │  (SQLite)    │  │  (images)    │              │
│  └──────────────┘  └──────────────┘              │
└──────────────────────────────────────────────────┘
```

## MCP Tool API

### generate_diagram
- **Input**: prompt, diagram_type, provider, resolution, aspect_ratio, style_reference, output_path, temperature
- **Flow**: Load template → Render prompt → Resolve provider → Generate → Save image → Track cost
- **Output**: {status, output_path, cost_usd, generation_time_ms, model_used}

### edit_diagram
- **Input**: image_path, prompt, provider, resolution, reference_images, output_path
- **Flow**: Load image → Resolve provider → Check edit support → Edit → Save → Track cost
- **Output**: {status, output_path, cost_usd, generation_time_ms}

### list_templates / list_providers / list_styles
- **Flow**: Read from filesystem/config → Format → Return
- **Output**: {status, items[], count}

### get_usage_report
- **Input**: days, group_by
- **Flow**: Query SQLite → Aggregate → Format
- **Output**: {status, total_generations, total_cost_usd, breakdown[]}

### configure_provider
- **Input**: provider, api_key
- **Flow**: Set env var → Health check → Return status
- **Output**: {status, message, health}

## Data Models (Pydantic v2)

See `src/diagram_forge/models.py` for full definitions. Key models:
- `GenerationConfig` — Input config for provider calls
- `GenerationResult` — Output from provider calls (dataclass)
- `DiagramTemplate` — Loaded YAML template
- `AppConfig` — Top-level configuration
- `GenerationRecord` — Cost tracking record
- `UsageReport` — Aggregated usage data

## Provider Interface

All providers implement `BaseImageProvider` ABC:
- `generate(config) -> GenerationResult`
- `edit(input_image, config) -> GenerationResult`
- `health_check() -> ProviderHealth`
- `get_pricing() -> PricingInfo`
- `supported_features() -> set[str]`

## Template System

YAML templates define:
- Prompt template with `{variable}` placeholders
- Style defaults (background, font, borders)
- Color system with semantic palette
- Required/optional variables with descriptions

Templates are loaded from `src/diagram_forge/templates/` and rendered via `template_engine.py`.

## Test Strategy

- **Unit tests**: All components in isolation with mock providers
- **Integration tests**: Server creation, template loading, cost tracking
- **No live API tests in CI**: Provider tests use mocks
- **Coverage target**: >80% on non-provider code
