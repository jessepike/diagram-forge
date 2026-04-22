# Diagram Forge — OSS Launch Plan

**Target launch:** 9 days from kickoff (Tue/Wed for HN).
**Objective:** Establish builder credibility via a polished OSS release on GitHub → HN → X, while keeping ongoing cost to $0.
**Positioning:** *Living diagrams for engineering teams* — not "another AI image tool."
**Status:** Planning. Kickoff TBD.

---

## North Star

A developer lands on the repo cold. Within 15 seconds they think: *"This person knows what they're doing. This tool is real. I want to try it."*

Three sub-goals:
1. **Portfolio piece** — show engineering craft (clean architecture, tests, docs, commit discipline).
2. **Community contribution** — something real people actually install and use.
3. **Reach** — front page of HN, 100+ GH stars in first week, meaningful X engagement.

**Non-goals:**
- Don't try to monetize at launch.
- Don't build SaaS infrastructure.
- Don't onboard users who'll cost money to support.

---

## Positioning

**The pitch (one line):**
> *"Architecture diagrams that stay in sync with your docs. Change the source, the diagrams regenerate."*

**The longer pitch:**
> Every engineer has shipped a diagram that rotted within a month. Diagram Forge fixes this. You declare which diagrams depend on which source files, and when the sources change, the diagrams regenerate. Ships with 17+ templates covering architecture, network, schema, state machines, user flows, roadmaps, and more. Built on Gemini 3 Pro and gpt-image-2, MCP-native, BYOK.

**Why this positioning wins:**
- "AI image generator" is commoditizing. Every week brings another one. You'll drown in the noise.
- "Living diagrams" is a category that doesn't exist yet. Own it.
- Templates and providers become supporting evidence for the sync story, not competing concepts.
- HN readers are docs-as-code people. The "keep your diagrams current" pain is shared and deep.

**What we DON'T say at launch:**
- Don't lead with "AI-powered" — it's the air we breathe, not a feature
- Don't list every template — hero 5, mention the rest
- Don't undersell sync — it's the moat, surface it early and often

---

## Principles

1. **BYOK or nothing.** Zero ongoing provider cost. Every demo path sends requests using the user's own API key.
2. **Ship the engineering, not the hype.** Lead with the sync feature, template system, provider ABC, cost tracking — the real work — not marketing copy.
3. **Gallery over live demo.** Most viewers will judge by pictures. Optimize the curation ruthlessly.
4. **One platform for hosting.** Consolidate to Vercel. Retire Railway.
5. **Be honest about limitations.** Hallucinations, cost, model drift. HN will forgive a limitation acknowledged; they'll crucify one hidden.
6. **Sync is the category, not a feature.** Everything else is supporting evidence.

---

## Phase 0 — Preconditions (BLOCKING)

**Cannot start any other phase until these are done.** Failing to do Phase 0 first = catastrophe.

### 0.1 Rotate exposed API keys (BACKLOG B21)
- Revoke the exposed OpenAI key at https://platform.openai.com/api-keys (see BACKLOG B21 for key identification)
- Revoke the exposed Gemini key at https://aistudio.google.com/apikey
- Issue replacements
- Update local `.env`, Railway env vars, Vercel env vars, `~/.zshrc`
- Delete backup tags: `git tag -d backup-before-cleanup backup-f1fbc38`
- **Verification:** old keys return 401 from their respective providers; new keys work via MCP

### 0.2 Verify Gemini model IDs — ✅ COMPLETE (2026-04-21)
- Smoke test confirmed: `-preview` suffix still required
- Config updated: `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`
- Committed in same session as gpt-image-2 upgrade

