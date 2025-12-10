# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- EPUB Pattern Analyzer module for detecting formatting patterns in EPUB files
  - PatternRegistry for managing pattern definitions
  - EpubAnalyzer for pattern detection
  - Round-trip validation for generated patterns
  - CLI commands: `synth-analyze discover`, `synth-analyze add-patterns`, `synth-analyze validate`
- Comprehensive test suite (326 tests)
- GitHub Actions CI workflow with multi-version Python testing
- Code quality tools: ruff, mypy configuration
- CLI entry points: `synth-data`, `synth-analyze`

### Changed
- Improved type hints across core modules
- Updated ConfigLoader API for better consistency

### Fixed
- EPUB component tuple unpacking issues
- PDF Visual ToC page number calculation
- Annotation font styling

## [0.1.0] - 2025-12-10

### Added
- Initial release
- EPUB generator with support for:
  - EPUB 2 and EPUB 3 formats
  - Multiple ToC styles (NCX, NavDoc, HTML)
  - Footnotes and endnotes systems
  - Font embedding with obfuscation
  - Image embedding
  - Various header patterns
- PDF generator with support for:
  - Visual Table of Contents
  - Configurable page layouts
  - Headers and footers
  - Page rotation
  - Annotations
- Markdown generator with support for:
  - GFM (GitHub Flavored Markdown)
  - Various section structures
  - Code blocks and lists
- Configuration system:
  - YAML/JSON configuration files
  - Probabilistic quantity specification
  - Deep config merging
- Base generator architecture for extensibility

### Dependencies
- ebooklib >= 0.18
- reportlab >= 4.0
- PyYAML >= 6.0
- jsonschema >= 4.0

[Unreleased]: https://github.com/synth-data-gen/synth_data_gen/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/synth-data-gen/synth_data_gen/releases/tag/v0.1.0
