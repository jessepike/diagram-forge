"""Style reference image management."""

from __future__ import annotations

from pathlib import Path

import yaml

from diagram_forge.models import StyleReference

BUNDLED_STYLES_DIR = Path(__file__).parent / "styles"


class StyleManager:
    """Manages style reference images from bundled and user directories."""

    def __init__(self, user_styles_dir: str | Path | None = None):
        self.bundled_dir = BUNDLED_STYLES_DIR
        self.user_dir = Path(user_styles_dir).expanduser() if user_styles_dir else None

    def list_styles(self) -> list[StyleReference]:
        """List all available style references."""
        styles: list[StyleReference] = []
        styles.extend(self._scan_directory(self.bundled_dir, source="bundled"))
        if self.user_dir and self.user_dir.exists():
            styles.extend(self._scan_directory(self.user_dir, source="user"))
        return styles

    def get_style(self, name: str) -> StyleReference | None:
        """Get a specific style by name."""
        for style in self.list_styles():
            if style.name == name:
                return style
        return None

    def get_style_path(self, name_or_path: str) -> Path | None:
        """Resolve a style name or path to a file path."""
        # Check if it's a direct file path
        p = Path(name_or_path).expanduser()
        if p.exists() and p.is_file():
            return p

        # Try as a style name
        style = self.get_style(name_or_path)
        if style:
            return style.path

        return None

    def _scan_directory(self, directory: Path, source: str = "") -> list[StyleReference]:
        """Scan a directory for style reference images."""
        styles: list[StyleReference] = []
        if not directory.exists():
            return styles

        image_extensions = {".png", ".jpg", ".jpeg", ".webp"}

        for style_dir in sorted(directory.iterdir()):
            if not style_dir.is_dir():
                continue

            # Look for reference image
            ref_image = None
            for ext in image_extensions:
                candidate = style_dir / f"reference{ext}"
                if candidate.exists():
                    ref_image = candidate
                    break

            if not ref_image:
                # Take first image found
                for image_file in style_dir.iterdir():
                    if image_file.suffix.lower() in image_extensions:
                        ref_image = image_file
                        break

            if not ref_image:
                continue

            # Load metadata if available
            meta_path = style_dir / "style.yaml"
            if meta_path.exists():
                with open(meta_path) as meta_file:
                    meta = yaml.safe_load(meta_file) or {}
            else:
                meta = {}

            styles.append(
                StyleReference(
                    name=meta.get("name", style_dir.name),
                    display_name=meta.get("display_name", style_dir.name.replace("-", " ").title()),
                    description=meta.get("description", f"Style from {source}: {style_dir.name}"),
                    path=ref_image,
                    tags=meta.get("tags", []),
                )
            )

        return styles
