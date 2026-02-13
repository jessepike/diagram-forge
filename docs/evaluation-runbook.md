# Evaluation Runbook (Pre-Change Baseline)

## Goal
Establish a low-cost, repeatable baseline before changing MCP server behavior.

## Scope
- Compare currently configured models/providers for:
  - Reliability (success rate)
  - Latency
  - Estimated/actual cost
  - Prompt completeness proxy (required labels present in rendered prompt)
- Keep spend bounded.

## Benchmark Set
- File: `evals/benchmark_v1.yaml`
- Size: 6 prompts (architecture, data_flow, sequence, component, integration, infographic)
- Intended budget: <= $5 for full matrix at 1K resolution.

## Commands
Dry run first (required):

```bash
python scripts/eval_diagram_models.py --dry-run --max-cost-usd 5
```

Execute bounded run:

```bash
python scripts/eval_diagram_models.py \
  --execute \
  --providers gemini,openai \
  --resolution 1K \
  --max-cases 6 \
  --max-cost-usd 5
```

## Cost Controls
- Hard cap: `--max-cost-usd` blocks execution if estimated cost exceeds cap.
- Cheap default resolution: `1K`.
- Small fixed prompt set: 6.
- Use only 2 providers for baseline (gemini + openai).

## Output
Each run writes to:
- `evals/runs/<timestamp>/summary.json`
- Generated images in same run directory when `--execute` is used.

Key fields in `summary.json`:
- `estimated_cost_usd`
- `actual_cost_usd`
- `success_rate`
- `results[]` per provider/case

## Decision Gate (Before Any Server Change)
Use this gate on baseline results:
1. Success rate >= 0.95
2. No provider has > 2x latency of alternative with similar quality
3. Actual cost within budget target
4. No repeated failures on any diagram type

If a provider fails a gate, do not remove immediately; flag for follow-up test cycle.

## Next Step After Baseline
After MCP improvements are implemented, re-run the same benchmark unchanged and compare:
- Delta in success rate
- Delta in median latency
- Delta in cost per image

Do not change benchmark prompts during the same comparison cycle.
