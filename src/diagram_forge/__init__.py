"""Diagram Forge — MCP server for AI-powered architecture diagram generation."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# Load .env from the repo root (where this package lives) so the server has
# OPENAI_API_KEY / GEMINI_API_KEY regardless of how it was launched. This
# decouples key resolution from Claude Code's MCP env-passing layer (which has
# proven brittle across CC version migrations) and lets a fresh clone work
# after `cp .env.example .env` with no further setup.
#
# Behavior:
# - If <repo>/.env exists, those values are loaded (without overriding any
#   variables the launching shell already exported — `override=False` default).
# - If no .env exists (e.g. plugin installed via PyPI without a .env on disk),
#   load_dotenv silently no-ops; the server still falls back to whatever the
#   launching env passed in.
_REPO_ENV = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_REPO_ENV if _REPO_ENV.exists() else None)

__version__ = "0.1.0"
