# Setup and Customization Guide

This guide covers day-1 setup plus the most common changes maintainers and evaluators make:
- API key setup
- provider/model defaults
- template editing
- prompt strategy updates
- style references

## 1) Install and start

```bash
pip install diagram-forge
```

Or from source:

```bash
git clone https://github.com/jessepike/diagram-forge.git
cd diagram-forge
pip install -e ".[dev]"
```

Run the server:

```bash
python -m diagram_forge.server
```

## 2) Set API keys

Set at least one provider key before starting your MCP client:

```bash
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export REPLICATE_API_TOKEN="your-key"
```

Security note:
- `configure_provider` is disabled by default.
- Preferred approach is environment variables at process start.
- If you intentionally want session-time key setup, enable it:

```bash
export DIAGRAM_FORGE_ENABLE_CONFIGURE_PROVIDER=1
```

## 3) Choose default provider/model

Defaults come from `config/default_config.yaml`.

Copy and customize:

```bash
cp config/default_config.yaml ~/.diagram-forge/custom_config.yaml
```

Set your config path:

```bash
export DIAGRAM_FORGE_CONFIG=~/.diagram-forge/custom_config.yaml
```

Example:

```yaml
version: 1
default_provider: gemini
output_directory: ~/.diagram-forge/output
styles_directory: ~/.diagram-forge/styles
database_path: ~/.diagram-forge/usage.db

providers:
  gemini:
    enabled: true
    model: gemini-2.5-flash-image
    api_key_env: GEMINI_API_KEY
  openai:
    enabled: true
    model: gpt-image-1.5
    api_key_env: OPENAI_API_KEY
  replicate:
    enabled: false
    model: black-forest-labs/flux-schnell
    api_key_env: REPLICATE_API_TOKEN
```

## 4) Tool-level model override

Per request, you can override model in `generate_diagram`:

```text
generate_diagram(prompt="...", provider="openai", model="gpt-image-1.5")
```

If `provider="auto"`, Diagram Forge uses template recommendations.

## 5) Modify templates

Templates live in:
- `src/diagram_forge/templates/*.yaml`

Each template supports:
- metadata: `name`, `display_name`, `description`
- routing hints: `recommended_provider`, `recommended_model`
- visual defaults: `style_defaults`, optional `color_system`
- prompt body: `prompt_template`
- variables map: `variables`

Recommended workflow:
1. Duplicate an existing template as a starting point.
2. Keep legibility constraints explicit (text size, contrast, spacing).
3. Preserve semantic color mapping for consistent outputs.
4. Update `recommended_provider`/`recommended_model` if you benchmarked alternatives.
5. Validate with at least 3-5 real prompts.

## 6) Prompt strategy changes

Prompt rendering happens in `src/diagram_forge/template_engine.py`.

Common changes:
- add/remove style defaults block content
- change legend generation behavior
- tune fallback prompt for unknown types

Before merging prompt changes:
- run `pytest -q`
- run a benchmark subset from `evals/benchmark_v1.yaml`
- visually review label clarity at 100% zoom

## 7) Add custom style references

Create a style folder under:

- `~/.diagram-forge/styles/<style-name>/reference.png`

Optional metadata file:

- `~/.diagram-forge/styles/<style-name>/style.yaml`

Example `style.yaml`:

```yaml
name: clean-enterprise
display_name: Clean Enterprise
description: High-legibility architecture look for docs and decks
tags:
  - architecture
  - enterprise
  - high-contrast
```

Use it:

```text
generate_diagram(prompt="...", style_reference="clean-enterprise")
```

## 8) Security boundaries (important)

- Output writes are limited to configured output directory.
- Input image reads are limited to current workspace, output dir, and styles dir.
- Input/output file types are image-only (`.png`, `.jpg`, `.jpeg`, `.webp`).
- Replicate output downloads are restricted to validated HTTPS hosts and size limits.

## 9) Release-quality local checks

```bash
pytest -q
ruff check src tests
mypy src
python -m build
```
