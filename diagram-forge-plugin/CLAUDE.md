# Diagram Forge Plugin

Claude Code plugin for AI-powered architecture diagram generation.

## MCP Server
This plugin bundles the `diagram-forge` MCP server which provides tools for generating enterprise-grade architecture diagrams via AI image providers (Gemini, OpenAI, Replicate).

## Commands
- `/diagram:create` — Guided diagram creation workflow
- `/diagram:iterate` — Refine an existing diagram
- `/diagram:usage` — View generation costs and usage stats
- `/diagram:templates` — List available diagram templates

## Agents
- `diagram-context-gatherer` — Explores projects to understand architecture for diagram generation

## Skills
- `diagram-intelligence` — Auto-triggers on diagram generation requests

## Setup
Requires at least one provider API key:
- `GEMINI_API_KEY` — For Google Gemini image generation
- `OPENAI_API_KEY` — For OpenAI GPT Image / DALL-E
- `REPLICATE_API_TOKEN` — For Replicate Flux models

The diagram-forge Python package must be installed: `pip install diagram-forge`
