# Changelog

For detailed release notes, see [CHANGELOG.md](https://github.com/synth-data-gen/synth_data_gen/blob/main/CHANGELOG.md) in the repository.

## Recent Changes

### [Unreleased]

#### Added
- EPUB Pattern Analyzer module for detecting formatting patterns in EPUB files
- Comprehensive test suite (326 tests)
- GitHub Actions CI workflow with multi-version Python testing
- Code quality tools: ruff, mypy configuration
- CLI entry points: `synth-data`, `synth-analyze`

#### Changed
- Improved type hints across core modules
- Updated ConfigLoader API for better consistency

### [0.1.0] - 2025-12-10

Initial release with:

- EPUB generator (EPUB 2/3, ToC styles, footnotes, font embedding)
- PDF generator (Visual ToC, page layouts, annotations)
- Markdown generator (GFM support)
- Configuration system with YAML/JSON support
- Base generator architecture for extensibility
