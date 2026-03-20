# Community Evaluator Guide

Use this guide when evaluating Diagram Forge for adoption.

## Evaluation goals

Validate four areas:
1. Output quality and legibility
2. Reliability across providers
3. Cost transparency
4. Security defaults and operational safety

## Prerequisites

- Python 3.11+
- At least one provider API key
- MCP host (Claude Code, Claude Desktop, Codex CLI, or Gemini CLI)

## Quick smoke test

1. Run server via stdio transport.
2. Call `list_providers` and confirm at least one `api_key_configured=true`.
3. Call `list_templates` and confirm 9 templates load.
4. Generate one architecture diagram.
5. Run one `edit_diagram` iteration.
6. Call `get_usage_report` and verify cost entries exist.

## Suggested evaluation matrix

Run at least 6 scenarios:
- architecture (layered)
- data_flow
- sequence
- component
- integration
- exec_infographic

For each scenario, score 1-5:
- visual hierarchy
- text legibility
- semantic color clarity
- structural correctness vs prompt
- editability (for providers supporting edit)

## Reliability and cost checks

Use benchmark tooling:

```bash
python scripts/eval_diagram_models.py --dry-run --max-cost-usd 5
python scripts/eval_diagram_models.py --execute --providers gemini,openai --resolution 1K --max-cases 6 --max-cost-usd 5
```

Review `evals/runs/<timestamp>/summary.json` for:
- success_rate
- latency patterns
- actual_cost_usd

## Security checks

Verify expected failures:
- attempt `output_path` outside configured output directory -> should fail
- attempt `image_path` from arbitrary non-allowed location -> should fail
- call `configure_provider` without enabling env flag -> should fail with security message

## Accessibility checks

For generated outputs:
- check text readability at normal zoom
- verify color usage encodes meaning (not decorative only)
- verify returned tool payload includes `accessibility.alt_text`

## What to report

When sharing feedback, include:
- provider + model used
- prompt(s)
- generated output path(s)
- success/failure behavior
- cost report snippet
- screenshots for quality concerns
- any unexpected security/access behavior

## Pass criteria for publish confidence

- No high-severity security regressions
- >= 95% success on benchmark matrix
- Readable labels in all baseline outputs
- Clear installation/configuration path for first-time users
- Lint/tests/type-check all green in CI-equivalent run
