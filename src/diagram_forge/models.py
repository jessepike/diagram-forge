"""Pydantic v2 models for Diagram Forge."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- Enums ---


class DiagramType(str, Enum):
    """Supported diagram types."""

    ARCHITECTURE = "architecture"
    DATA_FLOW = "data_flow"
    COMPONENT = "component"
    SEQUENCE = "sequence"
    INTEGRATION = "integration"
    INFOGRAPHIC = "infographic"
    C4_CONTAINER = "c4_container"
    EXEC_INFOGRAPHIC = "exec_infographic"
    GENERIC = "generic"


class ProviderName(str, Enum):
    """Supported image generation providers."""

    GEMINI = "gemini"
    OPENAI = "openai"
    REPLICATE = "replicate"


class Resolution(str, Enum):
    """Output resolution presets."""

    RES_1K = "1K"
    RES_2K = "2K"
    RES_4K = "4K"

    @property
    def dimensions(self) -> tuple[int, int]:
        """Return (width, height) for 16:9 aspect ratio."""
        return {
            "1K": (1024, 576),
            "2K": (2048, 1152),
            "4K": (4096, 2304),
        }[self.value]


class AspectRatio(str, Enum):
    """Supported aspect ratios."""

    WIDE = "16:9"
    SQUARE = "1:1"
    PORTRAIT = "9:16"
    STANDARD = "4:3"


class BillingModel(str, Enum):
    """How a provider charges."""

    PER_IMAGE = "per_image"
    PER_TOKEN = "per_token"
    PER_SECOND = "per_second"


# --- Generation Config ---


class GenerationConfig(BaseModel):
    """Configuration passed to providers for image generation."""

    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1)
    resolution: Resolution = Resolution.RES_2K
    aspect_ratio: AspectRatio = AspectRatio.WIDE
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    style_reference_path: Path | None = None
    output_path: Path | None = None
    reference_images: list[Path] = Field(default_factory=list)


# --- Generation Result ---


@dataclass
class GenerationResult:
    """Result from a provider generation/edit call."""

    success: bool
    image_data: bytes | None = None
    output_path: str | None = None
    model_used: str = ""
    tokens_used: int | None = None
    cost_usd: float = 0.0
    billing_model: BillingModel = BillingModel.PER_IMAGE
    generation_time_ms: int = 0
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderHealth:
    """Result of a provider health check."""

    available: bool
    provider: str = ""
    model: str = ""
    message: str = ""
    latency_ms: int = 0


@dataclass
class PricingInfo:
    """Pricing details for a provider."""

    provider: str
    model: str
    billing_model: BillingModel
    cost_per_unit: float
    unit_description: str
    currency: str = "USD"


# --- Template Models ---


class TemplateColorPalette(BaseModel):
    """Color palette for a template."""

    model_config = ConfigDict(extra="allow")


class TemplateColorSystem(BaseModel):
    """Color system definition for templates."""

    model_config = ConfigDict(extra="forbid")

    description: str = ""
    palette: dict[str, str] = Field(default_factory=dict)


class TemplateStyleDefaults(BaseModel):
    """Default style settings for a template."""

    model_config = ConfigDict(extra="allow")

    background: str = "white"
    font: str = "sans-serif"
    corners: str = "slightly rounded"
    borders: str = "black"
    aspect_ratio: str = "16:9"


class TemplateVariable(BaseModel):
    """A variable in a template prompt."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    required: bool = True
    default: str | None = None


class DiagramTemplate(BaseModel):
    """A YAML-loaded diagram template."""

    model_config = ConfigDict(extra="forbid")

    name: str
    display_name: str
    description: str
    version: str = "1.0"
    supports: list[str] = Field(default_factory=list)
    style_defaults: TemplateStyleDefaults = Field(default_factory=TemplateStyleDefaults)
    color_system: TemplateColorSystem | None = None
    recommended_provider: str | None = None
    recommended_model: str | None = None
    prompt_template: str
    variables: dict[str, str] = Field(default_factory=dict)


# --- Style Models ---


class StyleReference(BaseModel):
    """A style reference image with metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str
    display_name: str = ""
    description: str = ""
    path: Path
    tags: list[str] = Field(default_factory=list)

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        if v.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise ValueError(f"Style reference must be an image file, got: {v.suffix}")
        return v


# --- Provider Config ---


class ProviderConfig(BaseModel):
    """Configuration for a single provider."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    model: str
    api_key_env: str
    endpoint: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


# --- App Config ---


class AppConfig(BaseModel):
    """Top-level application configuration."""

    model_config = ConfigDict(extra="forbid")

    version: int = 1
    default_provider: ProviderName = ProviderName.GEMINI
    output_directory: str = "~/.diagram-forge/output"
    styles_directory: str = "~/.diagram-forge/styles"
    database_path: str = "~/.diagram-forge/usage.db"
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)


# --- Cost Tracking ---


class GenerationRecord(BaseModel):
    """A record of a single generation for cost tracking."""

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str
    model: str
    diagram_type: str | None = None
    resolution: str | None = None
    aspect_ratio: str | None = None
    tokens_used: int | None = None
    cost_usd: float
    billing_model: str
    generation_time_ms: int = 0
    success: bool = True
    output_path: str | None = None
    template_used: str | None = None
    style_used: str | None = None
    error_message: str | None = None


class UsageReport(BaseModel):
    """Aggregated usage report."""

    model_config = ConfigDict(extra="forbid")

    period_days: int
    total_generations: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    total_cost_usd: float = 0.0
    breakdown: list[dict[str, Any]] = Field(default_factory=list)
