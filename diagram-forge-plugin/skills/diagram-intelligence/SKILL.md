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

When triggered, generate the diagram immediately. Do not present a menu of options or ask what type of diagram — infer it from the user's request and go.

## MCP Tools

Call these directly:
- `mcp__diagram-forge__generate_diagram` — Generate a diagram from a prompt
- `mcp__diagram-forge__edit_diagram` — Edit an existing diagram
- `mcp__diagram-forge__list_templates` — List available templates
- `mcp__diagram-forge__list_providers` — Check provider availability
- `mcp__diagram-forge__list_styles` — List style references

## Behavior

1. **Infer diagram type** from the request. Default to `architecture`. Map keywords:
   - "data flow", "pipeline", "ETL" → `data_flow`
   - "sequence", "timeline" → `sequence`
   - "components", "modules" → `component`
   - "integration", "APIs" → `integration`
   - "infographic", "summary" → `infographic`
   - Everything else → `architecture`

2. **Build a detailed prompt** from the user's description. Enhance it with:
   - "All text crystal clear and perfectly legible"
   - "Professional, publication-ready"
   - Explicit layout structure (layers, columns, flow direction)
   - Named components with relationships

3. **Call `mcp__diagram-forge__generate_diagram`** with:
   - `prompt`: the enhanced prompt
   - `diagram_type`: inferred type
   - `resolution`: "2K"
   - `aspect_ratio`: "16:9"

4. **Show result**: output path and cost. Offer `/iterate` for refinements.

## Do NOT
- Present a menu asking what kind of diagram to create
- Ask the user to pick a template or provider
- Ask for confirmation before generating
- Say "what do you want to visualize?"

If the user said "create a diagram of X", you already know what X is. Generate it.

## Prompt Engineering Tips

- Be explicit about layout (top-to-bottom layers, left-to-right flow)
- Name every element — don't say "show inputs", list each input by name
- Specify color coding rules — colors should encode meaning
- For architecture diagrams, organize into named layers
- Include a legend for any color coding used
