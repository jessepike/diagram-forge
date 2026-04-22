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

### B16: Auto-regeneration hook (file-watch triggered)
- **Priority:** P2
- **Status:** Pending
- **Details:** PostToolUse or file-watch hook that detects when source markdown files (e.g. workstreams.md, roadmap.md) are saved and queues diagram regeneration. Could be a Claude Code hook or a lightweight file watcher script. Goal: diagrams stay in sync with flat files without manual `/diagrams` invocation. Daily or on-save trigger options. First validated in EvenGround project.
- **Acceptance:** Saving a source file triggers regeneration of dependent diagrams. User can opt-in per project.

### B17: brand_infographic template
- **Priority:** P2
- **Status:** Template YAML written (2026-02-27) — needs testing and baseline style reference
- **Details:** New template for investor/marketing slides with warm brand aesthetic (cream background, serif headlines, organic decoration, brand color palette). Designed to work with project-specific brand style references. Tested first with EvenGround brand style reference.
- **Template file:** `src/diagram_forge/templates/brand_infographic.yaml`
- **Acceptance:** Generates investor-quality slides that match a provided brand style reference

### B19: "Technical Brief" template (feature_brief)
- **Priority:** P2
- **Status:** Pending — pattern validated in EvenGround session (2026-03-01)
- **Details:** A portrait-format (9:16) 1-page technical brief template for summarizing what was built in a feature area. Pattern: title bar → foundation/context strip → gap/change cards (2-col grid with colored left borders) → flow diagram → coverage footer. Proven useful for async team oversight at speed — lets a founder/PM quickly understand architectural decisions without reading code diffs.
- **Reference diagram:** `/Users/jessepike/code/clients/even-ground/docs/diagrams/crisis-detection-brief.png`
- **Key design elements:** colored left-border cards (red/amber/orange by severity), horizontal flow diagram with color-coded steps, dark navy header + footer, dense but readable, monospace for file/code refs
- **Template file:** `src/diagram_forge/templates/feature_brief.yaml` (to create)
- **Acceptance:** Generates a readable 1-page technical brief from structured prompt input. Works well at 9:16 aspect ratio in 2K resolution.

### B18: PM diagram templates (product_roadmap, workstreams, kanban)
- **Priority:** P2
- **Status:** Templates written and live (2026-02-27) — validated with EvenGround project
- **Details:** Three new templates for product/project management diagrams. Fills a major gap — Diagram Forge had no PM-native templates before this. All three validated with real project content and iterated to production quality.
  - `product_roadmap` — phase pipeline with gate icons, status badges, expansion banner
  - `workstreams` — priority swimlanes with status, items, dependency notes
  - `kanban` — three-column board with category color bars, no-duplicate guard
- **Style references:** `minimal-app-ui`, `minimal-kanban`, `product-roadmap-status` saved as baselines
- **Acceptance:** Already complete — add to README, update template count

### B20: Move API keys out of plaintext ~/.zshrc
- **Priority:** P0
- **Status:** Pending — now also blocking OSS launch
- **Details:** GEMINI_API_KEY and OPENAI_API_KEY are exported as plaintext in `~/.zshrc` (lines 57-58). This was set up for diagram-forge's MCP config which reads `${GEMINI_API_KEY}` / `${OPENAI_API_KEY}` env vars. The MCP `.mcp.json` pattern is correct (env var references, not hardcoded values), but the source of those vars is insecure. Options: (1) macOS Keychain via `security find-generic-password` in a sourced script, (2) `.env` file with restricted permissions (`chmod 600`) sourced from `.zshrc`, (3) 1Password CLI (`op read`). Whichever approach, the keys must still be available as env vars at shell startup so Claude Code can resolve them when spawning MCP servers.
- **Acceptance:** API keys no longer appear in plaintext in any version-controllable or widely-readable file. MCP servers still start correctly.

### B21: Rotate exposed API keys (post-f1fbc38 leak)
- **Priority:** P0 — do this BEFORE any OSS launch or further push activity
- **Status:** Pending
- **Details:** On 2026-04-21, GitHub push protection caught commit `f1fbc38` containing `.env` with literal `OPENAI_API_KEY` and `GEMINI_API_KEY`. The commit never reached GitHub (push rejected, history rewritten to `5e72c66`, force-pushed clean). But the keys existed in plaintext on local disk in git history. Treat as compromised.
- **Acceptance:**
  1. Revoke the OpenAI key that was in `f1fbc38` at https://platform.openai.com/api-keys (inspect the commit locally via `git show backup-f1fbc38 -- .env` to confirm the exact key before revoking)
  2. Revoke the Gemini key that was in `f1fbc38` at https://aistudio.google.com/apikey
  3. Issue replacements
  4. Update: local `.env`, Railway env vars, Vercel env vars, any `~/.zshrc` exports
  5. Delete local backup tags: `git tag -d backup-before-cleanup backup-f1fbc38`

