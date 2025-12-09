"""
Round-trip validation for EPUB patterns.

Validates that the library can correctly generate and detect its own patterns:
1. Get generator config for a pattern
2. Generate an EPUB using that config
3. Analyze the generated EPUB
4. Verify the pattern is detected
"""

import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass

from .registry import PatternRegistry, PatternDefinition
from .epub_analyzer import EpubAnalyzer, AnalysisResult


@dataclass
class ValidationResult:
    """Result of a round-trip validation test."""

    pattern_id: str
    success: bool
    generated_path: Optional[Path] = None
    detected_patterns: List[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.detected_patterns is None:
            self.detected_patterns = []


def round_trip_validate(
    pattern_id: str,
    registry: Optional[PatternRegistry] = None,
    cleanup: bool = True,
) -> ValidationResult:
    """
    Validate a pattern through round-trip generation and detection.

    Args:
        pattern_id: ID of the pattern to validate.
        registry: PatternRegistry instance (creates default if None).
        cleanup: Whether to delete generated files after validation.

    Returns:
        ValidationResult with success status and details.
    """
    registry = registry or PatternRegistry()
    pattern = registry.get_pattern(pattern_id)

    if not pattern:
        return ValidationResult(
            pattern_id=pattern_id,
            success=False,
            error=f"Pattern not found in registry: {pattern_id}",
        )

    if not pattern.generator_config:
        return ValidationResult(
            pattern_id=pattern_id,
            success=False,
            error=f"Pattern has no generator_config: {pattern_id}",
        )

    temp_dir = None
    try:
        # Create temp directory for output
        temp_dir = Path(tempfile.mkdtemp(prefix="epub_validation_"))

        # Generate EPUB using pattern's config
        generated_path = _generate_epub_with_pattern(pattern, temp_dir)

        if not generated_path or not generated_path.exists():
            return ValidationResult(
                pattern_id=pattern_id,
                success=False,
                error="Failed to generate EPUB file",
            )

        # Analyze the generated EPUB
        analyzer = EpubAnalyzer(registry)
        result = analyzer.analyze(generated_path)

        # Check if the pattern was detected
        detected_ids = result.get_matched_pattern_ids()
        success = pattern_id in detected_ids

        return ValidationResult(
            pattern_id=pattern_id,
            success=success,
            generated_path=generated_path if not cleanup else None,
            detected_patterns=detected_ids,
            error=None if success else f"Pattern not detected. Found: {detected_ids}",
        )

    except Exception as e:
        return ValidationResult(
            pattern_id=pattern_id,
            success=False,
            error=f"Validation error: {str(e)}",
        )

    finally:
        if cleanup and temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def _generate_epub_with_pattern(
    pattern: PatternDefinition, output_dir: Path
) -> Optional[Path]:
    """
    Generate an EPUB file using the pattern's generator config.

    Args:
        pattern: Pattern definition with generator_config.
        output_dir: Directory for output files.

    Returns:
        Path to generated EPUB file, or None on failure.
    """
    try:
        # Import here to avoid circular imports
        from synth_data_gen import generate_data

        # Build config from pattern
        config = {
            "output_directory_base": str(output_dir),
            "output_set_name": "validation",
            "file_types": [
                {
                    "type": "epub",
                    "count": 1,
                    "epub_specific_settings": pattern.generator_config,
                }
            ],
        }

        # Generate
        generated_files = generate_data(config_obj=config)

        if generated_files:
            return Path(generated_files[0])

    except ImportError:
        # If generate_data not available, return None
        pass
    except Exception:
        pass

    return None


def validate_all_patterns(
    registry: Optional[PatternRegistry] = None,
    categories: Optional[List[str]] = None,
) -> List[ValidationResult]:
    """
    Validate all patterns (or patterns in specified categories).

    Args:
        registry: PatternRegistry instance.
        categories: Optional list of categories to validate.

    Returns:
        List of ValidationResult for each pattern.
    """
    registry = registry or PatternRegistry()
    results = []

    pattern_ids = registry.list_patterns()

    if categories:
        # Filter to specified categories
        pattern_ids = [
            pid
            for pid in pattern_ids
            if registry.get_pattern(pid).category in categories
        ]

    for pattern_id in pattern_ids:
        result = round_trip_validate(pattern_id, registry)
        results.append(result)

    return results


def generate_validation_report(results: List[ValidationResult]) -> str:
    """
    Generate a human-readable validation report.

    Args:
        results: List of ValidationResult from validate_all_patterns.

    Returns:
        Formatted report string.
    """
    lines = [
        "=" * 60,
        "EPUB Pattern Round-Trip Validation Report",
        "=" * 60,
        "",
    ]

    passed = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    lines.append(f"Total patterns: {len(results)}")
    lines.append(f"Passed: {len(passed)}")
    lines.append(f"Failed: {len(failed)}")
    lines.append("")

    if passed:
        lines.append("-" * 40)
        lines.append("PASSED:")
        for r in passed:
            lines.append(f"  ✓ {r.pattern_id}")
        lines.append("")

    if failed:
        lines.append("-" * 40)
        lines.append("FAILED:")
        for r in failed:
            lines.append(f"  ✗ {r.pattern_id}")
            lines.append(f"    Error: {r.error}")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)
