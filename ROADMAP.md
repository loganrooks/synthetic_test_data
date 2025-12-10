# Roadmap

This document outlines the development roadmap for `synth_data_gen`.

## Current Version: 0.1.0 (Alpha)

The library is functional but has known limitations. All three generators (EPUB, PDF, Markdown) produce valid output files.

---

## Deployment Readiness Checklist

This section tracks the immediate priorities to make the package deployment-ready.

### Phase 1 - Critical (Blocks Deployment)

| Task | Status | Notes |
|------|--------|-------|
| Fix 59 failing tests | ✅ Done | ConfigLoader API, EPUB components fixed |
| Write analyzer module tests | ✅ Done | 81 tests added (registry, analyzer, validation, CLI) |
| Set up GitHub Actions CI | ✅ Done | pytest, coverage, lint, type-check, build |
| Expand README with examples | ✅ Done | Installation, usage, YAML config, analyzer |

### Phase 2 - High Priority

| Task | Status | Notes |
|------|--------|-------|
| Add ruff/black/mypy configuration | ✅ Done | ruff + mypy configured in pyproject.toml |
| Complete type hints | ⬜ TODO | Currently ~50-60% coverage |
| Add CLI entry points | ✅ Done | synth-data, synth-analyze commands |
| Implement `add-patterns` command | ⬜ TODO | Currently stubbed in analyzer |

### Phase 3 - Release Prep

| Task | Status | Notes |
|------|--------|-------|
| Add LICENSE file | ⬜ TODO | Choose appropriate license |
| Add MANIFEST.in | ⬜ TODO | Package data files |
| Generate API docs | ⬜ TODO | Sphinx or MkDocs |
| Create CHANGELOG.md | ⬜ TODO | Document version history |
| Publish to TestPyPI | ⬜ TODO | Test package installation |
| Publish to PyPI | ⬜ TODO | Final release |

---

## Version 0.2.0 - Stability & Testing

**Focus:** Fix known issues, improve test coverage, stabilize API

### Must Have
- [ ] Fix PDF Visual ToC page number calculation (ISS-001)
- [ ] Resolve probabilistic test assertion issues (ISS-002)
- [ ] Create `default_config.yaml` with comprehensive defaults (ISS-008)
- [ ] Replace remaining `print()` with logging (ISS-006)
- [ ] Achieve 80%+ test coverage

### Should Have
- [ ] Consolidate ConfigLoader test files (ISS-007)
- [ ] Implement proper dot leader rendering (ISS-003)
- [ ] Add 180-degree page rotation support (ISS-004)
- [ ] Apply annotation font styling (ISS-005)

### Nice to Have
- [ ] Extract magic strings to constants/enums (ISS-009)
- [ ] Add type stubs for better IDE support
- [ ] Performance benchmarks for large document generation

---

## Version 0.3.0 - Combinatoric Test Generation

**Focus:** Flexible, comprehensive test data generation (see [ADR-001](adr/ADR-001-combinatoric-test-generation.md))

### Preset System (Tier 1)
- [ ] Design preset registry architecture
- [ ] Implement preset loading and merging
- [ ] Create presets derived from real EPUB analysis:
  - [ ] `epub2_calibre_basic` - Simple Calibre-converted EPUB2
  - [ ] `epub3_semantic` - Modern EPUB3 with semantic markup
  - [ ] `kant_critique_style` - Scholarly with dual footnotes, edition markers
  - [ ] `taylor_hegel_style` - Academic with same-page footnotes
  - [ ] `hegel_logic_style` - Complex with image-based symbols
  - [ ] `ocr_scanned_book` - PDF-like with OCR artifacts
  - [ ] `markdown_gfm` - GitHub Flavored Markdown
  - [ ] `markdown_academic` - With LaTeX, citations, frontmatter
- [ ] Preset override mechanism (`preset` + `overrides`)

### Feature Matrix (Tier 2)
- [ ] Implement matrix expansion algorithm
- [ ] Support wildcards in matrix values (`toc_style: "ncx_*"`)
- [ ] Add exclusion rules for invalid combinations
- [ ] Implement sampling for large matrices
- [ ] Add `--dry-run` preview mode

