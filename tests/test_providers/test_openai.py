"""Tests for OpenAI provider."""

from __future__ import annotations

import pytest

from diagram_forge.models import GenerationConfig, Resolution
from diagram_forge.providers.openai_provider import OpenAIProvider


class TestOpenAIProvider:
    def test_default_model(self):
        """Should return gpt-image-1 as default."""
        p = OpenAIProvider(api_key="test")
        assert "gpt-image" in p.model or "dall-e" in p.model

    def test_supported_features(self):
        """Should support generate and edit."""
        p = OpenAIProvider(api_key="test")
        features = p.supported_features()
        assert "generate" in features
        assert "edit" in features

    def test_pricing(self):
        """Should return valid pricing info."""
        p = OpenAIProvider(api_key="test")
        pricing = p.get_pricing()
        assert pricing.provider == "openai"
        assert pricing.cost_per_unit > 0

    def test_resolve_size_wide(self):
        """16:9 aspect ratio should map to 1536x1024."""
        p = OpenAIProvider(api_key="test")
        from diagram_forge.models import AspectRatio
        config = GenerationConfig(prompt="test", aspect_ratio=AspectRatio.WIDE)
        assert p._resolve_size(config) == "1536x1024"

    def test_resolve_size_square(self):
        """1:1 aspect ratio should map to 1024x1024."""
        p = OpenAIProvider(api_key="test")
        from diagram_forge.models import AspectRatio
        config = GenerationConfig(prompt="test", aspect_ratio=AspectRatio.SQUARE)
        assert p._resolve_size(config) == "1024x1024"

    def test_resolve_size_portrait(self):
        """9:16 aspect ratio should map to 1024x1536."""
        p = OpenAIProvider(api_key="test")
        from diagram_forge.models import AspectRatio
        config = GenerationConfig(prompt="test", aspect_ratio=AspectRatio.PORTRAIT)
        assert p._resolve_size(config) == "1024x1536"
