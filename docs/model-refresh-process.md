# Model Refresh Process

## Objective
Keep model choice current as availability, capability, and pricing change, without destabilizing production behavior.

## Cadence
- Weekly light check (15 minutes)
- Monthly full benchmark run
- Ad-hoc run when a provider announces major image model update

## Standard Process
1. Refresh model/pricing inputs
2. Run low-cost baseline benchmark
3. Review against decision criteria
4. Decide: keep current defaults, trial candidate, or switch
5. Record decision in `docs/status.md`

## Step 1: Refresh Inputs
Use official provider docs/API dashboards for:
- Model availability
- Deprecations
- Pricing changes
- Feature changes (editing, multi-image, higher resolution)

Update files:
- `config/default_config.yaml` (candidate model IDs)
- `config/pricing.yaml` (cost assumptions)

Create a short changelog note in `docs/status.md` with date.

## Step 2: Run Benchmark
Always run dry run first:

```bash
python scripts/eval_diagram_models.py --dry-run --max-cost-usd 5
```

Then run execute mode with budget cap.

## Decision Criteria
Score each candidate on four dimensions:
1. Quality proxy: success rate + visual spot check of 6 outputs
2. Accuracy proxy: labels/components requested appear and are legible
3. Consistency: repeated runs do not drift significantly
4. Cost: within target per-image budget for your tier

Recommended tiering:
- Fast/economy default for iteration
- Balanced default for production docs
- Premium opt-in for executive/marketing visuals

## Change Warrant Rules
A model switch is warranted when one of these is true:
1. >= 20% lower cost at similar quality/latency
2. >= 10% higher success rate at similar cost
3. Current model has deprecation risk or frequent failures
4. New required capability is unavailable in current default

## Operational Guardrails
- Never switch defaults from a single run.
- Require at least 2 benchmark runs on separate days.
- Keep old model as fallback for one release cycle.
- If failure rate spikes post-switch, roll back default model immediately.

## Suggested Ownership
- One maintainer owns weekly checks
- One reviewer approves default model changes
- Decision log is mandatory in `docs/status.md`
