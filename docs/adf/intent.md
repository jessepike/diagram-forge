# Intent — Diagram Forge Web UI

## Problem

Diagram Forge's capabilities are locked behind MCP clients (Claude Code, Claude Desktop, Codex CLI). The people who most need professional diagrams — PMs, designers, executives, clients — can't use it. You have to know what an MCP server is just to get started.

## Outcome

A web application that lets anyone generate enterprise-grade architecture diagrams by selecting a template, providing their content, and clicking generate. No CLI. No MCP client. No configuration beyond an API key.

## Why It Matters

Diagram generation is genuinely hard to do well. Diagram Forge solves that with 13 battle-tested templates and AI image generation — but it's invisible to 95% of potential users. A web UI changes the audience from "technical Claude Code users" to "anyone with a browser and a Gemini or OpenAI key."

This is also the first validation step for a potential hosted/commercial product. If non-technical users adopt it and ask to pay, the demand signal is real.

## Constraints

- Prototype first — validate before investing in production infrastructure
- BYOK (bring your own key) — no backend API cost risk in v1
- Reuse existing diagram-forge Python code — no rewrite of core logic
- Anonymous — no auth complexity in v1
- Deploy on Vercel (frontend) + Railway (Python API)
