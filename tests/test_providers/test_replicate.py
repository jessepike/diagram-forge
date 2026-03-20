"""Tests for Replicate provider."""

from __future__ import annotations


from diagram_forge.models import AspectRatio, GenerationConfig, Resolution
from diagram_forge.providers.replicate_provider import ReplicateProvider


class TestReplicateProvider:
    def test_default_model(self):
        """Should return flux-schnell as default."""
        p = ReplicateProvider(api_key="test")
        assert "flux" in p.model

    def test_supported_features(self):
        """Should support generate only."""
        p = ReplicateProvider(api_key="test")
        features = p.supported_features()
        assert "generate" in features
        assert "edit" not in features

    def test_pricing(self):
        """Should return per-second pricing."""
        p = ReplicateProvider(api_key="test")
        pricing = p.get_pricing()
        assert pricing.provider == "replicate"
        assert pricing.billing_model.value == "per_second"

    def test_resolve_dimensions_wide(self):
        """16:9 should produce wider-than-tall dimensions."""
        p = ReplicateProvider(api_key="test")
        config = GenerationConfig(
            prompt="test",
            resolution=Resolution.RES_2K,
            aspect_ratio=AspectRatio.WIDE,
        )
        dims = p._resolve_dimensions(config)
        assert dims["width"] > dims["height"]

    def test_resolve_dimensions_portrait(self):
        """9:16 should produce taller-than-wide dimensions."""
        p = ReplicateProvider(api_key="test")
        config = GenerationConfig(
            prompt="test",
            resolution=Resolution.RES_2K,
            aspect_ratio=AspectRatio.PORTRAIT,
        )
        dims = p._resolve_dimensions(config)
        assert dims["height"] > dims["width"]

    def test_resolve_dimensions_square(self):
        """1:1 should produce equal dimensions."""
        p = ReplicateProvider(api_key="test")
        config = GenerationConfig(
            prompt="test",
            resolution=Resolution.RES_1K,
            aspect_ratio=AspectRatio.SQUARE,
        )
        dims = p._resolve_dimensions(config)
        assert dims["width"] == dims["height"]