### Feature Catalog
- [ ] Document all EPUB features and valid values
  - [ ] ToC styles (9+ variants from analysis)
  - [ ] Header patterns (20+ variants)
  - [ ] Footnote/endnote systems (16+ variants)
  - [ ] Citation styles
  - [ ] Page marker formats
- [ ] Document all PDF features
- [ ] Document all Markdown features
- [ ] Auto-generate documentation from catalog

### Test Suite Generation
- [ ] `generate_test_suite()` API function
- [ ] Coverage report generation
- [ ] Integration with pytest fixtures

---

## Version 0.4.0 - Feature Completeness

**Focus:** Complete all generator features per specification

### PDF Generator
- [ ] Two-pass generation for accurate ToC page numbers
- [ ] Full OCR simulation (Gaussian noise, salt-and-pepper, blur)
- [ ] Complex table layouts (merged cells, nested tables)
- [ ] Image-based PDF generation (scanned document simulation)
- [ ] Form fields and interactive elements

### EPUB Generator
- [ ] Complete all 9+ ToC style implementations
- [ ] Complete all 16+ footnote/endnote patterns
- [ ] Complete all 20+ header formatting patterns
- [ ] Full multimedia support (audio, video references)
- [ ] Complex CSS styling options
- [ ] DRM simulation (encryption markers)
- [ ] EPUB validation integration

### Markdown Generator
- [ ] Full GFM (GitHub Flavored Markdown) support
- [ ] Wiki-style linking
- [ ] Math/LaTeX rendering options
- [ ] Diagram generation (Mermaid, PlantUML placeholders)

---

## Version 0.5.0 - Extensibility

**Focus:** Plugin system and custom generators

### Plugin Architecture
- [ ] Define plugin interface specification
- [ ] Plugin discovery and loading mechanism
- [ ] Plugin configuration schema
- [ ] Example plugin template

### New Generator Types
- [ ] HTML generator (standalone web pages)
- [ ] DOCX generator (Microsoft Word)
- [ ] RTF generator (Rich Text Format)
- [ ] Plain text generator (with configurable formatting)

### Configuration Enhancements
- [ ] JSON Schema for all configuration options
- [ ] Configuration validation CLI tool
- [ ] Configuration migration tool (version upgrades)

---

## Version 1.0.0 - Production Ready

**Focus:** API stability, documentation, packaging

### API Stability
- [ ] Freeze public API
- [ ] Semantic versioning enforcement
- [ ] Deprecation policy documentation

### Documentation
- [ ] Complete API reference documentation
- [ ] Tutorial: Getting Started
- [ ] Tutorial: Using Presets
- [ ] Tutorial: Feature Matrix Generation
- [ ] Tutorial: Custom Generators
- [ ] Tutorial: Configuration Deep Dive
- [ ] Example gallery with sample outputs

### CLI Tool
- [ ] `synth-data generate` - Generate files from config
- [ ] `synth-data matrix` - Expand and preview matrix
- [ ] `synth-data coverage` - Report feature coverage
- [ ] `synth-data presets` - List available presets
- [ ] `synth-data validate` - Validate configuration

### Distribution
- [ ] PyPI package publication
- [ ] Conda package
- [ ] Docker image for isolated generation
- [ ] GitHub Actions workflow for CI/CD

### Quality
- [ ] 90%+ test coverage
- [ ] Type checking with mypy (strict mode)
- [ ] Security audit
- [ ] Performance optimization

---

## Future Considerations (Post 1.0)

### Potential Features
- **Batch generation CLI** - Command-line tool for bulk document generation
- **Web UI** - Browser-based configuration and preview
- **Template system** - User-defined document templates
- **Content sources** - Integration with Lorem Ipsum APIs, Faker library
- **Corpus-based generation** - Generate documents mimicking real corpus statistics
- **Multilingual support** - RTL languages, CJK character sets
- **Accessibility features** - WCAG compliance testing data

### Integration Possibilities
- pytest plugin for automatic test fixture generation
- Hypothesis integration for property-based testing
- MLflow integration for ML pipeline testing

---

## Architecture Decision Records

- [ADR-001: Combinatoric Test Generation](adr/ADR-001-combinatoric-test-generation.md) - Three-tier configuration system

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to the roadmap.

Priorities are determined by:
1. Bug severity and user impact
2. Feature requests from active users
3. Alignment with project goals
4. Maintainer availability

To propose a roadmap change, open an issue with the `roadmap` label.
