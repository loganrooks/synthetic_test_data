"""
CLI interface for EPUB Pattern Analyzer.

Provides commands for:
- discover: Analyze EPUBs and identify patterns
- add-patterns: Add new patterns from candidates.yaml
- validate: Run round-trip validation
- coverage: Generate coverage report
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import List, Optional

from .registry import PatternRegistry
from .epub_analyzer import EpubAnalyzer
from .validation import validate_all_patterns, generate_validation_report


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for synth-analyze CLI."""
    parser = argparse.ArgumentParser(
        prog="synth-analyze",
        description="EPUB Pattern Analyzer - detect and validate formatting patterns",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # discover command
    discover_parser = subparsers.add_parser(
        "discover", help="Analyze EPUB(s) and identify patterns"
    )
    discover_parser.add_argument(
        "epub_path", type=Path, help="Path to EPUB file or directory"
    )
    discover_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("candidates.yaml"),
        help="Output file for unknown patterns (default: candidates.yaml)",
    )

    # add-patterns command
    add_parser = subparsers.add_parser(
        "add-patterns", help="Add patterns from candidates file"
    )
    add_parser.add_argument(
        "candidates_file", type=Path, help="Path to candidates.yaml"
    )
    add_parser.add_argument(
        "--validate",
        action="store_true",
        help="Run round-trip validation after adding",
    )

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Run round-trip validation on patterns"
    )
    validate_parser.add_argument(
        "--category",
        type=str,
        action="append",
        dest="categories",
        help="Only validate patterns in specified categories",
    )
    validate_parser.add_argument(
        "--pattern",
        type=str,
        action="append",
        dest="patterns",
        help="Only validate specific patterns",
    )

    # coverage command
    coverage_parser = subparsers.add_parser(
        "coverage", help="Show pattern coverage for EPUB(s)"
    )
    coverage_parser.add_argument(
        "epub_path", type=Path, help="Path to EPUB file or directory"
    )

    # list command
    list_parser = subparsers.add_parser("list", help="List all registered patterns")
    list_parser.add_argument(
        "--category", type=str, help="Filter by category"
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.command is None:
        parser.print_help()
        return 1

    if parsed_args.command == "discover":
        return cmd_discover(parsed_args)
    elif parsed_args.command == "add-patterns":
        return cmd_add_patterns(parsed_args)
    elif parsed_args.command == "validate":
        return cmd_validate(parsed_args)
    elif parsed_args.command == "coverage":
        return cmd_coverage(parsed_args)
    elif parsed_args.command == "list":
        return cmd_list(parsed_args)

    return 1


def cmd_discover(args: argparse.Namespace) -> int:
    """Handle discover command."""
    registry = PatternRegistry()
    analyzer = EpubAnalyzer(registry)

    epub_path = args.epub_path

    print(f"Analyzing: {epub_path}")
    print()

    if epub_path.is_file():
        results = [analyzer.analyze(epub_path)]
    elif epub_path.is_dir():
        results = analyzer.analyze_batch(epub_path)
    else:
        print(f"Error: Path not found: {epub_path}")
        return 1

    all_unknown = []

    for result in results:
        print(f"File: {result.epub_path}")
        print(f"EPUB Version: {result.epub_version}")
        print()

        matched = [m for m in result.detected_patterns if m.matched]
        if matched:
            print("Detected Known Patterns:")
            for match in matched:
                print(f"  ✓ {match.pattern_id}")
                for evidence in match.evidence:
                    print(f"      {evidence}")
            print()

        if result.unknown_patterns:
            print("Unrecognized Elements Found:")
            for unknown in result.unknown_patterns:
                print(f"  ⚠ {unknown.category}: Novel pattern detected")
                all_unknown.append(
                    {
                        "epub": str(result.epub_path),
                        "category": unknown.category,
                        "detected_signature": unknown.detected_signature,
                        "evidence": unknown.evidence,
                        "similar_patterns": unknown.similar_patterns,
                    }
                )
            print()

        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  ✗ {error}")
            print()

        print("-" * 40)

    # Write candidates file if unknown patterns found
    if all_unknown:
        candidates = {"candidates": all_unknown}
        with open(args.output, "w", encoding="utf-8") as f:
            yaml.dump(candidates, f, default_flow_style=False, allow_unicode=True)
        print(f"\nWriting candidates to: {args.output}")

    return 0


def cmd_add_patterns(args: argparse.Namespace) -> int:
    """Handle add-patterns command."""
    from .registry import PatternDefinition

    candidates_file = args.candidates_file

    if not candidates_file.exists():
        print(f"Error: File not found: {candidates_file}")
        return 1

    print(f"Processing {candidates_file}...")
    print()

    with open(candidates_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "candidates" not in data:
        print("Error: No candidates found in file")
        return 1

    registry = PatternRegistry()
    added_patterns = []
    errors = []

    for candidate in data["candidates"]:
        decision = candidate.get("decision")
        pattern_name = candidate.get("pattern_name")

        if decision == "skip":
            print(f"  ⊘ Skipping: {candidate.get('id', 'unknown')}")
            continue

        if decision == "new_pattern" and pattern_name:
            # Create new pattern from candidate data
            try:
                pattern = _create_pattern_from_candidate(pattern_name, candidate)
                if registry.add_pattern(pattern):
                    file_path = registry.save_pattern_to_file(pattern)
                    print(f"  ✓ Added new pattern: {pattern_name}")
                    print(f"    Saved to: {file_path}")
                    added_patterns.append(pattern_name)
                else:
                    print(f"  ✗ Pattern already exists: {pattern_name}")
                    errors.append(f"Pattern {pattern_name} already exists")
            except Exception as e:
                print(f"  ✗ Error adding {pattern_name}: {e}")
                errors.append(str(e))

        elif decision == "variant" and pattern_name:
            base_pattern_id = candidate.get("base_pattern")
            if not base_pattern_id:
                print(f"  ✗ Variant requires base_pattern: {pattern_name}")
                errors.append(f"Missing base_pattern for {pattern_name}")
                continue

            base_pattern = registry.get_pattern(base_pattern_id)
            if not base_pattern:
                print(f"  ✗ Base pattern not found: {base_pattern_id}")
                errors.append(f"Base pattern {base_pattern_id} not found")
                continue

            try:
                pattern = _create_variant_pattern(pattern_name, base_pattern, candidate)
                if registry.add_pattern(pattern):
                    file_path = registry.save_pattern_to_file(pattern)
                    print(f"  ✓ Added variant: {pattern_name} (based on {base_pattern_id})")
                    print(f"    Saved to: {file_path}")
                    added_patterns.append(pattern_name)
                else:
                    print(f"  ✗ Pattern already exists: {pattern_name}")
                    errors.append(f"Pattern {pattern_name} already exists")
            except Exception as e:
                print(f"  ✗ Error adding variant {pattern_name}: {e}")
                errors.append(str(e))

    print()
    print(f"Summary: {len(added_patterns)} patterns added, {len(errors)} errors")

    if args.validate and added_patterns:
        print()
        print("Running round-trip validation on new patterns...")
        for pattern_id in added_patterns:
            result = round_trip_validate(pattern_id, registry)
            status = "✓" if result.success else "✗"
            print(f"  {status} {pattern_id}")
            if not result.success and result.error:
                print(f"      {result.error}")

    return 1 if errors else 0


def _create_pattern_from_candidate(
    pattern_id: str, candidate: dict
) -> "PatternDefinition":
    """Create a PatternDefinition from candidate data."""
    from .registry import PatternDefinition

    return PatternDefinition(
        id=pattern_id,
        category=candidate.get("category", "unknown"),
        description=candidate.get("description", ""),
        detection_signature=candidate.get("detected_signature", {}),
        source_examples=candidate.get("source_examples", []),
        epub_versions=candidate.get("epub_versions", [2, 3]),
        requires=set(candidate.get("requires", [])),
        conflicts_with=set(candidate.get("conflicts_with", [])),
        generator_config=candidate.get("generator_config", {}),
    )


def _create_variant_pattern(
    pattern_id: str, base_pattern: "PatternDefinition", candidate: dict
) -> "PatternDefinition":
    """Create a variant pattern based on an existing pattern."""
    from .registry import PatternDefinition

    # Start with base pattern values, override with candidate data
    return PatternDefinition(
        id=pattern_id,
        category=candidate.get("category", base_pattern.category),
        description=candidate.get("description", f"Variant of {base_pattern.id}"),
        detection_signature={
            **base_pattern.detection_signature,
            **candidate.get("detected_signature", {}),
        },
        source_examples=candidate.get("source_examples", []),
        epub_versions=candidate.get("epub_versions", base_pattern.epub_versions),
        requires=set(candidate.get("requires", list(base_pattern.requires))),
        conflicts_with=set(candidate.get("conflicts_with", list(base_pattern.conflicts_with))),
        generator_config={
            **base_pattern.generator_config,
            **candidate.get("generator_config", {}),
        },
    )


def round_trip_validate(pattern_id: str, registry: PatternRegistry):
    """Import and run round-trip validation."""
    from .validation import round_trip_validate as _validate
    return _validate(pattern_id, registry)


def cmd_validate(args: argparse.Namespace) -> int:
    """Handle validate command."""
    registry = PatternRegistry()

    print("Running round-trip validation...")
    print()

    results = validate_all_patterns(registry, categories=args.categories)

    # Filter to specific patterns if requested
    if args.patterns:
        results = [r for r in results if r.pattern_id in args.patterns]

    report = generate_validation_report(results)
    print(report)

    # Return non-zero if any failures
    failures = [r for r in results if not r.success]
    return 1 if failures else 0


def cmd_coverage(args: argparse.Namespace) -> int:
    """Handle coverage command."""
    registry = PatternRegistry()
    analyzer = EpubAnalyzer(registry)

    epub_path = args.epub_path

    if epub_path.is_file():
        results = [analyzer.analyze(epub_path)]
    elif epub_path.is_dir():
        results = analyzer.analyze_batch(epub_path)
    else:
        print(f"Error: Path not found: {epub_path}")
        return 1

    # Aggregate coverage across all files
    all_matched = set()
    for result in results:
        all_matched.update(result.get_matched_pattern_ids())

    # Get all patterns by category
    all_categories = registry.get_all_categories()

    print("Pattern Coverage Report")
    print("=" * 60)
    print()

    total_patterns = 0
    total_covered = 0

    for category in all_categories:
        patterns = registry.get_patterns_by_category(category)
        covered = [p for p in patterns if p.id in all_matched]

        total_patterns += len(patterns)
        total_covered += len(covered)

        covered_pct = (len(covered) / len(patterns) * 100) if patterns else 0
        print(f"{category}: {len(covered)}/{len(patterns)} ({covered_pct:.0f}%)")

        for pattern in patterns:
            marker = "✓" if pattern.id in all_matched else " "
            print(f"  [{marker}] {pattern.id}")

        print()

    overall_pct = (total_covered / total_patterns * 100) if total_patterns else 0
    print("-" * 60)
    print(f"Overall: {total_covered}/{total_patterns} ({overall_pct:.0f}%)")

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """Handle list command."""
    registry = PatternRegistry()

    if args.category:
        patterns = registry.get_patterns_by_category(args.category)
        print(f"Patterns in category '{args.category}':")
    else:
        patterns = [registry.get_pattern(pid) for pid in registry.list_patterns()]
        print("All registered patterns:")

    print()

    current_category = None
    for pattern in patterns:
        if pattern.category != current_category:
            current_category = pattern.category
            if not args.category:
                print(f"\n[{current_category}]")

        print(f"  {pattern.id}")
        print(f"    {pattern.description}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
