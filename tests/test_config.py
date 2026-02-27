"""Tests for configuration loading."""

from __future__ import annotations

import os

import yaml

from diagram_forge.config import load_config, resolve_api_key
from diagram_forge.models import AppConfig, ProviderConfig, ProviderName


class TestLoadConfig:
    def test_load_default_config(self):
        """Loading with default path should produce a valid AppConfig."""
        config = load_config()
        assert isinstance(config, AppConfig)
        assert config.version == 1
        assert config.default_provider == ProviderName.GEMINI

    def test_load_config_has_providers(self):
        """Default config should have all three providers."""
        config = load_config()
        assert "gemini" in config.providers
        assert "openai" in config.providers
        assert "replicate" in config.providers

    def test_load_config_from_custom_path(self, tmp_dir):
        """Loading from a custom YAML path should work."""
        custom = {
            "version": 1,
            "default_provider": "openai",
            "output_directory": str(tmp_dir / "output"),
            "styles_directory": str(tmp_dir / "styles"),
            "database_path": str(tmp_dir / "test.db"),
            "providers": {
                "openai": {
                    "enabled": True,
                    "model": "dall-e-3",
                    "api_key_env": "OPENAI_API_KEY",
                }
            },
        }
        cfg_path = tmp_dir / "test_config.yaml"
        cfg_path.write_text(yaml.dump(custom))

        config = load_config(str(cfg_path))
        assert config.default_provider == ProviderName.OPENAI
        assert "openai" in config.providers

    def test_load_nonexistent_config(self, tmp_dir):
        """Loading from nonexistent path should return defaults."""
        config = load_config(str(tmp_dir / "nonexistent.yaml"))
        assert isinstance(config, AppConfig)
        assert config.version == 1


class TestResolveApiKey:
    def test_resolve_from_explicit_key(self):
        """Explicit key takes priority."""
        pc = ProviderConfig(model="test", api_key_env="TEST_KEY")
        assert resolve_api_key(pc, explicit_key="my-key") == "my-key"

    def test_resolve_from_env(self, monkeypatch):
        """Falls back to environment variable."""
        monkeypatch.setenv("TEST_API_KEY", "env-key-123")
        pc = ProviderConfig(model="test", api_key_env="TEST_API_KEY")
        assert resolve_api_key(pc) == "env-key-123"

    def test_resolve_returns_none_when_missing(self):
        """Returns None when no key available."""
        pc = ProviderConfig(model="test", api_key_env="NONEXISTENT_KEY_12345")
        # Ensure env var doesn't exist
        os.environ.pop("NONEXISTENT_KEY_12345", None)
        assert resolve_api_key(pc) is None
