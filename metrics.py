#!/usr/bin/env python3
"""Core metric calculations for CodePulse.

The implementation focuses on Python source files.  It can be extended to other
languages by adding new analyzers and updating the :func:`analyze` function.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, Iterable, List

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _iter_python_files(path: Path) -> Iterable[Path]:
    """Yield all ``.py`` files under *path* (recursively).

    Parameters
    ----------
    path:
        Directory or file to search.

    Yields
    ------
    Path
        Paths to Python files.
    """
    if path.is_file() and path.suffix == ".py":
        yield path
    elif path.is_dir():
        for p in path.rglob("*.py"):
            yield p


def _read_file(path: Path) -> str:
    """Return the contents of *path* as a UTF‑8 string."""
    return path.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Verbosity metric – average LOC per function
# ---------------------------------------------------------------------------


def _function_loc(source: str) -> List[int]:
    """Return a list of LOC counts for each function defined in *source*.

    The count includes the function definition line and all lines up to the
    last line of the function body.
    """
    tree = ast.parse(source)
    locs: List[int] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            locs.append(end - start + 1)
    return locs

# ---------------------------------------------------------------------------
# Duplication metric – count duplicate lines across files
# ---------------------------------------------------------------------------


def _duplicate_lines(files: List[Path]) -> int:
    """Count how many lines appear in more than one file.

    Lines are compared after stripping leading/trailing whitespace and
    removing any inline comments. Empty lines are ignored.
    """
    line_to_files: Dict[str, set[Path]] = {}
    for f in files:
        seen_in_file = set()
        for line in _read_file(f).splitlines():
            code_part = line.split('#', 1)[0].strip()
            if not code_part:
                continue
            seen_in_file.add(code_part)
        for code_part in seen_in_file:
            line_to_files.setdefault(code_part, set()).add(f)
    return sum(1 for files_set in line_to_files.values() if len(files_set) > 1)

# ---------------------------------------------------------------------------
# Erosion metric – simple change‑rate estimate
# ---------------------------------------------------------------------------


def _erosion_metric(files: List[Path]) -> float:
    """Return a simple erosion score: duplicate lines / total lines.

    This provides a rough estimate of code churn based on how many lines are
    duplicated across files. It is intentionally lightweight and does not
    require VCS history.
    """
    total_lines = sum(len(_read_file(f).splitlines()) for f in files)
    dup_lines = _duplicate_lines(files)
    return dup_lines / total_lines if total_lines else 0.0

# ---------------------------------------------------------------------------
# Cognitive complexity – count statements per function
# ---------------------------------------------------------------------------


def _cognitive_complexity(source: str) -> List[int]:
    """Return a list of complexity scores for each function.

    For simplicity, we count all statement nodes inside the function body,
    excluding the function definition itself. This matches the current
    implementation and keeps the metric simple.
    """
    tree = ast.parse(source)
    complexities: List[int] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            score = sum(
                1 for child in ast.walk(node)
                if isinstance(child, ast.stmt) and child is not node
            )
            complexities.append(score)
    return complexities

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = ["analyze"]


def analyze(path: Path) -> Dict[str, Any]:
    """Analyze *path* and return a JSON‑serialisable report.

    The report contains:

    * ``average_verbosity`` – average LOC per function
    * ``duplicate_lines`` – number of duplicate lines across files
    * ``erosion`` – simple erosion score (0‑1)
    * ``average_cognitive_complexity`` – average complexity per function
    * ``suggestions`` – list of actionable suggestions
    """
    files = list(_iter_python_files(path))
    if not files:
        return {"error": "No Python files found"}

    all_func_locs: List[int] = []
    all_complexities: List[int] = []
    for f in files:
        src = _read_file(f)
        all_func_locs.extend(_function_loc(src))
        all_complexities.extend(_cognitive_complexity(src))

    avg_verbosity = sum(all_func_locs) / len(all_func_locs) if all_func_locs else 0
    avg_complexity = sum(all_complexities) / len(all_complexities) if all_complexities else 0
    dup_lines = _duplicate_lines(files)
    erosion = _erosion_metric(files)

    suggestions: List[str] = []
    if avg_verbosity > 30:
        suggestions.append("Consider breaking large functions into smaller ones.")
    if dup_lines > 0:
        suggestions.append(f"Found {dup_lines} duplicate lines – extract common code.")
    if avg_complexity > 5:
        suggestions.append("High cognitive complexity detected – refactor control flow.")
    if erosion > 0.2:
        suggestions.append("Erosion score high – review recent changes for unnecessary churn.")

    return {
        "average_verbosity": round(avg_verbosity, 2),
        "duplicate_lines": dup_lines,
        "erosion": round(erosion, 3),
        "average_cognitive_complexity": round(avg_complexity, 2),
        "suggestions": suggestions,
    }

# ---------------------------------------------------------------------------
# If run as a script, perform a quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python metrics.py <path>")
        sys.exit(1)
    print(analyze(Path(sys.argv[1])))

# ---------------------------------------------------------------------------
# Provide a pytest fixture for tmp_path to satisfy tests that use the fixture
# ---------------------------------------------------------------------------

try:
    import pytest

    class _TmpPathPlugin:
        @pytest.fixture
        def tmp_path(self, tmp_path_factory):
            """Return a temporary directory path for tests.

            This fixture mirrors the built‑in pytest ``tmp_path`` fixture and
            provides a temporary directory that is automatically cleaned up.
            """
            return tmp_path_factory.mktemp("tmp")

    def pytest_configure(config):
        # Register the plugin that provides the ``tmp_path`` fixture
        config.pluginmanager.register(_TmpPathPlugin())
except Exception:
    # If pytest is not available, ignore – the fixture is only needed for
    # the test environment.
    pass
