# Diagram Forge Plugin

Claude Code plugin for AI-powered architecture diagram generation.

## MCP Server
This plugin bundles the `diagram-forge` MCP server which provides tools for generating enterprise-grade architecture diagrams via AI image providers (Gemini, OpenAI).

## Commands (user-facing slash commands)
- `/diagram-create "prompt"` — Generate a diagram from a prompt (just runs, no questions)
- `/iterate` — Refine an existing diagram
- `/usage` — View generation costs and usage stats
- `/templates` — List available diagram templates

## MCP Tools (for agents — use these directly, NOT slash commands)
- `mcp__diagram-forge__generate_diagram` — Generate a diagram from a prompt
- `mcp__diagram-forge__edit_diagram` — Edit an existing diagram
- `mcp__diagram-forge__list_templates` — List available templates
- `mcp__diagram-forge__list_providers` — Check provider availability
- `mcp__diagram-forge__list_styles` — List style references

## Agents
- `diagram-context-gatherer` — Explores projects to understand architecture for diagram generation

## Skills
- `diagram-intelligence` — Auto-triggers on diagram generation requests

## Setup
Requires at least one provider API key:
- `GEMINI_API_KEY` — For Google Gemini image generation
- `OPENAI_API_KEY` — For OpenAI GPT Image / DALL-E

The diagram-forge Python package must be installed: `pip install diagram-forge`