### B22: OSS launch prep — repo polish
- **Priority:** P1 (blocking OSS launch)
- **Status:** Pending
- **Details:** Current repo is private-quality. Needs OSS-grade polish before HN/X launch.
- **Tasks:**
  1. Delete `diagram-forge-plugin/.mcp.json.bak` — encodes the insecure shell-export pattern, misleading for OSS users. Live `.mcp.json` already uses `${user_config.*}` interpolation correctly.
  2. Add `.env.example` to repo with placeholder values for `GEMINI_API_KEY`, `OPENAI_API_KEY`. Commit to repo; users copy to `.env` (gitignored).
  3. README overhaul:
     - Hero section with 3-4 best generated diagrams
     - Clear "Getting started" by install mode (Claude Code plugin | pip install CLI | self-hosted web)
     - "Getting your keys" section linking OpenAI + Google key pages
     - Architecture diagram (built with diagram-forge itself — meta/demo)
     - Cost comparison table (gpt-image-2 vs Gemini vs gpt-image-1-mini)
     - License badge, install badge, test badge, PyPI badge
     - Demo video embed (30s screencast)
     - Link to live BYOK demo
  4. Pick license (MIT recommended — HN-friendly, permissive, zero friction)
  5. Add `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` (basic stubs)
  6. Add GitHub issue + PR templates
  7. Ensure `pyproject.toml` has complete metadata (author, classifiers, homepage, docs URL, repository URL)
- **Acceptance:** Repo reads as professional, open-source-ready. Someone landing cold can understand what it is, install it, and contribute.

### B23: OSS launch prep — BYOK demo site
- **Priority:** P1 (demo infrastructure for launch)
- **Status:** Pending
- **Details:** Modify the live Vercel/Railway demo so visitors can try generation with their OWN API key pasted into the UI. Zero cost to project owner, defensible security posture. Key must never be logged or stored server-side.
- **Implementation approach:**
  - Frontend: add "Use your own key" field (password input, `sensitive`, not persisted in localStorage by default — maybe session storage with explicit opt-in)
  - Backend: accept `X-User-Gemini-Key` / `X-User-OpenAI-Key` headers, use instead of server env vars for that request only
  - NEVER log, never store, never cache
  - Add rate limit (10 req/min per IP) even with BYOK to prevent abuse of the infrastructure itself
  - Clear privacy notice: "Your key is sent directly to OpenAI/Google, never stored on our servers. Inspect the code."
- **Acceptance:** User can paste their key into the demo, generate diagrams, and the project owner pays $0 for demo usage.

### B24: OSS launch prep — static demo gallery
- **Priority:** P1 (primary "demo" for readers who don't click BYOK)
- **Status:** Pending
- **Details:** Generate and commit a curated gallery of 20-30 example diagrams covering every template × key style reference × both providers. These are the portfolio pieces that sell the project to HN readers who won't bother clicking anything.
- **Tasks:**
  - One best example per template (13 images minimum)
  - Provider comparison: same prompt, Gemini vs gpt-image-2, side by side (at least 3 pairs)
  - Style reference showcase (agent-capabilities-card, minimal-kanban, exec-infographic)
  - Organize in `docs/gallery/` with an index MD
  - README hero + landing page hero pull from this gallery
- **Acceptance:** Gallery is the first impression. Someone scrolling the README in 15 seconds should walk away thinking "this is legitimately good."

### B25: OSS launch prep — 30-second screencast demo
- **Priority:** P2
- **Status:** Pending
- **Details:** Short screen recording: prompt typed → diagram appears → iteration. Embed in README (GIF or YouTube). Zero infra cost, high conversion.

### B26: OSS launch prep — PyPI publish
- **Priority:** P2 (supersedes B13)
- **Status:** Pending
- **Details:** Publish `diagram-forge` to PyPI so `pip install diagram-forge` works. Required for the "Python library direct" install mode to feel legitimate.
- **Blocks:** README install instructions, HN "Show HN" post credibility.

## Completed

### B0: Template v2 upgrade
- **Completed:** 2026-02-13
- **Details:** All 9 templates upgraded to v2 with hex codes, explicit rendering instructions, layout rules. Added c4_container and exec_infographic templates. Default Gemini model → gemini-3-pro-image-preview. Auto provider selection logic. Style reference baselines saved.
