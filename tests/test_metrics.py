"""Unit tests for the CodePulse metrics."""
import json
import os
import tempfile
import textwrap
from pathlib import Path

from metrics import analyze


def create_file(dir_path: Path, name: str, content: str) -> Path:
    p = dir_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_simple_project(tmp_path: Path):
    # Create two small modules with a duplicate line
    create_file(tmp_path, "a.py", textwrap.dedent("""
        def foo():
            x = 1
            y = 2
            return x + y
    """))
    create_file(tmp_path, "b.py", textwrap.dedent("""
        def bar():
            x = 1  # duplicate line
            z = 3
            return x * z
    """))

    report = analyze(tmp_path)
    assert isinstance(report, dict)
    assert report["duplicate_lines"] == 1
    assert report["average_verbosity"] > 0
    assert report["average_cognitive_complexity"] > 0
    assert isinstance(report["suggestions"], list)


def test_no_python_files(tmp_path: Path):
    create_file(tmp_path, "readme.md", "# Project")
    report = analyze(tmp_path)
    assert "error" in report

# Run tests if executed directly
if __name__ == "__main__":
    import unittest
    unittest.main()
