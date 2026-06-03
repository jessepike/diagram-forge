# Diagram Forge — Status

## Current State
- **Stage:** Develop → approaching OSS launch
- **Last session:** 2026-05-06 — env-handling regression fixed + provider routing inverted (OpenAI primary)
- **Branch:** main
- **Latest commits (3 unpushed):**
  - `9cd9b44 feat(routing): default to OpenAI gpt-image-2, Gemini secondary`
  - `15d8fba fix(env): treat empty-string env vars as unset before load_dotenv`
  - `e173ed2 feat: load .env automatically on import — decouple from CC plugin user_config`

## Live URLs (current, pending Vercel-only consolidation)
- **Frontend:** https://diagram-forge.vercel.app
- **Backend:** https://api-production-0eac.up.railway.app

## Session Log
- **2026-06-03**: Background theme switch — LIGHT is now the portfolio-wide default (Forge, via Krypton handoff `2026-06-03-diagramforge-light-default.md`). Added a `Theme` enum + `theme` field on `GlobalDesignTokens` + a built-in dark color preset (`_DARK_COLOR_OVERRIDES`, charcoal `#0E1116`). `generate_diagram` gained `theme: str = "light"`; `build_prompt`/`build_global_style_block` are theme-aware and emit an authoritative `BACKGROUND THEME: LIGHT|DARK` directive that overrides per-template "white background" hints (under dark, the template `style_defaults` background defers to the theme to avoid a conflicting signal). The configured default lives in `config/design_tokens.yaml` (`theme: light`) — one switch, no per-template find-replace. Dark stays reachable via `generate_diagram(theme="dark")`. Note: the *source* templates were already `background: white`; the prior dark `exec_infographic` came from per-call palette overrides, not a dark source default — so this change makes the light default explicit AND adds the missing dark switch (previously dark required hand-written prompt overrides). 5 new theme tests in `test_templates.py`; full suite green except the pre-existing `test_config::test_load_default_config` failure (stale gemini-default assertion, unrelated to this work). Double registration reconciled: `mcp__diagram-forge__*` (standalone, `~/.claude.json`) and `mcp__plugin_diagram-forge_diagram-forge__*` (plugin via `diagram-forge@capabilities-registry`) both run the SAME `python -m diagram_forge.server` from THIS repo, so the change lands on both surfaces from one edit; no source-level de-dup needed. **Requires MCP server restart to take effect** (running servers cache old code). De-dup of the two registrations is a config-level question for Jesse (see Next Steps).
- **2026-05-06**: Env-handling regression fixed + provider routing inverted. CC auto-update migration silently dropped the `~/.claude.json` mcpServers entry between Apr 27 and May 1 (40 zombie MCPs spawned over 9 days, all failing with empty-string env vars). Diagnosed via memory MCP search + git history. Three commits: (a) `e173ed2` — `load_dotenv()` in `__init__.py`; (b) `15d8fba` — empty-string-as-unset fix (the actual production fix; partial fix initially shipped without testing the exact failure mode); (c) `9cd9b44` — provider routing: `default_provider: openai`, fallback chain inverted to `[openai, gemini, gemini_flash_31]`, tool docstring rewritten so callers leave `provider="auto"`. Live end-to-end verified: gpt-image-2 generation under empty-string env, 628KB PNG, $0.006, model `gpt-image-2-2026-04-21`. New AWS standard `mcp-server-env-handling.yaml` codifies the prevention pattern for all future Pike MCPs. New BACKLOG section "OSS Launch — Plugin Distribution Readiness" (OSS-01 through OSS-05) tracks remaining product fixes for OSS-readiness.
- 2026-04-21: gpt-image-2 upgrade (`gpt-image-2-2026-04-21`), `quality` param (low/medium/high/auto) wired through MCP tool → provider → API, per-tier cost tables with real OpenAI rates, `recommended_quality` on templates, openai_mini provider alias, clean-commit history rewrite (removed leaked `.env` from `f1fbc38`, force-pushed to origin). Gemini model IDs corrected — `-preview` suffix still required, was wrongly dropped. OSS launch plan authored across three coordinated docs.
- 2026-02-28: Deploy complete — Railway backend + Vercel frontend, e2e smoke test passed
- 2026-02-27: WUI-01 through WUI-06 complete — web UI scaffolded + deployed

