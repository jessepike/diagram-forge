"""FastMCP server with all diagram generation tools."""

from __future__ import annotations

import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, Any, Literal, cast
from uuid import UUID

from pydantic import BaseModel, Field

from diagram_forge.config import ensure_directories, load_config, resolve_api_key
from diagram_forge.cost_tracker import CostTracker
from diagram_forge.models import (
    AspectRatio,
    DiagramType,
    GenerationConfig,
    GenerationRecord,
    ProviderName,
    Resolution,
)
from diagram_forge.providers import PROVIDER_MAP, get_provider
from diagram_forge.style_manager import StyleManager
from diagram_forge.template_engine import build_prompt, load_all_templates, load_template

ProviderChoice = Literal["auto", "gemini", "openai", "replicate"]
ReportGroupBy = Literal["provider", "diagram_type", "day"]

SAFE_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_IMAGE_INPUT_BYTES = 15 * 1024 * 1024
ENABLE_CONFIGURE_PROVIDER_ENV = "DIAGRAM_FORGE_ENABLE_CONFIGURE_PROVIDER"


def _serialize(value: Any) -> Any:
    """Convert Pydantic models, dataclasses, UUIDs to JSON-serializable types."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if hasattr(value, "__dataclass_fields__"):
        d = asdict(value)
        # Remove bytes fields
        d.pop("image_data", None)
        return d
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, set):
        return sorted(value)
    return value


def _resolve_path(path: Path, *, must_exist: bool) -> Path:
    expanded = path.expanduser()
    if not expanded.is_absolute():
        expanded = Path.cwd() / expanded
    return expanded.resolve(strict=must_exist)


def _is_within_roots(path: Path, roots: list[Path]) -> bool:
    return any(path.is_relative_to(root) for root in roots)


def _validate_readable_image_path(path: Path, roots: list[Path]) -> tuple[Path | None, str | None]:
    try:
        resolved = _resolve_path(path, must_exist=True)
    except FileNotFoundError:
        return None, f"File not found: {path}"

    if not resolved.is_file():
        return None, f"Not a file: {path}"
    if resolved.suffix.lower() not in SAFE_IMAGE_EXTENSIONS:
        return None, f"Unsupported image extension for '{path}'. Allowed: {sorted(SAFE_IMAGE_EXTENSIONS)}"
    if not _is_within_roots(resolved, roots):
        return None, "Path is outside allowed read directories."
    size_bytes = resolved.stat().st_size
    if size_bytes > MAX_IMAGE_INPUT_BYTES:
        return None, f"Image exceeds max size ({MAX_IMAGE_INPUT_BYTES} bytes): {path}"
    return resolved, None


def _validate_writable_image_path(path: Path, roots: list[Path]) -> tuple[Path | None, str | None]:
    resolved = _resolve_path(path, must_exist=False)
    if resolved.suffix.lower() not in SAFE_IMAGE_EXTENSIONS:
        return None, (
            f"Unsupported output extension for '{path}'. Allowed: {sorted(SAFE_IMAGE_EXTENSIONS)}"
        )
    if not _is_within_roots(resolved, roots):
        return None, "Path is outside allowed write directories."
    return resolved, None


def _build_alt_text(diagram_type: str, prompt: str) -> str:
    """Return a simple textual fallback for screen readers and docs."""
    summary = " ".join(prompt.split())
    return f"{diagram_type} diagram. {summary[:240]}".strip()


def create_server(config_path: str | None = None) -> Any:
    """Create and configure the Diagram Forge MCP server."""
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:
        raise RuntimeError(
            "MCP dependency is unavailable. Install with: pip install 'diagram-forge[dev]'"
        ) from exc

    # Load configuration
    config = load_config(config_path)
    ensure_directories(config)

    # Initialize components
    cost_tracker = CostTracker(config.database_path)
    style_manager = StyleManager(config.styles_directory)
    output_root = _resolve_path(Path(config.output_directory), must_exist=False)
    styles_root = _resolve_path(Path(config.styles_directory), must_exist=False)
    cwd_root = Path.cwd().resolve()
    allowed_read_roots = [output_root, styles_root, cwd_root]
    allowed_write_roots = [output_root]

    # Create FastMCP instance
    app = FastMCP("diagram-forge")

    # --- Tool: generate_diagram ---

    @app.tool()
    async def generate_diagram(
        prompt: str,
        diagram_type: DiagramType = DiagramType.GENERIC,
        provider: ProviderChoice = "auto",
        model: str | None = None,
        resolution: Resolution = Resolution.RES_2K,
        aspect_ratio: AspectRatio = AspectRatio.WIDE,
        style_reference: str | None = None,
        output_path: str | None = None,
        temperature: Annotated[float, Field(ge=0.0, le=2.0)] = 1.0,
    ) -> dict[str, Any]:
        """Generate an architecture diagram from a text prompt.

        Args:
            prompt: Description of what to generate
            diagram_type: Type of diagram (architecture|data_flow|component|sequence|integration|infographic|c4_container|exec_infographic|generic)
            provider: Image generation provider (auto|gemini|openai|replicate). "auto" picks the best provider for the diagram type.
            model: Override the default model for this provider (e.g. gpt-image-1.5, gemini-3-pro-image-preview)
            resolution: Output resolution (1K|2K|4K)
            aspect_ratio: Output aspect ratio (16:9|1:1|9:16|4:3)
            style_reference: Style name or path to reference image
            output_path: Where to save the image (auto-generated if not provided)
            temperature: Generation creativity (0.0 to 2.0)
        """
        start = time.monotonic()

        diagram_type_name = diagram_type.value
        resolution_name = resolution.value
        aspect_ratio_name = aspect_ratio.value
        provider_name: str = provider

        # Auto-select provider from template recommendation
        if provider_name == "auto":
            try:
                tmpl = load_template(diagram_type_name)
                provider_name = tmpl.recommended_provider or config.default_provider.value
                if not model and tmpl.recommended_model:
                    model = tmpl.recommended_model
            except FileNotFoundError:
                provider_name = config.default_provider.value

        # Resolve provider
        provider_config = config.providers.get(provider_name)
        if not provider_config:
            return {"status": "error", "error": f"Provider '{provider_name}' not configured"}

        api_key = resolve_api_key(provider_config)
        if not api_key:
            return {
                "status": "error",
                "error": f"No API key for provider '{provider_name}'. "
                f"Set {provider_config.api_key_env} environment variable.",
            }

        # Build the full prompt from template + user prompt
        full_prompt = build_prompt(
            diagram_type=diagram_type_name,
            user_prompt=prompt,
            resolution=resolution_name,
            aspect_ratio=aspect_ratio_name,
        )

        # Resolve style reference
        style_path = None
        if style_reference:
            style = style_manager.get_style(style_reference)
            if style:
                style_path = style.path
            else:
                style_path, error = _validate_readable_image_path(
                    Path(style_reference), allowed_read_roots
                )
                if error:
                    return {"status": "error", "error": f"Invalid style_reference: {error}"}

        # Build generation config
        gen_config = GenerationConfig(
            prompt=full_prompt,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            temperature=temperature,
            style_reference_path=style_path,
        )

        # Generate
        effective_model = model or provider_config.model
        img_provider = get_provider(provider_name, api_key, model=effective_model)
        result = await img_provider.generate(gen_config)

        elapsed_ms = int((time.monotonic() - start) * 1000)

        # Save image
        saved_path = None
        if result.success and result.image_data:
            if output_path:
                save_to, error = _validate_writable_image_path(Path(output_path), allowed_write_roots)
                if error:
                    return {"status": "error", "error": f"Invalid output_path: {error}"}
                assert save_to is not None
            else:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_to = output_root / f"{diagram_type_name}_{timestamp}.png"

            save_to.parent.mkdir(parents=True, exist_ok=True)
            save_to.write_bytes(result.image_data)
            saved_path = str(save_to)
            result.output_path = saved_path

        # Track cost
        cost_tracker.record(
            GenerationRecord(
                provider=provider_name,
                model=effective_model,
                diagram_type=diagram_type_name,
                resolution=resolution_name,
                aspect_ratio=aspect_ratio_name,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
                billing_model=result.billing_model.value,
                generation_time_ms=elapsed_ms,
                success=result.success,
                output_path=saved_path,
                template_used=diagram_type_name,
                style_used=style_reference,
                error_message=result.error_message,
            )
        )

        response = cast(dict[str, Any], _serialize(result))
        response["status"] = "success" if result.success else "error"
        if saved_path:
            response["output_path"] = saved_path
        response["accessibility"] = {"alt_text": _build_alt_text(diagram_type_name, prompt)}
        return response

    # --- Tool: edit_diagram ---

    @app.tool()
    async def edit_diagram(
        image_path: str,
        prompt: str,
        provider: ProviderName = ProviderName.GEMINI,
        resolution: Resolution | None = None,
        reference_images: list[str] | None = None,
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """Edit an existing diagram based on instructions.

        Args:
            image_path: Path to the existing diagram image
            prompt: Edit instructions
            provider: Image generation provider (gemini|openai|replicate)
            resolution: Output resolution (auto-detect if not specified)
            reference_images: Additional reference image paths
            output_path: Where to save the result
        """
        start = time.monotonic()
        provider_name = provider.value

        # Load input image
        img_path, error = _validate_readable_image_path(Path(image_path), allowed_read_roots)
        if error:
            return {"status": "error", "error": f"Invalid image_path: {error}"}
        assert img_path is not None
        input_image = img_path.read_bytes()

        # Resolve provider
        provider_config = config.providers.get(provider_name)
        if not provider_config:
            return {"status": "error", "error": f"Provider '{provider_name}' not configured"}

        api_key = resolve_api_key(provider_config)
        if not api_key:
            return {
                "status": "error",
                "error": f"No API key for provider '{provider_name}'. "
                f"Set {provider_config.api_key_env} environment variable.",
            }

        # Check provider supports editing
        img_provider = get_provider(provider_name, api_key, model=provider_config.model)
        if "edit" not in img_provider.supported_features():
            return {
                "status": "error",
                "error": f"Provider '{provider_name}' does not support image editing",
            }

        # Build config
        ref_paths: list[Path] = []
        for ref in (reference_images or []):
            ref_path, ref_error = _validate_readable_image_path(Path(ref), allowed_read_roots)
            if ref_error:
                return {"status": "error", "error": f"Invalid reference_images entry '{ref}': {ref_error}"}
            assert ref_path is not None
            ref_paths.append(ref_path)
        gen_config = GenerationConfig(
            prompt=prompt,
            resolution=resolution or Resolution.RES_2K,
            reference_images=ref_paths,
        )

        result = await img_provider.edit(input_image, gen_config)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        # Save result
        saved_path = None
        if result.success and result.image_data:
            if output_path:
                save_to, save_error = _validate_writable_image_path(
                    Path(output_path), allowed_write_roots
                )
                if save_error:
                    return {"status": "error", "error": f"Invalid output_path: {save_error}"}
                assert save_to is not None
            else:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_to = output_root / f"edit_{timestamp}.png"

            save_to.parent.mkdir(parents=True, exist_ok=True)
            save_to.write_bytes(result.image_data)
            saved_path = str(save_to)

        # Track cost
        cost_tracker.record(
            GenerationRecord(
                provider=provider_name,
                model=provider_config.model,
                diagram_type="edit",
                resolution=(resolution.value if resolution else "2K"),
                cost_usd=result.cost_usd,
                billing_model=result.billing_model.value,
                generation_time_ms=elapsed_ms,
                success=result.success,
                output_path=saved_path,
                error_message=result.error_message,
            )
        )

        response = cast(dict[str, Any], _serialize(result))
        response["status"] = "success" if result.success else "error"
        if saved_path:
            response["output_path"] = saved_path
        return response

    # --- Tool: list_templates ---

    @app.tool()
    async def list_templates() -> dict[str, Any]:
        """List all available diagram templates with descriptions."""
        templates = load_all_templates()
        return {
            "status": "success",
            "templates": [
                {
                    "name": t.name,
                    "display_name": t.display_name,
                    "description": t.description,
                    "supports": t.supports,
                    "variables": t.variables,
                    "recommended_provider": t.recommended_provider,
                    "recommended_model": t.recommended_model,
                }
                for t in templates.values()
            ],
            "count": len(templates),
        }

    # --- Tool: list_providers ---

    @app.tool()
    async def list_providers() -> dict[str, Any]:
        """List configured providers with status, models, and health information."""
        providers_info = []
        for name, pconfig in config.providers.items():
            api_key = resolve_api_key(pconfig)
            has_key = bool(api_key)
            features = []
            if has_key and api_key is not None and name in PROVIDER_MAP:
                try:
                    p = get_provider(name, api_key, model=pconfig.model)
                    features = sorted(p.supported_features())
                    pricing = _serialize(p.get_pricing())
                except Exception:
                    pricing = None
            else:
                pricing = None

            providers_info.append({
                "name": name,
                "enabled": pconfig.enabled,
                "model": pconfig.model,
                "api_key_configured": has_key,
                "api_key_env": pconfig.api_key_env,
                "features": features,
                "pricing": pricing,
            })

        return {
            "status": "success",
            "providers": providers_info,
            "default_provider": config.default_provider.value,
        }

    # --- Tool: list_styles ---

    @app.tool()
    async def list_styles() -> dict[str, Any]:
        """List all available style reference images."""
        styles = style_manager.list_styles()
        return {
            "status": "success",
            "styles": [
                {
                    "name": s.name,
                    "display_name": s.display_name,
                    "description": s.description,
                    "reference_file": s.path.name,
                    "tags": s.tags,
                }
                for s in styles
            ],
            "count": len(styles),
        }

    # --- Tool: get_usage_report ---

    @app.tool()
    async def get_usage_report(
        days: Annotated[int, Field(ge=1, le=3650)] = 30,
        group_by: ReportGroupBy = "provider",
    ) -> dict[str, Any]:
        """Get usage and cost report for diagram generations.

        Args:
            days: Number of days to report on (default: 30)
            group_by: Group results by 'provider', 'diagram_type', or 'day'
        """
        report = cost_tracker.get_usage_report(days=days, group_by=group_by)
        return {
            "status": "success",
            **_serialize(report),
        }

    # --- Tool: configure_provider ---

    @app.tool()
    async def configure_provider(
        provider: ProviderName,
        api_key: str,
    ) -> dict[str, Any]:
        """Configure an API key for a provider (sets environment variable for current session).

        Args:
            provider: Provider name (gemini|openai|replicate)
            api_key: The API key to set
        """
        if os.environ.get(ENABLE_CONFIGURE_PROVIDER_ENV) != "1":
            return {
                "status": "error",
                "error": (
                    "configure_provider is disabled by default for security. "
                    "Set API keys via environment variables before launching the server. "
                    f"To enable this tool intentionally, set {ENABLE_CONFIGURE_PROVIDER_ENV}=1."
                ),
            }

        provider_name = provider.value

        provider_config = config.providers.get(provider_name)
        if not provider_config:
            return {"status": "error", "error": f"Unknown provider: {provider_name}"}

        # Set the environment variable
        os.environ[provider_config.api_key_env] = api_key

        # Verify connectivity
        try:
            img_provider = get_provider(provider_name, api_key, model=provider_config.model)
            health = await img_provider.health_check()
            return {
                "status": "success" if health.available else "warning",
                "message": f"API key set for {provider_name} ({provider_config.api_key_env})",
                "health": _serialize(health),
            }
        except Exception as e:
            return {
                "status": "warning",
                "message": f"API key set for {provider_name}, but health check failed: {e}",
            }

    return app


def main() -> None:
    """Run the Diagram Forge MCP server over stdio."""
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
