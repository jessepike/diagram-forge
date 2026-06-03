"""Tests for template engine."""

from __future__ import annotations

import pytest

from diagram_forge.models import DiagramTemplate, GlobalDesignTokens, Theme
from diagram_forge.template_engine import (
    build_global_style_block,
    build_prompt,
    load_all_templates,
    load_template,
    render_prompt,
)


class TestLoadTemplate:
    def test_load_architecture_template(self):
        """Architecture template should load successfully."""
        t = load_template("architecture")
        assert t.name == "architecture"
        assert "TOGAF" in t.display_name
        assert t.color_system is not None
        assert "business" in t.color_system.palette

    def test_load_generic_template(self):
        """Generic template should load successfully."""
        t = load_template("generic")
        assert t.name == "generic"
        assert "content" in t.variables

    def test_load_nonexistent_template_raises(self):
        """Loading nonexistent template should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_template("nonexistent_template_xyz")


class TestLoadAllTemplates:
    def test_loads_all_templates(self):
        """Should load all 13 bundled templates."""
        templates = load_all_templates()
        assert len(templates) == 13
        expected = {
            "architecture", "data_flow", "component",
            "sequence", "integration", "infographic", "generic",
            "c4_container", "exec_infographic",
            "brand_infographic", "product_roadmap", "workstreams", "kanban",
        }
        assert set(templates.keys()) == expected

    def test_all_templates_have_required_fields(self):
        """Every template should have name, display_name, description, prompt_template."""
        for name, t in load_all_templates().items():
            assert t.name, f"{name} missing name"
            assert t.display_name, f"{name} missing display_name"
            assert t.description, f"{name} missing description"
            assert t.prompt_template, f"{name} missing prompt_template"


class TestRenderPrompt:
    def test_basic_render(self):
        """Render should substitute variables."""
        t = DiagramTemplate(
            name="test",
            display_name="Test",
            description="Test template",
            prompt_template="Draw a {thing} with {color} color.",
            variables={"thing": "box", "color": "blue"},
        )
        result = render_prompt(t)
        assert "box" in result
        assert "blue" in result

    def test_user_variables_override_defaults(self):
        """User-provided variables should override template defaults."""
        t = DiagramTemplate(
            name="test",
            display_name="Test",
            description="Test",
            prompt_template="Draw a {thing}.",
            variables={"thing": "circle"},
        )
        result = render_prompt(t, user_variables={"thing": "triangle"})
        assert "triangle" in result
        assert "circle" not in result

    def test_extra_instructions_appended(self):
        """Extra instructions should be appended to the prompt."""
        t = DiagramTemplate(
            name="test",
            display_name="Test",
            description="Test",
            prompt_template="Base prompt.",
        )
        result = render_prompt(t, extra_instructions="Make it red.")
        assert "Base prompt." in result
        assert "Make it red." in result


class TestBuildPrompt:
    def test_build_with_valid_template(self):
        """Building with a valid template type should include template content."""
        prompt = build_prompt(
            diagram_type="architecture",
            user_prompt="My system architecture",
            resolution="2K",
            aspect_ratio="16:9",
        )
        assert "architecture" in prompt.lower() or "TOGAF" in prompt
        assert "My system architecture" in prompt

    def test_build_with_unknown_type_falls_back(self):
        """Unknown diagram type should fall back to generic formatting."""
        prompt = build_prompt(
            diagram_type="unknown_type_xyz",
            user_prompt="Custom diagram",
        )
        assert "Custom diagram" in prompt
        assert "Enterprise presentation quality" in prompt

    def test_build_includes_resolution_and_aspect(self):
        """Build should include resolution and aspect ratio in the prompt."""
        prompt = build_prompt(
            diagram_type="generic",
            user_prompt="Test",
            resolution="4K",
            aspect_ratio="1:1",
        )
        assert "4K" in prompt


class TestTheme:
    def test_default_tokens_are_light(self):
        """Fresh tokens default to the light theme."""
        assert GlobalDesignTokens().theme == Theme.LIGHT

    def test_default_build_is_light(self):
        """build_prompt with no theme emits a LIGHT background directive."""
        prompt = build_prompt(diagram_type="exec_infographic", user_prompt="Test")
        assert "BACKGROUND THEME: LIGHT" in prompt
        assert "BACKGROUND THEME: DARK" not in prompt

    def test_explicit_dark_build(self):
        """theme='dark' emits a DARK background directive and dark canvas color."""
        prompt = build_prompt(
            diagram_type="exec_infographic", user_prompt="Test", theme="dark"
        )
        assert "BACKGROUND THEME: DARK" in prompt
        assert "#0E1116" in prompt  # dark canvas color
        # Per-template "STYLE: white background" hint is suppressed under dark
        # (deferred to the theme directive) so there's no conflicting signal.
        assert "STYLE: white background" not in prompt
        assert "theme-governed" in prompt

    def test_dark_then_light_independent(self):
        """for_theme is non-mutating: requesting dark then light yields light again."""
        base = GlobalDesignTokens()
        dark = base.for_theme(Theme.DARK)
        light = base.for_theme(Theme.LIGHT)
        assert dark.theme == Theme.DARK
        assert dark.colors.background == "#0E1116"
        assert light.theme == Theme.LIGHT
        assert light.colors.background == "#FFFFFF"
        # Base is unchanged.
        assert base.colors.background == "#FFFFFF"

    def test_style_block_light_vs_dark(self):
        """build_global_style_block reflects the token theme."""
        light_block = build_global_style_block(GlobalDesignTokens())
        dark_block = build_global_style_block(GlobalDesignTokens().for_theme(Theme.DARK))
        assert "BACKGROUND THEME: LIGHT" in light_block
        assert "BACKGROUND THEME: DARK" in dark_block
