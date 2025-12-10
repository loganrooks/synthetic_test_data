"""
Tests for the validation module.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from synth_data_gen.analyzer.validation import (
    ValidationResult,
    round_trip_validate,
    validate_all_patterns,
    generate_validation_report,
    _generate_epub_with_pattern,
)
from synth_data_gen.analyzer.registry import PatternRegistry, PatternDefinition


class TestValidationResult:
    """Tests for the ValidationResult dataclass."""

    def test_creation_success(self):
        """Test creating a successful ValidationResult."""
        result = ValidationResult(
            pattern_id="ncx_flat",
            success=True,
            generated_path=Path("/tmp/test.epub"),
            detected_patterns=["ncx_flat", "header_standard"],
        )

        assert result.pattern_id == "ncx_flat"
        assert result.success is True
        assert result.generated_path == Path("/tmp/test.epub")
        assert "ncx_flat" in result.detected_patterns
        assert result.error is None

    def test_creation_failure(self):
        """Test creating a failed ValidationResult."""
        result = ValidationResult(
            pattern_id="navdoc_full",
            success=False,
            error="Pattern not detected in generated EPUB",
        )

        assert result.pattern_id == "navdoc_full"
        assert result.success is False
        assert result.error is not None

    def test_default_detected_patterns(self):
        """Test that detected_patterns defaults to empty list."""
        result = ValidationResult(pattern_id="test", success=True)

        assert result.detected_patterns == []


class TestRoundTripValidate:
    """Tests for the round_trip_validate function."""

    def test_pattern_not_found(self):
        """Test validation with non-existent pattern."""
        result = round_trip_validate("nonexistent_pattern")

        assert result.success is False
        assert "not found" in result.error.lower()

    def test_pattern_without_generator_config(self, tmp_path):
        """Test validation with pattern lacking generator_config."""
        # Create a minimal patterns directory
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        import yaml

        patterns = {
            "patterns": {
                "no_config": {
                    "category": "toc_style",
                    "description": "Pattern without generator config",
                    "detection_signature": {"ncx": {"required": True}},
                    # No generator_config!
                }
            }
        }

        with open(patterns_dir / "test.yaml", "w") as f:
            yaml.dump(patterns, f)

        registry = PatternRegistry(patterns_dir=patterns_dir)

        result = round_trip_validate("no_config", registry=registry)

        assert result.success is False
        assert "no generator_config" in result.error.lower()

    @patch("synth_data_gen.analyzer.validation._generate_epub_with_pattern")
    def test_generation_failure(self, mock_generate, tmp_path):
        """Test handling generation failure."""
        mock_generate.return_value = None

        # Create registry with valid pattern
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        import yaml

        patterns = {
            "patterns": {
                "test_pattern": {
                    "category": "toc_style",
                    "description": "Test pattern",
                    "detection_signature": {"ncx": {"required": True}},
                    "generator_config": {"toc_settings": {"style": "ncx"}},
                }
            }
        }

        with open(patterns_dir / "test.yaml", "w") as f:
            yaml.dump(patterns, f)

        registry = PatternRegistry(patterns_dir=patterns_dir)

        result = round_trip_validate("test_pattern", registry=registry)

        assert result.success is False
        assert "generate" in result.error.lower()

    @patch("synth_data_gen.analyzer.validation._generate_epub_with_pattern")
    @patch("synth_data_gen.analyzer.validation.EpubAnalyzer")
    def test_successful_validation(self, mock_analyzer_class, mock_generate, tmp_path):
        """Test successful round-trip validation."""
        # Setup mocks
        epub_path = tmp_path / "generated.epub"
        epub_path.touch()
        mock_generate.return_value = epub_path

        mock_analyzer = MagicMock()
        mock_result = MagicMock()
        mock_result.get_matched_pattern_ids.return_value = ["test_pattern", "other"]
        mock_analyzer.analyze.return_value = mock_result
        mock_analyzer_class.return_value = mock_analyzer

        # Create registry
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        import yaml

        patterns = {
            "patterns": {
                "test_pattern": {
                    "category": "toc_style",
                    "description": "Test pattern",
                    "detection_signature": {"ncx": {"required": True}},
                    "generator_config": {"toc_settings": {"style": "ncx"}},
                }
            }
        }

        with open(patterns_dir / "test.yaml", "w") as f:
            yaml.dump(patterns, f)

        registry = PatternRegistry(patterns_dir=patterns_dir)

        result = round_trip_validate("test_pattern", registry=registry, cleanup=False)

        assert result.success is True
        assert result.error is None
        assert "test_pattern" in result.detected_patterns

    @patch("synth_data_gen.analyzer.validation._generate_epub_with_pattern")
    @patch("synth_data_gen.analyzer.validation.EpubAnalyzer")
    def test_pattern_not_detected(self, mock_analyzer_class, mock_generate, tmp_path):
        """Test when pattern is not detected in generated EPUB."""
        # Setup mocks
        epub_path = tmp_path / "generated.epub"
        epub_path.touch()
        mock_generate.return_value = epub_path

        mock_analyzer = MagicMock()
        mock_result = MagicMock()
        mock_result.get_matched_pattern_ids.return_value = ["other_pattern"]
        mock_analyzer.analyze.return_value = mock_result
        mock_analyzer_class.return_value = mock_analyzer

        # Create registry
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        import yaml

        patterns = {
            "patterns": {
                "test_pattern": {
                    "category": "toc_style",
                    "description": "Test pattern",
                    "detection_signature": {"ncx": {"required": True}},
                    "generator_config": {"toc_settings": {"style": "ncx"}},
                }
            }
        }

        with open(patterns_dir / "test.yaml", "w") as f:
            yaml.dump(patterns, f)

        registry = PatternRegistry(patterns_dir=patterns_dir)

        result = round_trip_validate("test_pattern", registry=registry)

        assert result.success is False
        assert "not detected" in result.error.lower()


class TestValidateAllPatterns:
    """Tests for validate_all_patterns function."""

    @patch("synth_data_gen.analyzer.validation.round_trip_validate")
    def test_validate_all(self, mock_validate, tmp_path):
        """Test validating all patterns."""
        mock_validate.return_value = ValidationResult(
            pattern_id="test",
            success=True,
        )

        # Create registry with multiple patterns
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        import yaml

        patterns = {
            "patterns": {
                "pattern_a": {
                    "category": "toc_style",
                    "description": "A",
                    "detection_signature": {},
                },
                "pattern_b": {
                    "category": "notes_system",
                    "description": "B",
                    "detection_signature": {},
                },
            }
        }

        with open(patterns_dir / "test.yaml", "w") as f:
            yaml.dump(patterns, f)

        registry = PatternRegistry(patterns_dir=patterns_dir)

        results = validate_all_patterns(registry)

        assert len(results) == 2
        assert mock_validate.call_count == 2

    @patch("synth_data_gen.analyzer.validation.round_trip_validate")
    def test_validate_by_category(self, mock_validate, tmp_path):
        """Test validating patterns in specific categories."""
        mock_validate.return_value = ValidationResult(
            pattern_id="test",
            success=True,
        )

        # Create registry
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        import yaml

        patterns = {
            "patterns": {
                "toc_pattern": {
                    "category": "toc_style",
                    "description": "ToC",
                    "detection_signature": {},
                },
                "notes_pattern": {
                    "category": "notes_system",
                    "description": "Notes",
                    "detection_signature": {},
                },
            }
        }

        with open(patterns_dir / "test.yaml", "w") as f:
            yaml.dump(patterns, f)

        registry = PatternRegistry(patterns_dir=patterns_dir)

        results = validate_all_patterns(registry, categories=["toc_style"])

        assert len(results) == 1
        call_args = mock_validate.call_args[0]
        assert call_args[0] == "toc_pattern"


class TestGenerateValidationReport:
    """Tests for generate_validation_report function."""

    def test_all_passed(self):
        """Test report with all passing results."""
        results = [
            ValidationResult(pattern_id="pattern_a", success=True),
            ValidationResult(pattern_id="pattern_b", success=True),
        ]

        report = generate_validation_report(results)

        assert "Total patterns: 2" in report
        assert "Passed: 2" in report
        assert "Failed: 0" in report
        assert "pattern_a" in report
        assert "FAILED:" not in report or "Failed: 0" in report

    def test_some_failed(self):
        """Test report with some failures."""
        results = [
            ValidationResult(pattern_id="pattern_a", success=True),
            ValidationResult(
                pattern_id="pattern_b",
                success=False,
                error="Pattern not detected",
            ),
        ]

        report = generate_validation_report(results)

        assert "Total patterns: 2" in report
        assert "Passed: 1" in report
        assert "Failed: 1" in report
        assert "✓ pattern_a" in report
        assert "✗ pattern_b" in report
        assert "Pattern not detected" in report

    def test_empty_results(self):
        """Test report with no results."""
        report = generate_validation_report([])

        assert "Total patterns: 0" in report
        assert "Passed: 0" in report
        assert "Failed: 0" in report


class TestGenerateEpubWithPattern:
    """Tests for _generate_epub_with_pattern helper."""

    def test_returns_none_on_import_error(self, tmp_path):
        """Test graceful handling when generate_data not available."""
        pattern = PatternDefinition(
            id="test",
            category="toc_style",
            description="Test",
            detection_signature={},
            generator_config={"toc_settings": {"style": "ncx"}},
        )

        # Mock the import inside the function by patching synth_data_gen.generate_data
        with patch.dict("sys.modules", {"synth_data_gen": MagicMock()}):
            import sys
            sys.modules["synth_data_gen"].generate_data = MagicMock(
                side_effect=ImportError("Module not found")
            )
            result = _generate_epub_with_pattern(pattern, tmp_path)

        # Should return None, not raise
        assert result is None

    def test_returns_path_on_success(self, tmp_path):
        """Test returning path when generation succeeds."""
        epub_path = tmp_path / "output" / "validation" / "test.epub"
        epub_path.parent.mkdir(parents=True)
        epub_path.touch()

        pattern = PatternDefinition(
            id="test",
            category="toc_style",
            description="Test",
            detection_signature={},
            generator_config={"toc_settings": {"style": "ncx"}},
        )

        with patch("synth_data_gen.generate_data") as mock_generate:
            mock_generate.return_value = [str(epub_path)]
            result = _generate_epub_with_pattern(pattern, tmp_path)

        assert result == epub_path

    def test_returns_none_on_empty_result(self, tmp_path):
        """Test returning None when no files generated."""
        pattern = PatternDefinition(
            id="test",
            category="toc_style",
            description="Test",
            detection_signature={},
            generator_config={"toc_settings": {"style": "ncx"}},
        )

        with patch("synth_data_gen.generate_data") as mock_generate:
            mock_generate.return_value = []
            result = _generate_epub_with_pattern(pattern, tmp_path)

        assert result is None
