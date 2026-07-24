"""Tests for output_path validation — relative paths must be rejected loudly.

A relative output_path resolves against the diagram-forge server's own working
directory (not the caller's repo), silently misplacing the saved file. The server
rejects relative paths early instead. Reported 2026-07-16.
"""

from __future__ import annotations

from diagram_forge.server import _reject_relative_output_path


class TestRejectRelativeOutputPath:
    def test_relative_path_returns_error(self):
        """A relative path should return an error dict mentioning 'absolute'."""
        result = _reject_relative_output_path("docs/diagrams/foo.png")
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "absolute" in result["error"].lower()

    def test_bare_relative_filename_returns_error(self):
        """A bare filename with no directory is still relative and rejected."""
        result = _reject_relative_output_path("foo.png")
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "absolute" in result["error"].lower()

    def test_absolute_path_returns_none(self):
        """An absolute path is valid and passes through (returns None)."""
        assert _reject_relative_output_path("/Users/you/repo/docs/diagram.png") is None

    def test_none_returns_none(self):
        """No output_path (auto-generated) is valid and passes through."""
        assert _reject_relative_output_path(None) is None

    def test_home_relative_path_is_treated_as_absolute(self):
        """A ~-prefixed path is made absolute by expanduser, so it is accepted."""
        assert _reject_relative_output_path("~/foo.png") is None
