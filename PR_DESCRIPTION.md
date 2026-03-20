# PR: Community Release Readiness Hardening

## Summary

This PR prepares Diagram Forge for public/community sharing by hardening security boundaries, tightening MCP tool schemas, improving accessibility metadata, and completing release governance docs.

## What changed

### Security and safety
- Restricted local image read paths to approved roots (workspace, styles dir, output dir).
- Restricted output writes to configured output directory.
- Enforced image extension and file size checks for local reads/writes.
- Hardened Replicate downloads with HTTPS/host validation, timeout, and max size checks.
- Disabled `configure_provider` by default unless explicitly enabled with `DIAGRAM_FORGE_ENABLE_CONFIGURE_PROVIDER=1`.
- Reduced path disclosure in `list_styles` responses (`reference_file` instead of full path).

### MCP tool quality
- Tightened tool arg schemas using enums/literals and bounded numeric fields.
- Added stronger type safety across server/provider/model modules.
- Preserved existing tool behavior while improving input validation.

### Accessibility and docs
- Added `accessibility.alt_text` in `generate_diagram` responses.
- Added `SECURITY.md` and `CONTRIBUTING.md`.
- Added `docs/setup-and-customization.md` for onboarding and customization.
- Added `docs/community-evaluator-guide.md` for structured external evaluation.
- Updated README with security defaults and references to setup/customization docs.
- Corrected template count mismatch in `docs/intent.md`.

### Engineering quality
- `pytest -q` passing
- `ruff check src tests` passing
- `mypy src` passing (strict)
- `python -m build` passing (sdist + wheel)

## Risk / compatibility notes

- `configure_provider` now returns a security error unless explicitly enabled by env var.
- `generate_diagram` and `edit_diagram` now reject unsafe/unapproved paths.
- Clients relying on full style path from `list_styles` should switch to style name usage.

## Reviewer checklist

- [ ] Verify path sandbox behavior (`image_path`, `reference_images`, `output_path`) blocks unsafe paths.
- [ ] Verify `configure_provider` is disabled by default and works only when explicitly enabled.
- [ ] Verify stricter tool schemas appear in MCP inspector as expected.
- [ ] Run smoke generation + edit with at least one provider.
- [ ] Confirm `get_usage_report` still records and reports correctly.
- [ ] Validate README + new docs are sufficient for first-time evaluator onboarding.
- [ ] Confirm no regressions in plugin skill guidance.

## Manual test commands

```bash
pytest -q
ruff check src tests
mypy src
python -m build
npx @modelcontextprotocol/inspector python -m diagram_forge.server
```
