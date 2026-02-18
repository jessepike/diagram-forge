# Security Policy

## Supported Versions

Only the latest release on `main` is supported for security fixes.

## Reporting a Vulnerability

Please do not open public issues for suspected vulnerabilities.

Report security issues privately to the maintainers with:
- A clear description of the issue
- Reproduction steps or proof of concept
- Expected vs. actual behavior
- Impact assessment

Include "diagram-forge security" in the subject line.

## Security Posture

Diagram Forge applies these defaults:
- Provider API keys are expected through environment variables.
- `configure_provider` is disabled by default and must be explicitly enabled.
- Local file reads are limited to image files in approved directories.
- Output writes are limited to the configured output directory.
- Replicate download URLs are validated and size-limited.

## Hardening Guidance

When deploying in shared environments:
- Run under a dedicated OS user with minimal filesystem permissions.
- Keep provider SDKs and dependencies patched.
- Rotate API keys periodically.
- Avoid enabling `configure_provider` unless required.
- Review MCP host logging settings to ensure secrets are not captured.
