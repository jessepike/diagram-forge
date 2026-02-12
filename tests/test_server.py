"""Tests for the MCP server creation and tool registration."""

from __future__ import annotations

import pytest

from diagram_forge.server import create_server, _serialize
from diagram_forge.models import UsageReport


class TestSerialize:
    def test_serialize_pydantic_model(self):
        """Should convert Pydantic models to dicts."""
        report = UsageReport(period_days=30, total_generations=5, total_cost_usd=0.195)
        result = _serialize(report)
        assert isinstance(result, dict)
        assert result["period_days"] == 30
        assert result["total_generations"] == 5

    def test_serialize_list(self):
        """Should recursively serialize lists."""
        result = _serialize([1, "two", {"three": 3}])
        assert result == [1, "two", {"three": 3}]

    def test_serialize_dict(self):
        """Should recursively serialize dicts."""
        result = _serialize({"key": "value", "num": 42})
        assert result == {"key": "value", "num": 42}

    def test_serialize_uuid(self):
        """Should convert UUIDs to strings."""
        from uuid import uuid4
        u = uuid4()
        result = _serialize(u)
        assert isinstance(result, str)
        assert result == str(u)

    def test_serialize_path(self):
        """Should convert Paths to strings."""
        from pathlib import Path
        p = Path("/tmp/test.png")
        result = _serialize(p)
        assert result == "/tmp/test.png"

    def test_serialize_set(self):
        """Should convert sets to sorted lists."""
        result = _serialize({"c", "a", "b"})
        assert result == ["a", "b", "c"]


class TestCreateServer:
    def test_create_server_returns_app(self):
        """create_server should return a FastMCP instance."""
        app = create_server()
        assert app is not None
        assert hasattr(app, "run")

    def test_create_server_with_custom_config(self, tmp_dir):
        """Should accept a custom config path."""
        import yaml
        cfg = {
            "version": 1,
            "default_provider": "gemini",
            "output_directory": str(tmp_dir / "output"),
            "styles_directory": str(tmp_dir / "styles"),
            "database_path": str(tmp_dir / "test.db"),
            "providers": {
                "gemini": {
                    "enabled": True,
                    "model": "test-model",
                    "api_key_env": "TEST_GEMINI_KEY",
                }
            },
        }
        cfg_path = tmp_dir / "config.yaml"
        cfg_path.write_text(yaml.dump(cfg))

        app = create_server(config_path=str(cfg_path))
        assert app is not None


class TestServerImport:
    def test_smoke_import(self):
        """Basic smoke test: server module should import cleanly."""
        from diagram_forge.server import create_server, main
        assert callable(create_server)
        assert callable(main)

    def test_providers_import(self):
        """Provider registry should import cleanly."""
        from diagram_forge.providers import PROVIDER_MAP, get_provider
        assert "gemini" in PROVIDER_MAP
        assert "openai" in PROVIDER_MAP
        assert "replicate" in PROVIDER_MAP

    def test_models_import(self):
        """All models should import cleanly."""
        from diagram_forge.models import (
            DiagramType,
            ProviderName,
            Resolution,
            AspectRatio,
            GenerationConfig,
            GenerationResult,
            AppConfig,
        )
        assert DiagramType.ARCHITECTURE.value == "architecture"
        assert ProviderName.GEMINI.value == "gemini"
        assert Resolution.RES_2K.value == "2K"
