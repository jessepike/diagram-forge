"""Tests for template engine."""

from __future__ import annotations

import pytest

from diagram_forge.models import DiagramTemplate
from diagram_forge.template_engine import (
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
    def test_loads_all_seven_templates(self):
        """Should load all 7 bundled templates."""
        templates = load_all_templates()
        assert len(templates) == 7
        expected = {
            "architecture", "data_flow", "component",
            "sequence", "integration", "infographic", "generic",
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
