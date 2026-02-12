---
name: iterate
description: Refine an existing diagram with edit instructions
arguments:
  - name: image_path
    description: Path to the diagram to edit
    required: true
  - name: instructions
    description: What to change in the diagram
    required: false
---

# Diagram Iteration Workflow

You are helping the user refine an existing diagram using the diagram-forge `edit_diagram` MCP tool.

## Steps

1. **Verify the image**: Confirm the provided image_path exists using the Read tool (it can read images).

2. **Gather edit instructions**: If the user provided instructions, use them. Otherwise, ask what they want to change. Common edits include:
   - Add/remove components
   - Change layout or grouping
   - Update labels or text
   - Adjust colors or styling
   - Add connections or data flows
   - Improve legibility

3. **Select provider**: Use the same provider that generated the original diagram if known. Gemini and OpenAI support editing; Replicate has limited edit support.

4. **Execute edit**: Call `edit_diagram` with the image path, edit instructions, and provider.

5. **Present results**: Show the new output path. Offer to iterate further or compare with the original.

## Guidelines
- Show the edit prompt before executing
- Mention that edits may not be pixel-perfect — sometimes regenerating with an updated prompt works better
- If multiple rounds of editing degrade quality, suggest regenerating from scratch with a refined prompt
