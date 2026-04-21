---
name: diagram-create
description: Generate a diagram. Pass a prompt describing what to visualize.
arguments:
  - name: prompt
    description: What to diagram
    required: true
---

# Diagram Create

Generate a diagram immediately from the user's prompt. Do not ask clarifying questions — just build it.

## Steps

1. **Infer diagram type** from the prompt. Default to `architecture` if unclear. Map keywords:
   - "data flow", "pipeline", "ETL" → `data_flow`
   - "sequence", "timeline", "interaction" → `sequence`
   - "components", "modules" → `component`
   - "integration", "connections", "APIs" → `integration`
   - "infographic", "summary", "overview" → `infographic`
   - Everything else → `architecture`

2. **Call `mcp__diagram-forge__generate_diagram`** with:
   - `prompt`: the user's prompt text, enhanced with "All text crystal clear and perfectly legible. Professional, publication-ready."
   - `diagram_type`: inferred from step 1
   - `resolution`: "2K"
   - `aspect_ratio`: "16:9"

3. **Show the result**: output path and a one-line cost summary. Mention `/iterate` for refinements.

Do NOT:
- Ask the user to pick a template
- Ask the user to pick a provider
- Ask for confirmation before generating
- Show the prompt before generating

Just generate it.