## Active Work
- **OSS launch prep** (see `docs/launch-plan.md` — 9-day plan, Phase 0.2 already complete)
  - Phase 0: rotate exposed keys (blocking — BACKLOG B21)
  - Phase 2.5: sync skill + 4 new templates (see `docs/sync-skill-design.md`, `docs/template-proposals.md`)
  - Phase 3: gallery + BYOK Vercel Edge Function demo (retires Railway)
  - Target: Tue/Wed HN launch, 9 days from kickoff

## Next Steps
1. **ROTATE EXPOSED KEYS** — BACKLOG B21 blocks OSS launch. Post-rotation, just edit `.env` (load_dotenv handles the rest).
2. **OSS-01 (launch blocker)** — fix `--directory` hardcoding in plugin's `.mcp.json`. Either `${CLAUDE_PLUGIN_ROOT}` substitution or PyPI package + plain `python -m diagram_forge.server`.
3. **OSS-02 / OSS-03 / OSS-04** — drop redundant `userConfig` schema, write README setup, smoke-test on fresh machine.
4. CTO to review `docs/sync-skill-design.md` open questions (#1-8)
5. CTO to approve the 4 new template proposals in `docs/template-proposals.md`
6. Delegate sync skill core implementation (tasks 1-6, 9) to Codex
7. Delegate 4 new templates to Codex in parallel
8. Forge retains: Claude Code skill, GH Action template, launch copy, launch execution

## Blockers / Open Questions
- Exposed keys need rotation (BACKLOG B21) — verified still functional 2026-05-06 but rotation is hygiene
- Name collision check: is "Diagram Forge" clear of trademark issues?
- Claude Code plugin marketplace status — can we submit?
- Gemini 3 Pro `-preview` suffix: how long until it drops? Could break our config again.

## Reference: env handling architecture (post 2026-05-06)
- **Server reads keys from `<repo>/.env`** via `load_dotenv()` in `src/diagram_forge/__init__.py` — runs at package import, before any module reads env.
- **Empty-string env vars are stripped before dotenv load** — defends against CC plugin spawn passing `OPENAI_API_KEY=""` from empty user_config substitution.
- **No CC config files contain literal keys.** `~/.claude.json` mcpServers entry uses `uv run --env-file` (belt-and-suspenders backup; the load_dotenv path is now primary).
- **AWS standard:** `~/code/_shared/aws/docs/standards/mcp-server-env-handling.yaml` v1.0.0. All future Pike MCPs must follow this pattern.

## Reference Docs Added This Session
- `docs/launch-plan.md` — 9-day OSS launch plan with positioning, phases, timeline
- `docs/sync-skill-design.md` — implementation blueprint for sync skill (10h effort)
- `docs/template-proposals.md` — specs for 4 new templates (network, schema, state machine, user flow)

## Handoff — 2026-04-21 (Forge → CTO)

**From:** Forge session (product work with consent — gpt-image-2 upgrade + launch planning)
**To:** CTO agent session
**Context:** OSS launch plan authored across 3 coordinated docs. Phase 0.2 (Gemini model IDs) complete. Phase 0.1 (rotate keys) is user task, not agent. Phase 2.5 (sync skill + 4 new templates) is the core differentiator and needs CTO design review before Codex implementation can start.

**Next actions for CTO:**
1. Review `docs/sync-skill-design.md` — work through 8 open design questions (prompt strategy defaults, summarize LLM choice, concurrency, template versioning, etc.)
2. Approve/edit 4 new template proposals in `docs/template-proposals.md`
3. Confirm hosting decision: Vercel-only Option C (Edge Function BYOK proxy), retire Railway
4. Confirm positioning shift: "living diagrams" narrative, sync as the moat
5. Produce a decision log entry that Codex can pick up for Phase 2.5 implementation

**Key files (read first):**
- `docs/launch-plan.md` — full plan context, especially Phase 2.5 and "Positioning" section
- `docs/sync-skill-design.md` — 8 open questions at the bottom need CTO calls
- `docs/template-proposals.md` — 4 template specs for approval
- `BACKLOG.md` — B21 (blocking user task), B22-B26 (launch prep)
- `CLAUDE.md` — project context

**Model recommendation:** Opus 4.7 + xhigh — design review with architectural implications, needs best reasoning.

**User should do in parallel:** BACKLOG B21 — rotate exposed OpenAI + Gemini keys (not an agent task).

**Two unpushed commits on main** (`5e72c66`, `1ee6753`) — push when ready.
