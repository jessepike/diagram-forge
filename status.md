# Diagram Forge — Status

## Current State
- **Stage:** Develop → approaching OSS launch
- **Last session:** 2026-04-21 — gpt-image-2 upgrade + Gemini model ID fix + OSS launch planning
- **Branch:** main (origin in sync; commit `5e72c66` force-pushed earlier)
- **Latest commit:** `5e72c66 feat(openai): upgrade to gpt-image-2-2026-04-21 with quality tiers`

## Live URLs (current, pending Vercel-only consolidation)
- **Frontend:** https://diagram-forge.vercel.app
- **Backend:** https://api-production-0eac.up.railway.app

## Session Log
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
1. **ROTATE EXPOSED KEYS** — BACKLOG B21 blocks everything. Do first.
2. CTO to review `docs/sync-skill-design.md` open questions (#1-8)
3. CTO to approve the 4 new template proposals in `docs/template-proposals.md`
4. Delegate sync skill core implementation (tasks 1-6, 9) to Codex
5. Delegate 4 new templates to Codex in parallel
6. Forge retains: Claude Code skill, GH Action template, launch copy, launch execution

## Blockers / Open Questions
- Exposed keys need rotation (BACKLOG B21)
- Name collision check: is "Diagram Forge" clear of trademark issues?
- Claude Code plugin marketplace status — can we submit?
- Gemini 3 Pro `-preview` suffix: how long until it drops? Could break our config again.

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
