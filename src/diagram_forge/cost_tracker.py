"""SQLite-backed usage and cost tracking with reporting."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from diagram_forge.models import GenerationRecord, UsageReport

SCHEMA = """
CREATE TABLE IF NOT EXISTS generations (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    diagram_type TEXT,
    resolution TEXT,
    aspect_ratio TEXT,
    tokens_used INTEGER,
    cost_usd REAL NOT NULL,
    billing_model TEXT NOT NULL,
    generation_time_ms INTEGER,
    success INTEGER NOT NULL,
    output_path TEXT,
    template_used TEXT,
    style_used TEXT,
    error_message TEXT
);
"""


class CostTracker:
    """SQLite-backed cost and usage tracker."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        """Create tables if they don't exist."""
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def record(self, record: GenerationRecord) -> None:
        """Insert a generation record."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO generations
                    (id, timestamp, provider, model, diagram_type, resolution,
                     aspect_ratio, tokens_used, cost_usd, billing_model,
                     generation_time_ms, success, output_path, template_used,
                     style_used, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(record.id),
                    record.timestamp.isoformat(),
                    record.provider,
                    record.model,
                    record.diagram_type,
                    record.resolution,
                    record.aspect_ratio,
                    record.tokens_used,
                    record.cost_usd,
                    record.billing_model,
                    record.generation_time_ms,
                    int(record.success),
                    record.output_path,
                    record.template_used,
                    record.style_used,
                    record.error_message,
                ),
            )

    def get_usage_report(
        self,
        days: int = 30,
        group_by: str = "provider",
    ) -> UsageReport:
        """Generate an aggregated usage report."""
        cutoff = datetime.now(timezone.utc).isoformat()
        # Simple approach: calculate cutoff from days
        from datetime import timedelta

        cutoff_dt = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff = cutoff_dt.isoformat()

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row

            # Totals
            row = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    COALESCE(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END), 0) as successes,
                    COALESCE(SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END), 0) as failures,
                    COALESCE(SUM(cost_usd), 0) as total_cost
                FROM generations
                WHERE timestamp >= ?
                """,
                (cutoff,),
            ).fetchone()

            total = row["total"]
            successes = row["successes"]
            failures = row["failures"]
            total_cost = row["total_cost"]

            # Breakdown
            valid_groups = {"provider", "diagram_type", "day"}
            if group_by not in valid_groups:
                group_by = "provider"

            if group_by == "day":
                group_col = "DATE(timestamp)"
            else:
                group_col = group_by

            breakdown_rows = conn.execute(
                f"""
                SELECT
                    {group_col} as group_key,
                    COUNT(*) as count,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                    COALESCE(SUM(cost_usd), 0) as cost,
                    COALESCE(AVG(generation_time_ms), 0) as avg_time_ms
                FROM generations
                WHERE timestamp >= ?
                GROUP BY {group_col}
                ORDER BY cost DESC
                """,
                (cutoff,),
            ).fetchall()

            breakdown = [
                {
                    "group": r["group_key"] or "unknown",
                    "count": r["count"],
                    "successes": r["successes"],
                    "cost_usd": round(r["cost"], 6),
                    "avg_generation_time_ms": int(r["avg_time_ms"]),
                }
                for r in breakdown_rows
            ]

        return UsageReport(
            period_days=days,
            total_generations=total,
            successful_generations=successes,
            failed_generations=failures,
            total_cost_usd=round(total_cost, 6),
            breakdown=breakdown,
        )
