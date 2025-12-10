"""
Tests for the PatternRegistry module.
"""


import pytest
import yaml

from synth_data_gen.analyzer.registry import (
    PatternConstraint,
    PatternDefinition,
    PatternRegistry,
)


class TestPatternDefinition:
    """Tests for the PatternDefinition dataclass."""

    def test_from_dict_minimal(self):
        """Test creating PatternDefinition from minimal dict."""
        data = {
            "category": "toc_style",
            "description": "A test pattern",
            "detection_signature": {"ncx": {"required": True}},
        }
        pattern = PatternDefinition.from_dict("test_pattern", data)

        assert pattern.id == "test_pattern"
        assert pattern.category == "toc_style"
        assert pattern.description == "A test pattern"
        assert pattern.detection_signature == {"ncx": {"required": True}}
        assert pattern.source_examples == []
        assert pattern.epub_versions == [2, 3]
        assert pattern.requires == set()
        assert pattern.conflicts_with == set()
        assert pattern.generator_config == {}

    def test_from_dict_full(self):
        """Test creating PatternDefinition from full dict."""
        data = {
            "category": "notes_system",
            "description": "Footnotes pattern",
            "detection_signature": {"reference": {"type": "sup_link"}},
            "source_examples": ["Book A", "Book B"],
            "epub_versions": [3],
            "requires": ["epub3_container"],
            "conflicts_with": ["epub2_only"],
            "generator_config": {"notes_system": {"type": "footnotes"}},
        }
        pattern = PatternDefinition.from_dict("footnotes_linked", data)

        assert pattern.id == "footnotes_linked"
        assert pattern.source_examples == ["Book A", "Book B"]
        assert pattern.epub_versions == [3]
        assert pattern.requires == {"epub3_container"}
        assert pattern.conflicts_with == {"epub2_only"}
        assert pattern.generator_config == {"notes_system": {"type": "footnotes"}}


class TestPatternConstraint:
    """Tests for the PatternConstraint dataclass."""

    def test_from_dict(self):
        """Test creating PatternConstraint from dict."""
        data = {
            "type": "conflicts",
            "source": "navdoc_*",
            "target": "epub2_only",
            "reason": "Navigation Documents require EPUB3",
        }
        constraint = PatternConstraint.from_dict(data)

        assert constraint.constraint_type == "conflicts"
        assert constraint.source_pattern == "navdoc_*"
        assert constraint.target_pattern == "epub2_only"
        assert constraint.reason == "Navigation Documents require EPUB3"

    def test_from_dict_defaults(self):
        """Test creating PatternConstraint with missing fields."""
        constraint = PatternConstraint.from_dict({})

        assert constraint.constraint_type == "unknown"
        assert constraint.source_pattern == ""
        assert constraint.target_pattern == ""
        assert constraint.reason == ""


