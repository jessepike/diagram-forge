"""Tests for OpenAI provider."""

from __future__ import annotations

import pytest

from diagram_forge.models import GenerationConfig, Resolution
from diagram_forge.providers.openai_provider import OpenAIProvider


class TestOpenAIProvider:
    def test_default_model(self):
        """Should return gpt-image-2 as default."""
        p = OpenAIProvider(api_key="test")
        assert p.model == "gpt-image-2-2026-04-21"
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

    def test_cost_tiers_gpt_image_2(self):
        """gpt-image-2 cost should scale with quality tier."""
        p = OpenAIProvider(api_key="test", model="gpt-image-2-2026-04-21")
        low = p._estimate_cost("1536x1024", "low")
        medium = p._estimate_cost("1536x1024", "medium")
        high = p._estimate_cost("1536x1024", "high")
        assert low == 0.005
        assert medium == 0.041
        assert high == 0.165
        # auto should estimate at medium.
        assert p._estimate_cost("1536x1024", "auto") == medium

    def test_cost_tiers_gpt_image_1_mini(self):
        """gpt-image-1-mini should be cheaper than gpt-image-2 at medium/high."""
        mini = OpenAIProvider(api_key="test", model="gpt-image-1-mini")
        full = OpenAIProvider(api_key="test", model="gpt-image-2-2026-04-21")
        assert mini._estimate_cost("1536x1024", "medium") < full._estimate_cost("1536x1024", "medium")
        assert mini._estimate_cost("1536x1024", "high") < full._estimate_cost("1536x1024", "high")

    def test_supports_quality(self):
        """Only gpt-image-2 and -mini accept the quality parameter."""
        assert OpenAIProvider(api_key="t", model="gpt-image-2-2026-04-21")._supports_quality()
        assert OpenAIProvider(api_key="t", model="gpt-image-1-mini")._supports_quality()
        assert not OpenAIProvider(api_key="t", model="gpt-image-1.5")._supports_quality()
        assert not OpenAIProvider(api_key="t", model="dall-e-3")._supports_quality()

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
