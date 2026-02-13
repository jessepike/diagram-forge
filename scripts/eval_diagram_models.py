#!/usr/bin/env python3
"""Low-cost benchmark runner for Diagram Forge providers/models.

Usage examples:
  python scripts/eval_diagram_models.py --dry-run
  python scripts/eval_diagram_models.py --execute --providers gemini,openai --max-cost-usd 3
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import time
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import yaml
from PIL import Image, ImageDraw

from diagram_forge.config import load_config, resolve_api_key
from diagram_forge.models import AspectRatio, GenerationConfig, Resolution
from diagram_forge.providers import get_provider
from diagram_forge.template_engine import build_prompt


@dataclass
class EvalResult:
    case_id: str
    provider: str
    model: str
    success: bool
    elapsed_ms: int
    cost_usd: float
    output_path: str | None
    error: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run low-cost diagram model benchmark")
    parser.add_argument("--benchmark", default="evals/benchmark_v1.yaml")
    parser.add_argument("--output-dir", default="evals/runs")
    parser.add_argument("--config", default=None, help="Optional config file path")
    parser.add_argument("--providers", default="gemini,openai", help="Comma-separated providers")
    parser.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"])
    parser.add_argument("--aspect-ratio", default="16:9", choices=["16:9", "1:1", "9:16", "4:3"])
    parser.add_argument("--max-cases", type=int, default=6)
    parser.add_argument("--max-cost-usd", type=float, default=5.0)
    parser.add_argument("--prompt-file", default=None, help="Path to a markdown/text file to use as a single benchmark case")
    parser.add_argument("--diagram-type", default="architecture", choices=["architecture", "data_flow", "component", "sequence", "integration", "infographic", "generic"])
    parser.add_argument("--execute", action="store_true", help="Actually call providers")
    parser.add_argument("--dry-run", action="store_true", help="Plan-only mode")
    return parser.parse_args()


def _safe_model_label(model: str) -> str:
    """Convert model id to filesystem-safe label."""
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", model)


def _stamp_model_label(image_data: bytes, provider_name: str, model: str) -> bytes:
    """Stamp provider/model label onto generated image for side-by-side comparison."""
    label = f"{provider_name}/{model}"
    with Image.open(BytesIO(image_data)) as img:
        image = img.convert("RGBA")
        draw = ImageDraw.Draw(image, "RGBA")
        text_x, text_y = 14, 14
        box_w = max(180, int(len(label) * 8.5))
        box_h = 30
        draw.rectangle(
            [(text_x - 8, text_y - 6), (text_x - 8 + box_w, text_y - 6 + box_h)],
            fill=(0, 0, 0, 150),
        )
        draw.text((text_x, text_y), label, fill=(255, 255, 255, 255))
        out = BytesIO()
        image.convert("RGB").save(out, format="PNG")
        return out.getvalue()


def load_benchmark(path: str) -> dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def estimate_case_cost(provider_name: str, resolution: str) -> float:
    if provider_name == "gemini":
        return 0.039
    if provider_name == "openai":
        return 0.011 if resolution == "1K" else 0.016
    if provider_name == "replicate":
        return 0.006
    return 0.05


def quick_label_score(prompt_case: dict[str, Any], used_prompt: str) -> float:
    must = [x.lower() for x in prompt_case.get("must_include_labels", [])]
    if not must:
        return 1.0
    text = used_prompt.lower()
    hits = sum(1 for x in must if x in text)
    return round(hits / len(must), 3)


async def run_case(
    provider_name: str,
    model: str,
    api_key: str,
    case: dict[str, Any],
    output_dir: Path,
    resolution: str,
    aspect_ratio: str,
    execute: bool,
) -> EvalResult:
    case_id = case["id"]
    full_prompt = build_prompt(
        diagram_type=case["diagram_type"],
        user_prompt=case["prompt"],
        resolution=resolution,
        aspect_ratio=aspect_ratio,
    )

    if not execute:
        return EvalResult(
            case_id=case_id,
            provider=provider_name,
            model=model,
            success=True,
            elapsed_ms=0,
            cost_usd=estimate_case_cost(provider_name, resolution),
            output_path=None,
            error=None,
        )

    provider = get_provider(provider_name, api_key, model=model)
    cfg = GenerationConfig(
        prompt=full_prompt,
        resolution=Resolution(resolution),
        aspect_ratio=AspectRatio(aspect_ratio),
        temperature=0.3,
    )

    start = time.monotonic()
    result = await provider.generate(cfg)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    output_path: str | None = None
    if result.success and result.image_data:
        stamped = _stamp_model_label(result.image_data, provider_name, model)
        model_label = _safe_model_label(model)
        fname = f"{provider_name}__{model_label}__{case_id}.png"
        path = output_dir / fname
        path.write_bytes(stamped)
        output_path = str(path)

    return EvalResult(
        case_id=case_id,
        provider=provider_name,
        model=model,
        success=result.success,
        elapsed_ms=elapsed_ms,
        cost_usd=result.cost_usd,
        output_path=output_path,
        error=result.error_message,
    )


async def main() -> int:
    args = parse_args()
    execute = args.execute and not args.dry_run

    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if not prompt_path.exists():
            print(f"Prompt file not found: {prompt_path}")
            return 1
        prompt_text = prompt_path.read_text()
        benchmark = {"name": "prompt-file-benchmark", "prompts": [{
            "id": prompt_path.stem,
            "diagram_type": args.diagram_type,
            "prompt": (
                "Create an enterprise-grade technical diagram from this source document. "
                "Preserve component names and relationships exactly. Ensure text is legible.\n\n"
                f"SOURCE DOCUMENT:\n{prompt_text}"
            ),
            "must_include_labels": [],
        }]}
    else:
        benchmark = load_benchmark(args.benchmark)

    cases = (benchmark.get("prompts") or [])[: args.max_cases]
    if not cases:
        print("No benchmark cases found")
        return 1

    config = load_config(args.config)
    providers = [p.strip() for p in args.providers.split(",") if p.strip()]

    matrix: list[tuple[str, str, str]] = []
    for provider_name in providers:
        pconfig = config.providers.get(provider_name)
        if not pconfig:
            print(f"Skipping unconfigured provider: {provider_name}")
            continue
        api_key = resolve_api_key(pconfig) or ""
        if execute and not api_key:
            print(f"Skipping {provider_name}: missing API key ({pconfig.api_key_env})")
            continue
        matrix.append((provider_name, pconfig.model, api_key))

    if not matrix:
        print("No runnable providers in matrix")
        return 1

    estimated_total = 0.0
    for provider_name, _, _ in matrix:
        for _ in cases:
            estimated_total += estimate_case_cost(provider_name, args.resolution)

    print(f"Estimated benchmark cost: ${estimated_total:.3f}")
    if estimated_total > args.max_cost_usd:
        print(f"Refusing to run: estimated cost ${estimated_total:.3f} exceeds cap ${args.max_cost_usd:.2f}")
        return 2

    ts = time.strftime("%Y%m%d_%H%M%S")
    run_dir = Path(args.output_dir) / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    results: list[EvalResult] = []
    for provider_name, model, api_key in matrix:
        for case in cases:
            r = await run_case(
                provider_name=provider_name,
                model=model,
                api_key=api_key,
                case=case,
                output_dir=run_dir,
                resolution=args.resolution,
                aspect_ratio=args.aspect_ratio,
                execute=execute,
            )
            results.append(r)
            status = "ok" if r.success else "fail"
            print(f"[{status}] {provider_name} {case['id']} cost=${r.cost_usd:.4f} t={r.elapsed_ms}ms")

    # Lightweight prompt-completeness score from required labels in prompt text.
    # This is pre-change baseline only; post-change add OCR/image-based scoring.
    prompt_scores = {}
    for case in cases:
        used_prompt = build_prompt(
            diagram_type=case["diagram_type"],
            user_prompt=case["prompt"],
            resolution=args.resolution,
            aspect_ratio=args.aspect_ratio,
        )
        prompt_scores[case["id"]] = quick_label_score(case, used_prompt)

    total_cost = round(sum(r.cost_usd for r in results), 6)
    success_rate = round(sum(1 for r in results if r.success) / max(len(results), 1), 3)

    summary = {
        "run_timestamp": ts,
        "execute": execute,
        "providers": providers,
        "resolution": args.resolution,
        "aspect_ratio": args.aspect_ratio,
        "max_cases": args.max_cases,
        "estimated_cost_usd": round(estimated_total, 6),
        "actual_cost_usd": total_cost,
        "success_rate": success_rate,
        "prompt_completeness_scores": prompt_scores,
        "results": [asdict(r) for r in results],
    }

    out_file = run_dir / "summary.json"
    out_file.write_text(json.dumps(summary, indent=2))
    print(f"Saved: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
