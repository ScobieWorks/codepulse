#!/usr/bin/env python3
"""Base class for language‑specific analyzers.

The :class:`LanguageAnalyzer` defines a minimal interface that can be
implemented by language‑specific subclasses.  The default implementation
provided in :mod:`metrics` uses this base class for Python files.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict


class LanguageAnalyzer(ABC):
    """Abstract base class for language analyzers.

    Subclasses must implement :meth:`analyze` which receives a :class:`Path`
    pointing to a project directory or a single source file and returns a
    dictionary that can be serialised to JSON.
    """

    @abstractmethod
    def analyze(self, path: Path) -> Dict:
        """Analyse *path* and return a report dictionary."""
        raise NotImplementedError
