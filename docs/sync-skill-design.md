# Diagram Forge — Sync Skill Design

**Status:** Design proposal. Authored by Forge, pending CTO review + Codex implementation.
**Goal:** Automatically regenerate diagrams when the source documents they depend on change. "Living diagrams."
**Why it matters:** This is the feature that differentiates Diagram Forge from every other AI image generator. Every engineer has shipped a diagram that rotted within a month — this solves it.

---

## Concept

A repo declares which diagrams depend on which source files via a manifest. When sources change, dependent diagrams are marked stale and can be regenerated with one command — locally via CLI, interactively via Claude Code, or automatically via GitHub Actions.

Three invocation surfaces:
- **Claude Code slash command:** `/diagrams-sync` — interactive, inline with developer workflow
- **CLI:** `diagram-forge sync` — for non-Claude workflows, scripts, CI
- **GitHub Action:** regenerate on push, open PR with updated diagrams

---

## Artifacts

### 1. `diagrams.yaml` — the manifest (repo root)

```yaml
version: 1

defaults:
  provider: auto        # auto | openai | openai_mini | gemini | gemini_flash_31
  quality: auto         # auto | low | medium | high — inherits template's recommended_quality
  resolution: 2K
  aspect_ratio: 16:9
  output_dir: diagrams/
  prompt_strategy: hybrid    # raw | summarize | structured | manual | hybrid

diagrams:
  architecture:
    template: architecture
    sources:
      - docs/architecture.md
      - docs/services.md
    output: diagrams/architecture.png
    quality: high                # override default
    # Optional: extra prompt context injected before source content
    prompt_context: |
      System has 5 services: api, worker, scheduler, notifier, web.
      All behind an nginx load balancer.

  data_flow:
    template: data_flow
    sources:
      - docs/pipelines.md
    output: diagrams/data-flow.png

  product_roadmap:
    template: product_roadmap
    sources:
      - BACKLOG.md
      - docs/roadmap.md
    output: diagrams/roadmap.png
    prompt_strategy: summarize   # long source → summarize first
```

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `template` | yes | One of the bundled diagram templates |
| `sources` | yes | List of file paths whose content feeds (or influences) the diagram |
| `output` | yes | Where to write the PNG |
| `quality` / `provider` / `model` / `resolution` / `aspect_ratio` | no | Per-diagram override of defaults |
| `prompt_context` | no | Extra prompt content injected verbatim |
| `prompt_strategy` | no | How to turn sources into prompt (see below) |
| `style_reference` | no | Style reference name or file path |

### 2. `.diagram-forge/state.json` — state tracking

```json
{
  "version": 1,
  "diagrams": {
    "architecture": {
      "last_regenerated": "2026-04-21T15:42:00Z",
      "source_hashes": {
        "docs/architecture.md": "sha256:abc123...",
        "docs/services.md": "sha256:def456..."
      },
      "manifest_hash": "sha256:789xyz...",
      "cost_usd": 0.041,
      "model": "gpt-image-2-2026-04-21",
      "provider": "openai",
      "quality": "high",
      "output": "diagrams/architecture.png"
    }
  }
}
```

The state file is **gitignored** (per-contributor state). Diagrams themselves ARE committed to the repo — that's the whole point.

---

## Staleness detection

A diagram is **stale** if any of:
1. It doesn't exist on disk at its declared `output` path
2. Any of its `sources` has a hash different from what's recorded in `state.json`
3. Its manifest entry (template, provider, quality, prompt_context, etc.) has changed since last regenerate
4. It's not present in `state.json` at all (first-time sync)

Hash algorithm: SHA-256 of file contents. Fast, standard, collision-resistant.

---

## Prompt strategies

The hardest design question: how do we turn arbitrary source docs into a prompt the image model can use?

### `raw` — concatenate sources verbatim
- Works for: short, tightly-scoped markdown with explicit structure
- Breaks for: anything >~1500 tokens of source

