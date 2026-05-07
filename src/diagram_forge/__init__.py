"""Diagram Forge — MCP server for AI-powered architecture diagram generation."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the repo root (where this package lives) so the server has
# OPENAI_API_KEY / GEMINI_API_KEY regardless of how it was launched. This
# decouples key resolution from Claude Code's MCP env-passing layer (which has
# proven brittle across CC version migrations) and lets a fresh clone work
# after `cp .env.example .env` with no further setup.
#
# Defense against CC's `${user_config.X}` substitution:
# When a Claude Code plugin .mcp.json declares `"env": {"OPENAI_API_KEY":
# "${user_config.openai_api_key}"}` and user_config storage is empty, CC sets
# the env var to an empty STRING (not unset) at spawn time. `load_dotenv()`
# defaults to `override=False`, which preserves existing values — including
# empty strings — and refuses to fill them from `.env`. Result: server
# launches with `OPENAI_API_KEY=""` despite a valid `.env` on disk. Fix:
# treat empty-string values for known keys as unset before calling dotenv.
# Real shell exports (non-empty values) are preserved.
for _var in ("OPENAI_API_KEY", "GEMINI_API_KEY"):
    if _var in os.environ and not os.environ[_var]:
        del os.environ[_var]

# Load behavior:
# - If <repo>/.env exists, fill any unset OPENAI_API_KEY / GEMINI_API_KEY.
# - If no .env exists (e.g. plugin installed via PyPI without a .env on disk),
#   load_dotenv silently no-ops; the server falls back to whatever the
#   launching env passed in.
_REPO_ENV = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_REPO_ENV if _REPO_ENV.exists() else None)

__version__ = "0.1.0"