class TestPatternRegistry:
    """Tests for the PatternRegistry class."""

    @pytest.fixture
    def temp_patterns_dir(self, tmp_path):
        """Create a temporary patterns directory with test YAML files."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create test patterns file
        toc_patterns = {
            "patterns": {
                "ncx_flat": {
                    "category": "toc_style",
                    "description": "Simple flat NCX",
                    "detection_signature": {"ncx": {"required": True, "max_depth": 2}},
                    "generator_config": {"toc_settings": {"style": "ncx"}},
                },
                "navdoc_basic": {
                    "category": "toc_style",
                    "description": "EPUB3 Navigation Document",
                    "epub_versions": [3],
                    "detection_signature": {"navdoc": {"required": True}},
                    "requires": ["epub3_container"],
                    "conflicts_with": ["epub2_only"],
                },
            }
        }

        notes_patterns = {
            "patterns": {
                "footnotes_linked": {
                    "category": "notes_system",
                    "description": "Linked footnotes",
                    "detection_signature": {"reference": {"type": "sup_link"}},
                },
            }
        }

        constraints = {
            "constraints": [
                {
                    "type": "conflicts",
                    "source": "navdoc_*",
                    "target": "epub2_only",
                    "reason": "NavDoc requires EPUB3",
                },
                {
                    "type": "requires",
                    "source": "footnotes_*",
                    "target": "body_content",
                    "reason": "Footnotes need body content",
                },
            ]
        }

        with open(patterns_dir / "toc_styles.yaml", "w") as f:
            yaml.dump(toc_patterns, f)

        with open(patterns_dir / "notes.yaml", "w") as f:
            yaml.dump(notes_patterns, f)

        with open(patterns_dir / "constraints.yaml", "w") as f:
            yaml.dump(constraints, f)

        return patterns_dir

    def test_load_patterns_from_directory(self, temp_patterns_dir):
        """Test loading patterns from YAML files."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        assert len(registry.patterns) == 3
        assert "ncx_flat" in registry.patterns
        assert "navdoc_basic" in registry.patterns
        assert "footnotes_linked" in registry.patterns

    def test_load_constraints(self, temp_patterns_dir):
        """Test loading constraints from constraints.yaml."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        assert len(registry.constraints) == 2
        assert registry.constraints[0].constraint_type == "conflicts"
        assert registry.constraints[0].source_pattern == "navdoc_*"

    def test_get_pattern(self, temp_patterns_dir):
        """Test getting a pattern by ID."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        pattern = registry.get_pattern("ncx_flat")
        assert pattern is not None
        assert pattern.id == "ncx_flat"
        assert pattern.category == "toc_style"

        # Non-existent pattern
        assert registry.get_pattern("nonexistent") is None

    def test_get_patterns_by_category(self, temp_patterns_dir):
        """Test getting all patterns in a category."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        toc_patterns = registry.get_patterns_by_category("toc_style")
        assert len(toc_patterns) == 2

        pattern_ids = [p.id for p in toc_patterns]
        assert "ncx_flat" in pattern_ids
        assert "navdoc_basic" in pattern_ids

        # Empty category
        empty = registry.get_patterns_by_category("nonexistent")
        assert empty == []

    def test_get_all_categories(self, temp_patterns_dir):
        """Test getting all category names."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        categories = registry.get_all_categories()
        assert "toc_style" in categories
        assert "notes_system" in categories

    def test_list_patterns(self, temp_patterns_dir):
        """Test listing all pattern IDs."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        pattern_ids = registry.list_patterns()
        assert len(pattern_ids) == 3
        assert "ncx_flat" in pattern_ids

    def test_validate_pattern_combination_valid(self, temp_patterns_dir):
        """Test validating a valid pattern combination."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        violations = registry.validate_pattern_combination(["ncx_flat", "footnotes_linked"])
        # Should have no conflicts but may have missing requirements
        conflict_violations = [v for v in violations if "Conflict" in v]
        assert len(conflict_violations) == 0

    def test_validate_pattern_combination_conflict(self, temp_patterns_dir):
        """Test detecting conflicts in pattern combination."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        # Add epub2_only pattern to simulate conflict
        registry.patterns["epub2_only"] = PatternDefinition(
            id="epub2_only",
            category="container",
            description="EPUB2 only",
            detection_signature={},
        )

        violations = registry.validate_pattern_combination(["navdoc_basic", "epub2_only"])

        # Should detect conflict from navdoc_basic's conflicts_with
        conflict_violations = [v for v in violations if "conflicts" in v.lower()]
        assert len(conflict_violations) > 0

    def test_validate_pattern_combination_missing_requirement(self, temp_patterns_dir):
        """Test detecting missing requirements."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        # navdoc_basic requires epub3_container which isn't in the combination
        violations = registry.validate_pattern_combination(["navdoc_basic"])

        requirement_violations = [v for v in violations if "requires" in v.lower()]
        assert len(requirement_violations) > 0

    def test_match_pattern_wildcard(self, temp_patterns_dir):
        """Test wildcard matching in constraints."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        # Test prefix wildcard
        pattern_set = {"navdoc_basic", "navdoc_full", "ncx_flat"}
        matches = registry._match_pattern_wildcard("navdoc_*", pattern_set)
        assert matches == {"navdoc_basic", "navdoc_full"}

        # Test exact match
        matches = registry._match_pattern_wildcard("ncx_flat", pattern_set)
        assert matches == {"ncx_flat"}

        # Test no match
        matches = registry._match_pattern_wildcard("nonexistent", pattern_set)
        assert matches == set()

    def test_get_compatible_patterns(self, temp_patterns_dir):
        """Test getting patterns compatible with a given pattern."""
        registry = PatternRegistry(patterns_dir=temp_patterns_dir)

        # navdoc_basic conflicts with epub2_only
        registry.patterns["epub2_only"] = PatternDefinition(
            id="epub2_only",
            category="container",
            description="EPUB2 only",
            detection_signature={},
        )

        compatible = registry.get_compatible_patterns("navdoc_basic")

        # Should not include epub2_only (conflicting) or navdoc_basic itself
        assert "navdoc_basic" not in compatible
        assert "epub2_only" not in compatible
        assert "ncx_flat" in compatible

    def test_empty_patterns_directory(self, tmp_path):
        """Test handling empty or non-existent patterns directory."""
        empty_dir = tmp_path / "empty"
        # Don't create the directory

        registry = PatternRegistry(patterns_dir=empty_dir)

        assert len(registry.patterns) == 0
        assert len(registry.constraints) == 0

    def test_invalid_yaml_file(self, tmp_path):
        """Test handling invalid YAML files gracefully."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create invalid YAML
        with open(patterns_dir / "invalid.yaml", "w") as f:
            f.write("invalid: yaml: content: [")

        # Should not raise, just skip invalid file
        registry = PatternRegistry(patterns_dir=patterns_dir)
        assert len(registry.patterns) == 0

    def test_yaml_file_without_patterns_key(self, tmp_path):
        """Test handling YAML files without patterns key."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create YAML without patterns key
        with open(patterns_dir / "other.yaml", "w") as f:
            yaml.dump({"other_key": "value"}, f)

        registry = PatternRegistry(patterns_dir=patterns_dir)
        assert len(registry.patterns) == 0


    def test_add_pattern(self, tmp_path):
        """Test adding a new pattern to the registry."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        registry = PatternRegistry(patterns_dir=patterns_dir)

        new_pattern = PatternDefinition(
            id="new_test_pattern",
            category="test_category",
            description="A test pattern",
            detection_signature={"test": True},
        )

        assert registry.add_pattern(new_pattern) is True
        assert "new_test_pattern" in registry.patterns
        assert "test_category" in registry._categories
        assert "new_test_pattern" in registry._categories["test_category"]

    def test_add_pattern_duplicate(self, tmp_path):
        """Test that adding duplicate pattern returns False."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        registry = PatternRegistry(patterns_dir=patterns_dir)

        pattern = PatternDefinition(
            id="duplicate_pattern",
            category="test",
            description="Test",
            detection_signature={},
        )

        assert registry.add_pattern(pattern) is True
        assert registry.add_pattern(pattern) is False

    def test_save_pattern_to_file(self, tmp_path):
        """Test saving a pattern to a YAML file."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        registry = PatternRegistry(patterns_dir=patterns_dir)

        pattern = PatternDefinition(
            id="saved_pattern",
            category="toc_style",
            description="A saved pattern",
            detection_signature={"ncx": {"required": True}},
            source_examples=["Example Book"],
            generator_config={"toc_settings": {"style": "ncx"}},
        )

        file_path = registry.save_pattern_to_file(pattern)

        assert file_path.exists()
        assert file_path.name == "toc_style.yaml"

        # Verify file contents
        with open(file_path) as f:
            data = yaml.safe_load(f)

        assert "patterns" in data
        assert "saved_pattern" in data["patterns"]
        assert data["patterns"]["saved_pattern"]["category"] == "toc_style"
        assert data["patterns"]["saved_pattern"]["description"] == "A saved pattern"

    def test_save_pattern_to_existing_file(self, tmp_path):
        """Test saving a pattern to an existing YAML file."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create initial file with one pattern
        initial_data = {
            "patterns": {
                "existing_pattern": {
                    "category": "toc_style",
                    "description": "Existing",
                    "detection_signature": {},
                }
            }
        }
        file_path = patterns_dir / "toc_style.yaml"
        with open(file_path, "w") as f:
            yaml.dump(initial_data, f)

        registry = PatternRegistry(patterns_dir=patterns_dir)

        new_pattern = PatternDefinition(
            id="new_pattern",
            category="toc_style",
            description="New pattern",
            detection_signature={"new": True},
        )

        registry.save_pattern_to_file(new_pattern)

        # Verify both patterns exist
        with open(file_path) as f:
            data = yaml.safe_load(f)

        assert "existing_pattern" in data["patterns"]
        assert "new_pattern" in data["patterns"]


class TestPatternRegistryWithRealPatterns:
    """Tests using the real patterns directory."""

    def test_load_real_patterns(self):
        """Test loading from the real patterns directory."""
        registry = PatternRegistry()

        # Should load patterns from the real directory
        assert len(registry.patterns) > 0

        # Check some expected patterns exist
        categories = registry.get_all_categories()
        assert "toc_style" in categories

    def test_real_pattern_structure(self):
        """Test that real patterns have required fields."""
        registry = PatternRegistry()

        for pattern_id, pattern in registry.patterns.items():
            assert pattern.id == pattern_id
            assert pattern.category != ""
            assert isinstance(pattern.detection_signature, dict)
            assert isinstance(pattern.epub_versions, list)