### `summarize` — LLM summary pass before generation
- Uses Claude Haiku or Sonnet to summarize sources into a diagram-ready description
- Cost: +$0.01-0.05 per regenerate for the summary LLM call
- Quality: much better on long source docs
- Implementation: new `src/diagram_forge/prompt_strategies/summarize.py` that takes sources + template spec, returns summary

### `structured` — extract from frontmatter/embedded YAML
- Source docs contain explicit diagram data blocks:
  ```markdown
  # Architecture

  <!-- diagram-data: architecture.png -->
  ```yaml
  services:
    - name: api
      type: web
      depends_on: [database, cache]
    - name: worker
      type: background
      depends_on: [queue]
  ```
  <!-- /diagram-data -->
  ```
- Template renders from structured data rather than prose
- Most reliable, requires source-doc discipline
- Opt-in per-diagram

### `manual` — ignore source content, use `prompt_context` only
- Sources are change triggers only; diagram is regenerated from a fixed prompt
- Useful when the diagram is about the repo state broadly, not the specific content of a file
- Example: "regenerate this architecture diagram whenever ANY file in `src/` changes"

### `hybrid` (recommended default)
- If total source token count < 1500: use `raw`
- Else: use `summarize`
- Deterministic behavior: if the user wants control, they set the strategy explicitly

---

## CLI command shape

```bash
# Check status (no mutations, no cost)
diagram-forge sync
# → Prints: "3 stale diagrams, estimated cost $0.12. Run with --apply to regenerate."

# Apply changes
diagram-forge sync --apply
# → Regenerates stale diagrams, updates state.json

# Cost-capped apply
diagram-forge sync --apply --budget 0.50
# → Won't spend more than $0.50; stops partway and reports what was regenerated

# Selective
diagram-forge sync --apply --only architecture,data_flow
# → Only those diagrams, even if others are also stale

# Force (regenerate everything, bypass staleness check)
diagram-forge sync --apply --force

# Dry run (show what would happen, no cost)
diagram-forge sync --apply --dry-run

# Watch mode (daemon)
diagram-forge sync --watch
# → fswatch/watchdog on source files; regenerates on save; runs in foreground

# Initialize manifest (scaffold)
diagram-forge sync init
# → Creates diagrams.yaml with examples based on detected docs
```

**Exit codes:**
- `0` — success (or no stale diagrams)
- `1` — user error (bad manifest, bad args)
- `2` — provider error (auth, rate limit)
- `3` — partial success (some regenerated, some failed)
- `4` — budget exhausted before completion

---

## Claude Code skill integration

New skill at `diagram-forge-plugin/skills/sync/SKILL.md`:

```yaml
---
name: diagrams-sync
description: Use when the user wants to regenerate stale diagrams after editing source docs, check which diagrams are out of date, or set up automatic diagram regeneration. Triggers on phrases like "regenerate diagrams", "update diagrams", "are my diagrams current", "sync diagrams", "diagram-forge sync".
---
```

The skill body describes:
1. How to read `diagrams.yaml`
2. How to run `diagram-forge sync` to check status
3. How to preview cost before regenerating
4. How to interpret the output
5. When to ask user for budget cap vs proceed

**Auto-trigger candidate (PostToolUse hook):**
After a Write or Edit to any file listed in any diagram's `sources`, surface a notification: *"3 diagrams depend on this file. Run /diagrams-sync to check status."*

---

## GitHub Action

`.github/workflows/diagrams-sync.yml`:

```yaml
name: Regenerate Diagrams
on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'diagrams.yaml'
      - '**/*.md'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install diagram-forge
      - name: Sync diagrams
        run: diagram-forge sync --apply --budget 1.00
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      - name: Open PR with regenerated diagrams
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "chore(diagrams): regenerate stale diagrams"
          title: "chore(diagrams): regenerate stale diagrams"
          body: |
            Automatic diagram regeneration triggered by docs changes.
            See workflow run for cost breakdown.
          branch: auto/diagrams-sync
          base: main
```