### 0.3 Set provider spend limits (defense in depth)
- OpenAI: `$20/day`, `$50/month` hard caps
- Gemini: spend alerts at `$10/month`
- Railway: usage alerts (even though we're retiring it)

**Exit criteria:** Keys rotated. Models confirmed working. Spend caps in place.

---

## Phase 1 — Architecture decisions (1 day)

### 1.1 Hosting: Vercel-only, Option C (Edge Function proxy)
Retire Railway. Single platform. Architecture:

```
User browser
   │ (BYOK: user pastes key)
   ▼
Next.js static site on Vercel
   │ POST /api/generate  with X-User-Key header
   ▼
Vercel Edge Function
   │ (no logging, no storage)
   ▼
OpenAI / Gemini API
   │
   ▼
Response streamed back to browser
```

**Why not Option A (Python Fluid Compute on Vercel):** works but heavier. Edge Function is lighter and sufficient for a proxy.
**Why not Option B (browser-direct):** OpenAI CORS may warn, and keys in DevTools alarm users.
**Why not Cloudflare:** Python on Workers still behind Fluid Compute maturity; not worth ecosystem switch.

### 1.2 License: MIT
Most permissive, HN-friendly, zero friction. No copyleft complications.

### 1.3 PyPI package name: `diagram-forge`
Confirm available. If taken, fall back to `diagramforge` or `mcp-diagram-forge`.

### 1.4 Brand decisions
- **Name:** "Diagram Forge" (keep)
- **Tagline:** TBD — workshop during repo polish. Candidate: *"AI-native architecture diagrams, with the engineering to match."*
- **Logo:** Skip for v0.1.0. Text wordmark is fine. Can add later.

**Exit criteria:** Hosting decision locked, license picked, PyPI name confirmed, tagline settled.

---

## Phase 2 — Repo polish (2-3 days)

### 2.1 Cleanup (BACKLOG B22)
- [ ] Delete `diagram-forge-plugin/.mcp.json.bak` — encodes old insecure pattern
- [ ] Delete `data/chroma/` (untracked), ensure gitignored
- [ ] Verify no secrets anywhere via `gitleaks` or equivalent scan
- [ ] Add `.env.example` with placeholders for every env var the project reads
- [ ] Audit `.gitignore` — add `*.db-shm`, `*.db-wal`, `tsconfig.tsbuildinfo`, `data/*.db*`

### 2.2 Repo metadata
- [ ] `LICENSE` — MIT, your name + year
- [ ] `CONTRIBUTING.md` — basic contribution flow, dev setup, test expectations
- [ ] `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1 (standard template)
- [ ] `SECURITY.md` — how to report a vulnerability (use GitHub security advisories, not public issues)
- [ ] `.github/ISSUE_TEMPLATE/` — bug report + feature request templates
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` — checklist
- [ ] `pyproject.toml` — complete metadata (author, classifiers, homepage, docs URL, repository URL, keywords)

### 2.3 README overhaul
**This is your portfolio piece.** Target 5 min read. Structure:
1. **Hero** — name, tagline, 2-3 badges (license, PyPI, tests), one killer screenshot
2. **What it does** — 3 sentences, no hype
3. **Gallery preview** — 6 best diagrams in a grid with links to full gallery
4. **Why** — the pain story. "I was making architecture diagrams in Lucidchart..."
5. **Quickstart** — 3 install modes (Claude Code plugin | pip | self-hosted), each with one-line install + one-line use
6. **How it works** — architecture diagram (generated BY diagram-forge — meta/demo), 3 paragraphs
7. **Capabilities** — templates list, style references, cost tracking, multi-provider
8. **Costs** — transparent table (gpt-image-2 tiers, Gemini, gpt-image-1-mini)
9. **Comparison** — brief "vs Mermaid/PlantUML/Lucidchart/Excalidraw" section
10. **Roadmap** — 3-4 bullets of what's next (signals active development)
11. **Contributing** — link to CONTRIBUTING.md
12. **License + credits**

### 2.4 Test + lint hygiene
- [ ] CI via GitHub Actions: run tests on push/PR, `ruff`, `mypy`
- [ ] README test badge from CI
- [ ] Coverage badge (optional, codecov or similar free tier)
- [ ] All existing tests pass locally
- [ ] Pre-commit config (`pre-commit-config.yaml`) — ruff + basic hygiene

### 2.5 Code audit pass
Before OSS eyes, one sweep through:
- [ ] No TODOs referencing personal/sensitive context
- [ ] No hardcoded paths (e.g., `/Users/jessepike/`)
- [ ] No personal project references in comments
- [ ] Docstrings on all public APIs
- [ ] Provider ABC is clearly documented as the extension point
- [ ] Template system has a "how to add a template" section

**Exit criteria:** Cold-landing visitor can clone, install, test, and submit a PR without asking a question.

---

## Phase 2.5 — Core differentiator: Sync skill + new templates (2 days)

This phase is what turns the launch from "another AI image tool" into "the living diagrams tool." Required for the positioning to hold up.

### 2.5.1 Auto-update sync skill
See detailed design at `docs/sync-skill-design.md`. Summary:

- **Manifest** (`diagrams.yaml`) declares which diagrams depend on which source files
- **State tracking** (`.diagram-forge/state.json`) hashes sources for staleness detection
- **CLI command** `diagram-forge sync` — status, apply, budget-capped, force, dry-run, watch modes
- **Claude Code skill + slash command** `/diagrams-sync` — interactive flow inside CC
- **GitHub Action template** — users can drop in to auto-regenerate diagrams on PR merge

**Effort:** ~10h — see sync design doc for task breakdown. Recommended split:
- Core (manifest, state, detect, strategies, CLI, tests) → delegate to Codex
- Claude Code skill + GH Action template → Forge does these

### 2.5.2 New templates (4 additions)
See detailed specs at `docs/template-proposals.md`. The 4 at launch:

1. **`network_diagram`** — L2/L3/cloud topologies (SRE/ops audience)
2. **`database_schema`** — ERD with relationships, keys, domain groupings (backend audience)
3. **`state_machine`** — states, transitions, guards, composite states (distributed systems audience)
4. **`user_flow`** — actors, actions, decisions, outcomes (product/UX audience)

Each template: ~2h including design + test generation. Total: ~8h, <$1 in provider cost.

**Effort:** ~8h total. Largely mechanical once designs are approved — Codex can do these in parallel after CTO reviews the template-proposals doc.

### 2.5.3 Update positioning artifacts with new breadth
- Gallery (Phase 3.1) needs to cover architectural + PM + communication + **new templates**
- README hero updated to show range
- HN post opens with sync narrative, templates listed as supporting evidence

**Exit criteria:** `diagram-forge sync` works end-to-end on a real repo (use diagram-forge itself as dogfood — its own architecture diagrams are sync-managed). All 4 new templates generate acceptable output on both providers.

---

## Phase 3 — Demo infrastructure (2 days)

### 3.1 Static demo gallery (BACKLOG B24)
The primary "demo" for 95% of readers.

- [ ] `docs/gallery/` directory with subdirs by cluster: `architecture/`, `network/`, `schema/`, `pm/`, `communication/`, `state/`, `flow/`
- [ ] One best-of-breed generation per template (17 total — 13 existing + 4 new)
- [ ] 3 provider comparison pairs (Gemini 3 Pro vs gpt-image-2 high, same prompt)
- [ ] 3 style reference showcases
- [ ] **Sync demo** — short animated GIF or image series showing: edit markdown → run sync → diagrams update. This is THE hero artifact.
- [ ] Index page: `docs/gallery/README.md` with grid layout, grouped by cluster
- [ ] Each image has: prompt shown, provider + model used, cost, generation time
- [ ] All images committed to repo (resolutions sized for GitHub: 1536×1024 is fine, ~100KB each with PNG compression)
- [ ] Landing page hero pulls from 3-4 best + the sync demo

### 3.2 BYOK demo site (BACKLOG B23)
Single consolidated Vercel deployment.

**Architecture:**
- Frontend: Next.js (existing `web/frontend/`), static export
- Backend: One Vercel Edge Function at `/api/generate` (NEW — replaces Railway backend)
- Edge Function:
  - Accepts `X-User-Gemini-Key` or `X-User-OpenAI-Key` header
  - Forwards request to appropriate provider
  - Never logs keys, never persists
  - Rate limits by IP: 10 req/min, 50 req/day (abuse prevention on infrastructure, not cost)
  - Returns image + cost estimate

**Frontend UX:**
- Prominent "Bring Your Own Key" panel on landing
- Provider selector (Gemini | OpenAI)
- API key input (password field, session-storage by default, "remember" checkbox for localStorage)
- Template picker
- Prompt textarea
- Generate button with cost preview ("This will cost ~$0.041")
- Result panel with download + share-link button

**Security posture:**
- Clear privacy notice: "Your key is proxied to OpenAI/Gemini through a Vercel Edge Function that does not log or store it. Inspect the source."
- Link to Edge Function source in repo
- No analytics on the key submission path
- No third-party scripts on the demo page (no Google Analytics, no ad networks)

### 3.3 Screencast (BACKLOG B25)
30-60 seconds. One take if possible, or clean edit.
- [ ] Script: prompt → generate → tweak → regenerate. Show cost counter.
- [ ] Screen recording (ScreenStudio, CleanShot X, or Loom)
- [ ] Clean terminal, clean browser, no personal info visible
- [ ] Export as MP4 + GIF (use gifski for quality)
- [ ] Upload to YouTube (unlisted is fine) + commit GIF to repo
- [ ] README embed + HN post embed

**Exit criteria:** Someone cold-landing can view gallery (offline), watch video (zero friction), and try BYOK demo (low friction).

---

## Phase 4 — Distribution (1 day)

### 4.1 PyPI publish (BACKLOG B26)
- [ ] Final pyproject.toml with all metadata
- [ ] Test build locally: `uv build`
- [ ] Test install from wheel in a clean venv
- [ ] Register on PyPI (if not already)
- [ ] Publish: `uv publish` or `twine upload`
- [ ] Verify: fresh machine, `pip install diagram-forge` works
- [ ] Add PyPI badge to README

### 4.2 Claude Code plugin marketplace
If/when CC has a plugin marketplace. Submit with:
- [ ] `plugin.json` sensitive userConfig for keys (already done)
- [ ] Clear setup instructions
- [ ] Screenshot + description

### 4.3 GitHub release
- [ ] Tag `v0.1.0` (or `v0.1.0-beta` if you want to signal early)
- [ ] Release notes: summary, install methods, known limitations
- [ ] Attach generated gallery samples as release assets

**Exit criteria:** Users can `pip install diagram-forge` or install the Claude Code plugin in one command.

---

## Phase 5 — Launch day (1 day, executed on Tue or Wed)

### 5.1 Internal QA (morning before launch)
- [ ] Fresh Claude Code install on a clean machine (or container) — plugin install, key entry, generate a diagram. Time the whole flow.
- [ ] Fresh `pip install diagram-forge` in a clean venv — run CLI, generate a diagram.
- [ ] BYOK demo site — incognito window, paste own key, generate, verify nothing leaks.
- [ ] Click every link in README. Fix any 404.
- [ ] Screencast plays smoothly across devices.

### 5.2 X thread (warm-up, 6:30am PT)
Goal: seed a small group of followers and technical friends. Don't mention HN.

**Thread structure:**
1. Hook — "I was tired of Lucidchart and Mermaid so I built something." [best generated diagram]
2. 3-5 more diagrams showing range (TOGAF, C4, data flow, kanban, infographic)
3. Technical bullet points — provider ABC, YAML template DSL, cost tracking, MCP integration
4. Link to GitHub repo
5. Invitation to try BYOK demo

Pin the tweet. Respond to early replies actively.

### 5.3 HN "Show HN" post (8:00am PT, Tue or Wed)

**Title:** `Show HN: Diagram Forge – living architecture diagrams that stay in sync with your docs`

(Under 80 chars. Lead with the differentiator. Neutral tone.)

**Post body (first comment) draft:**
> Hi HN. Every engineer has shipped an architecture diagram that rotted within a month. I built Diagram Forge to fix this.
>
> You declare which diagrams depend on which source files via a `diagrams.yaml` manifest. When sources change, the diagrams regenerate. Run it locally, via Claude Code, or as a GitHub Action that opens a PR with updated diagrams on every docs push.
>
> ```yaml
> diagrams:
>   architecture:
>     template: architecture
>     sources: [docs/architecture.md, docs/services.md]
>     output: diagrams/architecture.png
> ```
>
> Then `diagram-forge sync --apply` — any sources changed, those diagrams regenerate. That's the whole idea.
>
> Under the hood:
> - **17 templates** across architecture (C4, TOGAF, component, data flow, integration, sequence), network (L2/L3/cloud), schema (ERD), state machines, user flows, and product/PM artifacts (roadmaps, workstreams, kanban)
> - **Pluggable provider ABC** — Gemini 3 Pro, gpt-image-2, gpt-image-1-mini, adding more is one class
> - **Cost tracking** — SQLite per-generation log, quality-tiered (gpt-image-2 at 1536×1024 medium is $0.041; Gemini 3.1 Flash $0.039)
> - **Style reference system** — pin future generations to match an existing image's layout/typography/palette
> - **MCP-native** — Claude Code plugin, but also works as a standalone Python library or CLI
>
> Live demo is BYOK — you paste your own OpenAI or Gemini key, we proxy through a Vercel Edge Function that doesn't log or store it (source in the repo). I built it BYOK so I don't pay for everyone's experimentation.
>
> Honest limitations:
> - Vague prompts → hallucinated component names. The template system mitigates but doesn't eliminate.
> - Slower than Mermaid — a high-quality generation takes ~25s. That's image generation, not me.
> - Text rendering is good but not typesetting-quality for very dense schemas. Use `quality=high` when labels matter.
>
> Built in the open, MIT licensed, happy to take PRs.
>
> [GitHub]  [Demo]  [PyPI]  [Sync demo GIF]

**After posting:**
- Refresh HN homepage at T+30min, T+1h, T+2h
- Camp on the post for 3-4 hours responding to every comment
- Don't get defensive. Acknowledge valid criticism. Show you read carefully.
- If it hits front page, stay on it the rest of the day

### 5.4 Cross-posts (late morning)
- r/LocalLLaMA — reframed for that audience (model comparison, self-hostable)
- r/ClaudeAI — emphasize MCP integration, plugin install
- Lobsters — invite-gated but quality audience, worth it if you have access

### 5.5 Blog post (publish same day or next morning)
**Primary title:** *"Living diagrams: keeping architecture docs in sync with code"*

- ~1500 words
- Lead with the pain (diagrams rot) → solution (sync manifest) → concrete walkthrough of setting it up on a real repo (use diagram-forge itself)
- Show the GitHub Action PR flow
- Real diagram examples from sync output
- Brief provider + cost section as supporting evidence
- Link back to repo and demo
- Post to Substack/Hashnode/personal blog, cross-post to dev.to and Hacker Noon
- Share on X the next day

**Secondary post** (publish 1-2 weeks later to sustain momentum):
*"gpt-image-2 vs Gemini 3 Pro across 17 diagram types — a real evaluation"*
- Use the Tier 2 eval run output
- Scorecards per axis per template
- Cost/latency comparisons
- Honest "use X for Y" recommendations

### 5.6 Monitor
- [ ] OpenAI spend dashboard — should be $0 if BYOK is working
- [ ] Gemini spend dashboard — same
- [ ] Vercel analytics — traffic, Edge Function invocations, errors
- [ ] GitHub — stars, issues, PRs; triage issues within 24h
- [ ] HN comments — respond for 48h at minimum
- [ ] X replies and quote tweets

**Exit criteria:** 48 hours post-launch, state is stable. Issues triaged. Reach captured.

---

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cost blowup if BYOK fails | Low | High | OpenAI spend caps, Vercel rate limits, kill switch for the demo page |
| Launches flat (no HN traction) | Medium | Low | Blog post provides independent reach. X thread + Reddit cross-posts buffer. |
| Model ID drift (Gemini `-preview`) | Medium | Medium | Phase 0.2 smoke test |
| Gemini/OpenAI CORS blocks browser calls | Low | Medium | Already using server-side proxy approach (Option C), not browser-direct |
| Secret scanning false positives on commit | Low | Low | Already passed GitHub push protection post-cleanup |
| Negative HN reception ("just another LLM wrapper") | Medium | Medium | Lead framing with engineering depth + pain story, not AI hype |
| Bot abuse of BYOK demo | Low | Low | IP rate limit, Cloudflare Turnstile if escalates |

---

## Task list (condensed, with backlog refs)

**Phase 0** — Key rotation + verification (B21) ✅ 0.2 done
**Phase 1** — Arch decisions, license, PyPI name
**Phase 2** — Repo polish (B22)
**Phase 2.5** — Sync skill + 4 new templates (NEW)
**Phase 3** — Gallery (B24) + BYOK demo (B23) + Screencast (B25)
**Phase 4** — PyPI publish (B26)
**Phase 5** — Launch execution

## Timeline (9-day plan)

| Day | Phase | Milestone |
|-----|-------|-----------|
| 1 | 0 | Keys rotated, spend caps (0.2 already done) |
| 2 | 1 + start 2 | Decisions locked, repo cleanup started |
| 3 | 2 | Repo polish done (README, license, CI) |
| 4-5 | 2.5 | Sync skill core built (Codex) + 4 new templates (Codex) |
| 6 | 2.5 + 3 | Sync skill surfaces done (CC skill, GH Action template); gallery curation starts |
| 7 | 3 | Gallery complete (17 templates × provider comparisons + sync demo GIF), screencast recorded, BYOK demo deployed |
| 8 | 4 | PyPI published, internal QA, launch copy finalized |
| 9 | 5 | Launch day (Tue or Wed) |

**Slippage tolerance:** +2 days OK. Prioritized drop order if slipping:
1. Drop `user_flow` template (P2, safe to ship in v1.1)
2. Drop BYOK demo, rely on gallery + screencast + install paths
3. Drop GitHub Action template (keep CLI + CC skill only; users can self-wire GH Action)
4. Drop sync skill → absolute last resort, defeats the positioning

**Do NOT drop:** sync skill core. It's the launch narrative. Without it, the launch is generic.

---

## Success metrics

**24 hours post-launch:**
- 50+ GH stars
- HN post above 20 points OR 15+ comments
- Zero production incidents (demo still up, no cost blowup)

**1 week:**
- 200+ GH stars
- 5+ non-trivial GitHub issues/PRs from strangers
- 1-2 pieces of inbound (job inquiry, podcast invite, collaboration ask)
- <$5 total provider cost across all demo traffic

**1 month:**
- 500+ GH stars (stretch)
- PyPI download count >1000
- Featured in at least one newsletter (DevOps'ish, Pointer, Console, etc.)
- Continued weekly commit activity (signals active project)

---

## Open questions

1. ~~**Gemini model IDs**~~ — ✅ resolved (2026-04-21): `-preview` required, config fixed
2. **Claude Code plugin marketplace** — does it exist yet in a form we can submit to, or is it still informal?
3. **Name collision** — is "Diagram Forge" clear of trademark issues? Quick search before launch.
4. **Blog hosting** — which platform? Substack reaches different audience than personal site.
5. **Logo** — skip for v0.1.0 or spend a half-day? Recommend skip.
6. **Do we include the existing Railway deploy in the launch** or just retire it silently? Recommend retire quietly, replace with Vercel Option C.
7. **Sync skill: should it use its own MCP tool or share the existing `generate_diagram`?** — Recommend a new dedicated tool (`sync_diagrams`) that takes a manifest, to keep the interaction clean.
8. **Eval framework scope at launch** — include the Tier 2 eval content in the launch, or save for the follow-up blog post? Recommend: save for follow-up to keep launch narrative focused on sync. Run Tier 2 once internally before launch as QA.

---

## Notes to self

- The code is good. Don't undersell the engineering.
- The story is real. Don't fake enthusiasm.
- HN can smell both. Be direct and honest.
- The gallery is the demo. Curate ruthlessly.
- **Sync is the story. Templates are table stakes. Don't let the narrative drift toward "another AI image tool."**
- If one piece has to slip, slip the live demo. Gallery + screencast + GH repo + PyPI + sync skill is already a strong launch.
- Respond to every HN comment for 48h. This single behavior matters.
- Use Diagram Forge on itself. Dogfood the sync skill in this very repo before launch — your own architecture diagrams should be sync-managed. That's the most credible demo there is.

---

## Related design docs

- **`docs/sync-skill-design.md`** — full implementation blueprint for the sync skill (Phase 2.5.1)
- **`docs/template-proposals.md`** — detailed specs for the 4 new templates (Phase 2.5.2)

Both authored as handoff material for CTO review and Codex implementation.
