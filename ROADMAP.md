# Roadmap

This document outlines the development roadmap for `synth_data_gen`.

## Current Version: 0.1.0 (Alpha)

The library is functional but has known limitations. All three generators (EPUB, PDF, Markdown) produce valid output files.

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

## Version 0.3.0 - Feature Completeness

**Focus:** Complete all generator features per specification

### PDF Generator
- [ ] Two-pass generation for accurate ToC page numbers
- [ ] Full OCR simulation (Gaussian noise, salt-and-pepper, blur)
- [ ] Complex table layouts (merged cells, nested tables)
- [ ] Image-based PDF generation (scanned document simulation)
- [ ] Form fields and interactive elements

### EPUB Generator
- [ ] Complete NCX and NavDoc support for all EPUB versions
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

## Version 0.4.0 - Extensibility

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
- [ ] Tutorial: Custom Generators
- [ ] Tutorial: Configuration Deep Dive
- [ ] Example gallery with sample outputs

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to the roadmap.

Priorities are determined by:
1. Bug severity and user impact
2. Feature requests from active users
3. Alignment with project goals
4. Maintainer availability

To propose a roadmap change, open an issue with the `roadmap` label.
