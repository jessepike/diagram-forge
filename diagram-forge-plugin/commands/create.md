---
name: create
description: Generate an architecture diagram with guided workflow
arguments:
  - name: description
    description: What to diagram (optional — will ask if not provided)
    required: false
---

# Diagram Creation Workflow

You are orchestrating a diagram generation workflow using the diagram-forge MCP tools.

## Steps

1. **Understand the request**: If the user provided a description argument, use it. Otherwise, ask what they want to diagram.

2. **Gather context**: Use the `context-gatherer` agent (Task tool with subagent_type) to explore the current project and understand the architecture. Pass the user's description to the agent.

3. **Select template**: Call `list_templates` to show available diagram types. Based on the user's request, recommend the best template. Let the user confirm or choose differently.

4. **Determine provider**: Call `list_providers` to check which providers have API keys configured. Recommend the best available provider (prefer Gemini for architecture diagrams). Inform the user if no providers have keys set.

5. **Build the prompt**: Combine the gathered context with the user's description. Use clear, structured language that describes:
   - Components and their relationships
   - Layers/groupings
   - Connection types
   - Color coding requirements

6. **Generate**: Call `generate_diagram` with the assembled prompt, selected template type, provider, and any style reference.

7. **Present results**: Show the output path and offer to iterate with `/diagram:iterate`.

## Guidelines
- Always show the user the prompt before generating (ask for confirmation)
- Suggest style references if available (call `list_styles`)
- Default to 2K resolution, 16:9 aspect ratio for architecture diagrams
- Track costs — mention the estimated cost before generating
