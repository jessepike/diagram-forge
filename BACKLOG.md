# Diagram Forge Backlog

## Active

### B1: Restore recommended_provider/model fields
- **Priority:** P1
- **Status:** In progress — fields added to models.py and server.py, stripped from YAMLs pending MCP restart
- **Details:** Re-add `recommended_provider` and `recommended_model` to all template YAMLs after MCP server restart validates the new Pydantic model fields
- **Templates:** all 9

### B2: Test remaining templates
- **Priority:** P1
- **Status:** Pending
- **Details:** Templates not yet tested with real generation:
  - `architecture` (TOGAF) — with ArchiMate convention colors
  - `component` — internal structure + boundaries
  - `sequence` — UML sequence interactions
  - `integration` — system connection map
  - `infographic` — learning card / concept explainer
- **Goal:** Generate on both Gemini 3 Pro and GPT 1.5, compare, flag baselines

### B3: Add OpenAI quality/style params
- **Priority:** P2
- **Status:** Pending
- **Details:** OpenAI API supports `quality="hd"` and `style="natural"` params not currently passed in `openai_provider.py`. `natural` may improve technical diagram output. `hd` may improve text legibility.
- **Acceptance:** Both params exposed as optional in generate_diagram, passed through to OpenAI API

### B4: Temperature tuning benchmarks
- **Priority:** P2
- **Status:** Pending
- **Details:** Test Gemini at temperature 0.3, 0.5, 0.7, 1.0 on the same prompt to understand effect on layout consistency. Low temp (0.4) showed slightly cleaner results in initial test.

### B5: Style reference library expansion
- **Priority:** P2
- **Status:** 3 baselines saved (c4-container, exec-infographic, data-flow)
- **Details:** Save best outputs as style references for remaining templates. Test style_reference impact on Gemini output consistency. Document how users save their own styles.

### B6: Update README with new templates and features
- **Priority:** P1
- **Status:** Complete
- **Details:** README updated: 7→9 templates, style references, auto provider selection, architecture section. Claude Code plugin section added.

### B7: Add BPMN/workflow template
- **Priority:** P3
- **Status:** Pending
- **Details:** Swimlane-based workflow diagram template. Research showed no official BPMN color standard — use accessibility-friendly palette. Low priority until current templates are polished.

### B8: Provider-specific prompt tuning
- **Priority:** P3
- **Status:** Pending
- **Details:** GPT needs more explicit spatial directives than Gemini. Consider adding provider-specific prompt addons to templates (e.g., extra size/spacing instructions when provider=openai). Could be a `provider_hints` section in YAML.

### B9: Edit workflow improvements
- **Priority:** P3
- **Status:** Pending
- **Details:** Current edit_diagram requires manual image path. Consider: auto-suggest last generated image, pass edit instructions more naturally, support "regenerate with tweaks" without full re-prompt.

### B10: Accessibility color audit
- **Priority:** P3
- **Status:** Research complete (Paul Tol, IBM, Wong palettes documented)
- **Details:** Audit all template color palettes against WCAG 2.1 AA contrast requirements. Add an accessibility-first color preset option. Test with colorblind simulators.

### B11: C4 Context (Level 1) template
- **Priority:** P2
- **Status:** Pending
- **Details:** Current C4 template is Level 2 (Container). Add Level 1 Context diagram — fewer elements, bigger boxes, focuses on system boundaries and external actors. Same Structurizr color palette.

### B12: Batch/comparison generation mode
- **Priority:** P3
- **Status:** Pending
- **Details:** Generate same prompt across multiple providers/models in one call. Returns side-by-side results for comparison. Useful for benchmarking and style selection.

### B13: PyPI package publishing
- **Priority:** P2
- **Status:** Pending
- **Details:** Publish `diagram-forge` to PyPI so users can `pip install diagram-forge`. Add pyproject.toml metadata, classifiers, build workflow.

### B14: Output format options (SVG, PDF)
- **Priority:** P3
- **Status:** Pending
- **Details:** Currently PNG only. Some use cases need SVG (scalable) or PDF (print). Research provider support — may need post-processing with cairosvg or similar.

### B15: Prompt preview / dry-run mode
- **Priority:** P2
- **Status:** Pending
- **Details:** Show the fully rendered prompt without generating an image. Helps users debug template variable substitution and understand what gets sent to the provider. Zero cost.

## Completed

### B0: Template v2 upgrade
- **Completed:** 2026-02-13
- **Details:** All 9 templates upgraded to v2 with hex codes, explicit rendering instructions, layout rules. Added c4_container and exec_infographic templates. Default Gemini model → gemini-3-pro-image-preview. Auto provider selection logic. Style reference baselines saved.
