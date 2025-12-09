"""
Pattern Registry for EPUB formatting patterns.

Provides a structured catalog of all supported patterns with:
- Detection signatures (CSS selectors, tag patterns)
- Constraint modeling (requires, conflicts_with)
- Generator configuration mappings
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from pathlib import Path


@dataclass
class PatternDefinition:
    """Definition of a single detectable EPUB pattern."""

    id: str
    category: str
    description: str
    detection_signature: Dict[str, Any]
    source_examples: List[str] = field(default_factory=list)
    epub_versions: List[int] = field(default_factory=lambda: [2, 3])
    requires: Set[str] = field(default_factory=set)
    conflicts_with: Set[str] = field(default_factory=set)
    generator_config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, pattern_id: str, data: Dict[str, Any]) -> "PatternDefinition":
        """Create a PatternDefinition from a dictionary."""
        return cls(
            id=pattern_id,
            category=data.get("category", "unknown"),
            description=data.get("description", ""),
            detection_signature=data.get("detection_signature", {}),
            source_examples=data.get("source_examples", []),
            epub_versions=data.get("epub_versions", [2, 3]),
            requires=set(data.get("requires", [])),
            conflicts_with=set(data.get("conflicts_with", [])),
            generator_config=data.get("generator_config", {}),
        )


@dataclass
class PatternConstraint:
    """Constraint relationship between patterns."""

    constraint_type: str  # "requires", "conflicts", "implies"
    source_pattern: str  # Pattern ID or wildcard (e.g., "navdoc_*")
    target_pattern: str
    reason: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatternConstraint":
        """Create a PatternConstraint from a dictionary."""
        return cls(
            constraint_type=data.get("type", "unknown"),
            source_pattern=data.get("source", ""),
            target_pattern=data.get("target", ""),
            reason=data.get("reason", ""),
        )


class PatternRegistry:
    """
    Registry of all supported EPUB patterns with constraint modeling.

    Loads patterns from YAML files in the patterns/ directory.
    """

    PATTERNS_DIR = Path(__file__).parent / "patterns"

    def __init__(self, patterns_dir: Optional[Path] = None):
        """Initialize the registry, optionally from a custom patterns directory."""
        self.patterns_dir = patterns_dir or self.PATTERNS_DIR
        self.patterns: Dict[str, PatternDefinition] = {}
        self.constraints: List[PatternConstraint] = []
        self._categories: Dict[str, List[str]] = {}
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load all pattern definitions from YAML files."""
        if not self.patterns_dir.exists():
            return

        # Load pattern definition files
        for yaml_file in self.patterns_dir.glob("*.yaml"):
            if yaml_file.name == "constraints.yaml":
                self._load_constraints(yaml_file)
            else:
                self._load_pattern_file(yaml_file)

    def _load_pattern_file(self, file_path: Path) -> None:
        """Load patterns from a single YAML file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if not data or "patterns" not in data:
                    return

                for pattern_id, pattern_data in data["patterns"].items():
                    pattern = PatternDefinition.from_dict(pattern_id, pattern_data)
                    self.patterns[pattern_id] = pattern

                    # Index by category
                    if pattern.category not in self._categories:
                        self._categories[pattern.category] = []
                    self._categories[pattern.category].append(pattern_id)
        except (yaml.YAMLError, IOError):
            pass  # Skip invalid files

    def _load_constraints(self, file_path: Path) -> None:
        """Load pattern constraints from constraints.yaml."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if not data or "constraints" not in data:
                    return

                for constraint_data in data["constraints"]:
                    constraint = PatternConstraint.from_dict(constraint_data)
                    self.constraints.append(constraint)
        except (yaml.YAMLError, IOError):
            pass

    def get_pattern(self, pattern_id: str) -> Optional[PatternDefinition]:
        """Get a pattern by its ID."""
        return self.patterns.get(pattern_id)

    def get_patterns_by_category(self, category: str) -> List[PatternDefinition]:
        """Get all patterns in a category."""
        pattern_ids = self._categories.get(category, [])
        return [self.patterns[pid] for pid in pattern_ids if pid in self.patterns]

    def get_all_categories(self) -> List[str]:
        """Get list of all pattern categories."""
        return list(self._categories.keys())

    def validate_pattern_combination(self, pattern_ids: List[str]) -> List[str]:
        """
        Validate a combination of patterns for constraint violations.

        Returns:
            List of constraint violation messages (empty if valid).
        """
        violations = []
        pattern_set = set(pattern_ids)

        for constraint in self.constraints:
            # Check if constraint applies
            matching_sources = self._match_pattern_wildcard(
                constraint.source_pattern, pattern_set
            )

            if not matching_sources:
                continue

            if constraint.constraint_type == "conflicts":
                matching_targets = self._match_pattern_wildcard(
                    constraint.target_pattern, pattern_set
                )
                if matching_targets:
                    violations.append(
                        f"Conflict: {matching_sources} conflicts with {matching_targets}. "
                        f"Reason: {constraint.reason}"
                    )

            elif constraint.constraint_type == "requires":
                matching_targets = self._match_pattern_wildcard(
                    constraint.target_pattern, pattern_set
                )
                if not matching_targets:
                    violations.append(
                        f"Missing requirement: {matching_sources} requires "
                        f"{constraint.target_pattern}. Reason: {constraint.reason}"
                    )

        # Also check pattern-level constraints
        for pattern_id in pattern_ids:
            pattern = self.get_pattern(pattern_id)
            if not pattern:
                continue

            # Check requires
            for required in pattern.requires:
                if required not in pattern_set:
                    violations.append(
                        f"Pattern '{pattern_id}' requires '{required}'"
                    )

            # Check conflicts
            for conflict in pattern.conflicts_with:
                if conflict in pattern_set:
                    violations.append(
                        f"Pattern '{pattern_id}' conflicts with '{conflict}'"
                    )

        return violations

    def _match_pattern_wildcard(
        self, pattern_spec: str, pattern_set: Set[str]
    ) -> Set[str]:
        """Match a pattern specification (possibly with wildcard) against a set."""
        if pattern_spec.endswith("_*"):
            prefix = pattern_spec[:-1]  # Remove trailing *
            return {p for p in pattern_set if p.startswith(prefix)}
        elif pattern_spec in pattern_set:
            return {pattern_spec}
        return set()

    def get_compatible_patterns(self, pattern_id: str) -> Set[str]:
        """Get all patterns compatible with the given pattern."""
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return set()

        compatible = set(self.patterns.keys())
        compatible.discard(pattern_id)

        # Remove conflicts
        compatible -= pattern.conflicts_with

        # Check global constraints
        for constraint in self.constraints:
            if constraint.constraint_type == "conflicts":
                if self._match_pattern_wildcard(constraint.source_pattern, {pattern_id}):
                    # Remove all targets
                    targets = self._match_pattern_wildcard(
                        constraint.target_pattern, compatible
                    )
                    compatible -= targets

        return compatible

    def list_patterns(self) -> List[str]:
        """Get list of all pattern IDs."""
        return list(self.patterns.keys())