---

## Implementation plan

Total effort: **~10 hours** end-to-end.

| # | Task | Effort | Owner | Files |
|---|------|--------|-------|-------|
| 1 | Manifest schema in Pydantic | 1h | Codex | `src/diagram_forge/models.py` — `DiagramManifest`, `DiagramSpec` |
| 2 | Manifest loader + validator | 1h | Codex | `src/diagram_forge/sync/manifest.py` |
| 3 | Hash + state tracking | 1h | Codex | `src/diagram_forge/sync/state.py` |
| 4 | Staleness detection | 1h | Codex | `src/diagram_forge/sync/detect.py` |
| 5 | Prompt strategies (raw + hybrid first; summarize + structured later) | 2h | Codex | `src/diagram_forge/sync/strategies.py` |
| 6 | CLI `sync` subcommand (Click or Typer) | 2h | Codex | `src/diagram_forge/cli.py` (new) |
| 7 | Claude Code skill + slash command | 1h | Forge | `diagram-forge-plugin/skills/sync/`, `diagram-forge-plugin/commands/sync.md` |
| 8 | GitHub Action template | 0.5h | Forge | `.github/workflow-templates/diagrams-sync.yml` (shipped as user-copy-paste, not auto-run in own repo) |
| 9 | Unit tests | 1.5h | Codex | `tests/test_sync/` |
| 10 | Docs + example | 1h | Forge | README section, example repo |

Suggested order: 1→2→3→4→5→6→9 (build core), then 7→8→10 (surfaces + docs).

---

## Open design questions (for CTO)

1. **Prompt strategy default** — `hybrid` as recommended, or should it be explicit/required per diagram? Trade-off: hybrid is more ergonomic but less predictable; explicit is more predictable but more boilerplate.

2. **Summarize LLM choice** — Claude Haiku for cost, Sonnet for quality. Recommend Haiku by default with Sonnet opt-in per diagram.

3. **GitHub Action: regenerate all, or only stale?** — Full repo sync catches cases where state.json drifted. But it's more expensive. Recommend: Action runs with `--apply` (not `--force`), so it regenerates stale only. If state.json is out-of-date, contributors run `sync --force` locally.

4. **Concurrency** — should `sync --apply` parallelize regenerations? 3-5 diagrams could run concurrently against provider rate limits. Recommend: yes, configurable `--concurrency N` flag, default 3.

5. **Manifest-change detection** — hashing the full manifest entry per diagram. But what if only `prompt_context` changes? That's technically a manifest change but not a source change. Should both trigger regeneration? Recommend: yes — any change to the diagram's spec triggers regenerate.

6. **Template changes** — if a bundled template YAML changes (e.g., we upgrade the architecture template from v2 to v3), should all diagrams using it regenerate? Challenging to detect without recording template version per diagram in state.json. Recommend: record `template_version` in state; regenerate if version changed.

7. **Cost preview accuracy** — we can estimate cost at the template's `recommended_quality`, but the actual cost depends on resolved quality + actual size. Recommend: use recommended_quality for estimate, show range ($0.005-$0.165 for gpt-image-2) when quality is `auto`.

8. **Watch mode — what about .gitignored files?** — if a diagram's source is `docs/secrets.md` (gitignored), it's a user-local diagram. Should watch mode still track it? Recommend: yes, watch mode is local-scope, honors the manifest regardless of gitignore.

---

## What this enables (positioning)

Once shipped, the one-line pitch becomes:

> *"Architecture diagrams that stay in sync with your docs. Change the source, the diagrams regenerate."*

That's a category. "Living diagrams" as a concept doesn't exist in the market. Own it.

**Corollary:** Everything else in Diagram Forge (templates, style references, multi-provider) becomes supporting evidence for the living-diagrams pitch, not competing concepts.
