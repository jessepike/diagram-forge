"""Configuration loading: YAML + env vars + Pydantic validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from diagram_forge.models import AppConfig, ProviderConfig

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "default_config.yaml"


def load_config(config_path: str | Path | None = None) -> AppConfig:
    """Load configuration from YAML file with env var resolution.

    Priority: explicit config_path > DIAGRAM_FORGE_CONFIG env > default_config.yaml
    """
    if config_path is None:
        config_path = os.environ.get("DIAGRAM_FORGE_CONFIG", str(DEFAULT_CONFIG_PATH))

    path = Path(config_path).expanduser()
    raw: dict[str, Any]

    if path.exists():
        with open(path) as f:
            loaded = yaml.safe_load(f) or {}
            raw = loaded if isinstance(loaded, dict) else {}
    else:
        raw = {}

    # Parse providers section into ProviderConfig objects
    providers_raw = raw.pop("providers", {})
    providers: dict[str, ProviderConfig] = {}
    for name, cfg in providers_raw.items():
        if isinstance(cfg, dict):
            providers[name] = ProviderConfig(**cfg)

    return AppConfig(providers=providers, **raw)


def resolve_api_key(provider_config: ProviderConfig, explicit_key: str | None = None) -> str | None:
    """Resolve API key from explicit value or environment variable."""
    if explicit_key:
        return explicit_key
    return os.environ.get(provider_config.api_key_env)


def ensure_directories(config: AppConfig) -> None:
    """Create output and styles directories if they don't exist."""
    Path(config.output_directory).expanduser().mkdir(parents=True, exist_ok=True)
    Path(config.styles_directory).expanduser().mkdir(parents=True, exist_ok=True)
    Path(config.database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
