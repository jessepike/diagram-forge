"""Tests for cost tracker."""

from __future__ import annotations

import pytest

from diagram_forge.cost_tracker import CostTracker
from diagram_forge.models import GenerationRecord


class TestCostTracker:
    def test_initialize_creates_db(self, tmp_dir):
        """CostTracker should create the database file."""
        db_path = tmp_dir / "test_usage.db"
        CostTracker(db_path)
        assert db_path.exists()

    def test_record_and_report(self, tmp_dir):
        """Should record a generation and retrieve it in a report."""
        tracker = CostTracker(tmp_dir / "test.db")

        record = GenerationRecord(
            provider="gemini",
            model="gemini-2.0-flash",
            diagram_type="architecture",
            resolution="2K",
            aspect_ratio="16:9",
            cost_usd=0.039,
            billing_model="per_image",
            generation_time_ms=1500,
            success=True,
            output_path="/tmp/test.png",
            template_used="architecture",
        )
        tracker.record(record)

        report = tracker.get_usage_report(days=1)
        assert report.total_generations == 1
        assert report.successful_generations == 1
        assert report.failed_generations == 0
        assert report.total_cost_usd == 0.039

    def test_failed_generation_tracking(self, tmp_dir):
        """Should track failed generations separately."""
        tracker = CostTracker(tmp_dir / "test.db")

        tracker.record(GenerationRecord(
            provider="openai",
            model="dall-e-3",
            cost_usd=0.0,
            billing_model="per_image",
            success=False,
            error_message="API error",
        ))

        report = tracker.get_usage_report(days=1)
        assert report.total_generations == 1
        assert report.successful_generations == 0
        assert report.failed_generations == 1

    def test_group_by_provider(self, tmp_dir):
        """Report should group by provider correctly."""
        tracker = CostTracker(tmp_dir / "test.db")

        for provider, cost in [("gemini", 0.039), ("openai", 0.016), ("gemini", 0.039)]:
            tracker.record(GenerationRecord(
                provider=provider,
                model="test-model",
                cost_usd=cost,
                billing_model="per_image",
                success=True,
            ))

        report = tracker.get_usage_report(days=1, group_by="provider")
        assert report.total_generations == 3
        assert len(report.breakdown) == 2  # gemini + openai

        # Gemini should be first (higher total cost)
        gemini_row = next(r for r in report.breakdown if r["group"] == "gemini")
        assert gemini_row["count"] == 2
        assert gemini_row["cost_usd"] == pytest.approx(0.078, abs=0.001)

    def test_group_by_diagram_type(self, tmp_dir):
        """Report should group by diagram_type correctly."""
        tracker = CostTracker(tmp_dir / "test.db")

        for dtype in ["architecture", "architecture", "sequence"]:
            tracker.record(GenerationRecord(
                provider="gemini",
                model="test",
                diagram_type=dtype,
                cost_usd=0.01,
                billing_model="per_image",
                success=True,
            ))

        report = tracker.get_usage_report(days=1, group_by="diagram_type")
        assert len(report.breakdown) == 2

    def test_empty_report(self, tmp_dir):
        """Empty database should return zero counts."""
        tracker = CostTracker(tmp_dir / "test.db")
        report = tracker.get_usage_report(days=30)
        assert report.total_generations == 0
        assert report.total_cost_usd == 0.0
        assert report.breakdown == []
