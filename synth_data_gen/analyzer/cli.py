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

    for candidate in data["candidates"]:
        decision = candidate.get("decision")
        pattern_name = candidate.get("pattern_name")

        if decision == "skip":
            print(f"Skipping: {candidate.get('id', 'unknown')}")
            continue

        if decision == "new_pattern" and pattern_name:
            print(f"Adding new pattern: {pattern_name}")
            # TODO: Implement pattern addition to registry
            print("  ⚠ Pattern addition not yet implemented")

        if decision == "variant":
            base_pattern = candidate.get("base_pattern")
            print(f"Adding variant of {base_pattern}: {pattern_name}")
            # TODO: Implement variant addition
            print("  ⚠ Variant addition not yet implemented")

    if args.validate:
        print()
        print("Running round-trip validation...")
        # TODO: Validate newly added patterns

    return 0


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
