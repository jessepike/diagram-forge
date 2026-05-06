# Diagram Forge — Backlog

## Web UI (Active — Develop Stage)

Work items for `web/` monorepo. Build in order.

| ID | Item | Priority | Status | Notes |
|---|---|---|---|---|
| WUI-01 | FastAPI skeleton — `web/api/` with `/health`, `/templates`, `/generate` (mock response), `/extract` | P0 | Pending | Dockerfile for Railway; X-API-Secret auth on all routes |
| WUI-02 | Next.js scaffold — `web/frontend/` layout, left panel, right panel, Settings component | P0 | Pending | Tailwind CSS 4, light theme; Settings as slide-out panel |
| WUI-03 | Wire generate end-to-end — real diagram-forge call, base64 response, provider resolution | P0 | Pending | Frontend resolves "auto" before API call; 3MB PNG cap; 60s timeout |
| WUI-04 | File upload + `/extract` — multipart upload, PyMuPDF (PDF) + python-docx (DOCX), extract-on-select flow | P0 | Pending | On file selection → call /extract → populate textarea → switch to Paste tab |
| WUI-05 | Error states, loading states, polish — all 4 states (initial/generating/success/error), char counter, provider badges | P1 | Pending | 50k char limit enforced client + server; skeleton during generation |
| WUI-06 | Deploy — Railway (Dockerfile) + Vercel; env vars; CORS locked to Vercel URL | P1 | Pending | `RAILWAY_API_SECRET` on both; `RAILWAY_API_URL` on Vercel |
| WUI-07 | Visual polish — apply Stitch palette and component patterns | P2 | Pending | Reference: `docs/diagram_forge_main_dashboard/`, `docs/diagram_forge_settings_panel/` |

## OSS Launch — Plugin Distribution Readiness

Items required before the diagram-forge Claude Code plugin can be installed and run by an external user (a stranger cloning the repo or installing via a future PyPI release). Surfaced 2026-05-06 during a CC migration regression that exposed how the plugin currently can't work for anyone but Jesse on Jesse's machine.

| ID | Item | Priority | Status | Notes |
|---|---|---|---|---|
| OSS-01 | **Plugin `.mcp.json` `--directory` is hardcoded to `/Users/jessepike/code/_shared/diagram-forge`** — OSS users have no such path. | P0 (launch blocker) | Pending | Two paths: (a) replace with `${CLAUDE_PLUGIN_ROOT}` so it resolves relative to wherever the plugin gets installed, OR (b) ship the server as a PyPI package and have the plugin's MCP just call `python -m diagram_forge.server` (no --directory needed). (b) is cleaner; pairs with B13. |
| OSS-02 | **Decide: keep `userConfig` schema in `plugin.json` or drop in favor of pure `.env`** | P1 | Pending | Now that `__init__.py` runs `load_dotenv()`, the `userConfig` substitution is no longer required — the server reads keys from `.env` regardless. Trade-off: `userConfig` is the canonical CC plugin UX (interactive `/plugins config`) vs `.env` is Unix-native and survives CC config migrations. Recommend dropping `userConfig` to remove a redundant layer; document `.env` setup in README. |
| OSS-03 | **README setup instructions for OSS users** — current README does not document the `cp .env.example .env` flow or the plugin install path | P1 | Pending | Reference the existing `docs/launch-plan.md`. Cover: clone, `.env`, `claude plugins install`, first-run check, troubleshooting. |
| OSS-04 | **Verify plugin works end-to-end on a fresh machine** | P1 | Pending | Smoke-test on macmini or a fresh OrbStack VM: clone, install plugin, generate one diagram. If it fails for any reason (missing dep, hardcoded path, etc.), fix before launch. |
| OSS-05 | **Document the dual-registration history + the post-load_dotenv simplification** in `docs/launch-plan.md` | P2 | Pending | Future maintainer needs to know why `load_dotenv()` is in `__init__.py` and that it intentionally bypasses CC's `${user_config.X}` template flow. |

### Recently completed

| Date | Item | Notes |
|---|---|---|
| 2026-05-06 | **`load_dotenv()` in `src/diagram_forge/__init__.py`** | Server now loads keys from repo `.env` regardless of how it was launched. Decouples key resolution from CC's MCP env-passing layer. Resolves the regression where a CC auto-update migration silently wiped the `~/.claude.json` mcpServers entry between Apr 27 and May 1, breaking diagram generation for ~9 days. Added `python-dotenv>=1.0.0` to explicit deps (was already transitive). Created `.env.example`. See `_shared/pike-agents/CHANGELOG.md` for full diagnostic write-up. |

## MCP Server Backlog

| ID | Item | Priority | Status | Notes |
|---|---|---|---|---|
| B01 | Restore `recommended_provider` / `model` fields to new templates (product_roadmap, workstreams, kanban, brand_infographic) | P1 | Pending | Added in B17/B18 without these fields |
| B02 | Test remaining templates — architecture, component, sequence, integration, infographic | P1 | Pending | Visual QA pass |
| B13 | Publish to PyPI — `pip install diagram-forge` | P2 | Pending | Requires pyproject.toml version + twine setup. **Pairs with OSS-01.** |
| B15 | Prompt preview / dry-run mode — show rendered prompt without generating | P2 | Pending | Useful for debugging templates |
| B21 | **Rotate OpenAI + Gemini API keys** | P1 | Pending | Both keys leaked in commit `f1fbc38` on 2026-04-21, history rewritten via squash to `5e72c66` but keys hit local disk. Verified still functional 2026-05-06. After rotation, just update `.env` — no other config touches needed (load_dotenv handles the rest). |

## Rendering Quality — Observed from Production Use

Source: EvenGround master backlog kanban (37 cards, 6 categories, 3 generations + 2 edits, 2026-03-01)
Golden example: `~/.diagram-forge/styles/minimal-kanban/examples/master-backlog-kanban.md`

| ID | Item | Priority | Status | Notes |
|---|---|---|---|---|
| RQ-01 | **Duplicate card rendering on large boards** — Gemini duplicates cards when kanban has 15+ total cards. Template has "EXACTLY ONCE" instruction but model ignores at scale. | P1 | Pending | Observed: P1-06 duplicated in Done column on first gen. Fix: add explicit per-column count enforcement + total count verification in prompt |
| RQ-02 | **Edit drift — fixing one card introduces new duplicates** — edit_diagram re-renders everything, whack-a-mole effect. Fixing P1-06 dupe caused FIX-2 dupe. Required 2 edit passes. | P1 | Pending | Fix: include full card manifest in edit prompt; add "DO NOT modify unspecified cards" instruction |
| RQ-03 | **Structured card data instead of free-text blocks** — template variables accept free text, losing structure. Callers manually format each card. | P2 | Pending | Proposed: accept JSON/YAML card arrays, template engine renders deterministically with guaranteed no dupes and correct counts |
| RQ-04 | **Golden example prompts per template** — ship example prompts alongside templates so callers know optimal input format. | P2 | In Progress | Done: kanban (`minimal-kanban/examples/`). TODO: architecture, c4, data_flow, workstreams, roadmap, exec_infographic, sequence, component, integration |
| RQ-05 | **Post-generation vision validation** — optional validation step using vision model to count elements, detect dupes, verify legend, check legibility. Return validation report alongside image. | P2 | Pending | Opt-in via `validate: true` parameter |
| RQ-06 | **Template-level card count enforcement** — auto-count from input and inject: "TO DO must have EXACTLY 19 cards, no more, no less. TOTAL: 35 unique cards." Lightweight version of RQ-05. | P2 | Pending | Pure prompt engineering, no vision model needed |
