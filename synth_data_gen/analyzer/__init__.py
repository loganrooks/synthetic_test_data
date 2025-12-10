"""
EPUB Pattern Analyzer module.

Provides tools for:
- Detecting formatting patterns in EPUB files
- Validating pattern coverage
- Human-in-the-loop workflow for adding new patterns
- Round-trip validation of generated EPUBs
"""

from .epub_analyzer import AnalysisResult, EpubAnalyzer, PatternMatch
from .registry import PatternConstraint, PatternDefinition, PatternRegistry

__all__ = [
    "PatternRegistry",
    "PatternDefinition",
    "PatternConstraint",
    "EpubAnalyzer",
    "AnalysisResult",
    "PatternMatch",
]
