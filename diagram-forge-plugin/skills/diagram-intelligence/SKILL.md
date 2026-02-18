---
name: diagram-intelligence
description: >
  Auto-triggers when the user requests diagram generation, architecture visualization,
  or system design diagrams. Detects mentions of "create a diagram", "generate architecture",
  "visualize the system", "draw a data flow", "make an infographic", or similar requests.
  Orchestrates the diagram-forge MCP tools for prompt engineering, template selection,
  style reference matching, and iterative refinement.
---

# Diagram Intelligence Skill

You have access to the **diagram-forge** MCP server with these tools:
- `generate_diagram` — Generate a new diagram from a text prompt
- `edit_diagram` — Edit an existing diagram with instructions
- `list_templates` — Show available diagram templates
- `list_providers` — Show configured providers and their status
- `list_styles` — Show available style references
- `get_usage_report` — View generation costs and usage
- `configure_provider` — Optional session-only API key setup (often disabled by default)

## When Triggered

When the user asks to create or visualize a diagram:

1. **Assess the request**: Determine the diagram type (architecture, data flow, sequence, component, integration, infographic, or generic)

2. **Check provider availability**: Call `list_providers` to see which providers are configured. If none have API keys, guide the user to set environment variables before launching the server. Only use `configure_provider` when explicitly enabled by the operator.

3. **Context gathering**: If the user wants to diagram their current project, use the Explore agent or read key files (CLAUDE.md, README, architecture docs) to understand the system.

4. **Template selection**: Match the request to the best template. Call `list_templates` for options.

5. **Prompt engineering**: Build a detailed, structured prompt that includes:
   - Clear component descriptions
   - Layer organization
   - Connection definitions
   - Color coding rules
   - Legibility and quality instructions

6. **Style matching**: If style references are available (`list_styles`), suggest matching ones.

7. **Generate**: Call `generate_diagram` with the assembled parameters.

8. **Iterate**: Offer refinement via `edit_diagram` or regeneration with adjusted prompts.

## Prompt Engineering Tips

- Be explicit about layout (top-to-bottom layers, left-to-right flow, etc.)
- Specify color coding rules clearly — colors should encode meaning
- Always include "All text crystal clear and perfectly legible"
- For architecture diagrams, organize components into named layers
- For data flow, specify swim lanes and arrow directions
- Include a legend for any color coding used
