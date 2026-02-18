# Contributing

## Development Setup

```bash
pip install -e ".[dev]"
```

## Quality Gates

Run before opening a PR:

```bash
pytest -q
ruff check src tests
mypy src
```

## PR Expectations

- Keep changes scoped and include tests.
- Document user-facing behavior changes in `README.md`.
- Update `docs/status.md` when changing defaults (models, pricing assumptions, safety behavior).
- For security-sensitive changes, update `SECURITY.md` and include a brief threat note in the PR.

## MCP Tool Changes

When editing tool signatures or behavior:
- Prefer constrained schemas (enums/bounds) over free-form strings.
- Avoid accepting raw secrets in tool inputs.
- Validate all filesystem and network inputs.

## Accessibility

Diagram prompts should preserve legibility requirements.
If you add or modify templates, keep text-size/readability constraints explicit and maintain a textual fallback path where available.
