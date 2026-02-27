# Diagram Forge — Intent (ADF Discover)

## Problem Statement
Generating enterprise-grade architecture diagrams requires a repeatable workflow: gathering system context, engineering detailed prompts with templates, providing style references, and iterating on results. This workflow is manual, inconsistent, and not shareable across teams or AI clients.

## User Needs
- Generate high-quality architecture diagrams from natural language descriptions
- Use proven templates for common diagram types (TOGAF, data flow, sequence, etc.)
- Apply consistent visual styles with reference images
- Track generation costs across providers
- Work across any AI client (Claude Code, Claude Desktop, Codex, Gemini CLI)

## Solution
**diagram-forge**: A standalone MCP server that encapsulates the diagram generation workflow:
- Template-driven prompt engineering for 7 diagram types
- Template-driven prompt engineering for 9 diagram types
- Swappable provider architecture (Gemini, OpenAI, Replicate)
- Style reference image management
- SQLite-backed cost tracking and reporting
- pip-installable, cross-client via stdio transport

**diagram-forge-plugin**: Claude Code plugin providing UX layer:
- Guided creation workflow (`/diagram:create`)
- Context gathering agent that explores projects
- Auto-triggering skill for diagram requests
- Iterative refinement commands

## Technology Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.11+ | Image ecosystem, provider SDKs, MCP server consistency |
| Framework | FastMCP (mcp>=1.0.0) | Proven pattern, pythonic decorators |
| Providers | Gemini + OpenAI + Replicate | Validates swappable architecture, covers ecosystems |
| Transport | stdio | Maximum client compatibility |
| Cost tracking | SQLite | Lightweight, portable, no external deps |
| Templates | YAML | Human-editable, version-controllable |

## Success Criteria
- [ ] Generate architecture diagrams via any configured provider
- [ ] All 7 templates produce well-structured prompts
- [ ] All 9 templates produce well-structured prompts
- [ ] Cost tracking records all generations accurately
- [ ] Works in Claude Code, Claude Desktop, and Codex CLI
- [ ] Plugin commands provide smooth guided workflow
- [ ] Tests pass with >80% coverage on non-provider code

## Competitive Landscape
- **Blueprint MCP**: Diagram generation but limited to single provider
- **nano-banana-mcp**: Image generation focused, not architecture-specific
- **nano-banana-pro**: Advanced features but not template-driven

Diagram Forge differentiates through template-driven prompt engineering, multi-provider support, and cost tracking.
