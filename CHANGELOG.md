# Changelog

All notable changes to synth_data_gen will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Claude Code Development System Bootstrap implementation
- Systematic development workflow with SPARC-V-L³ protocol
- Comprehensive project documentation system
- Activity, feedback, and self-analysis logging
- Emergency stabilization plan for critical issues
- Constructor methods for all generator classes (EpubGenerator, PdfGenerator, MarkdownGenerator)

### Changed
- CLAUDE.md restructured to follow bootstrap template
- Development workflow now requires systematic verification protocols

### Fixed
- Generator constructor TypeError - all generators now accept (global_config, specific_config)
- Function redefinition errors in pdf.py (removed 5 duplicate functions, 578 lines)
- Function redefinition errors in toc.py (removed 2 duplicate functions, 164 lines)
- Import failures for all generator classes

### Infrastructure
- Created directory structure for systematic documentation
- Established log-based development tracking system
- Implemented verification protocols for high-risk operations
- Phase 0 emergency stabilization completed successfully

## [0.1.0] - Initial Project State

### Added
- Basic synthetic data generation package structure
- MainGenerator orchestration system
- BaseGenerator abstract pattern
- EpubGenerator with component-based architecture foundation
- PdfGenerator for PDF document creation
- MarkdownGenerator for markdown document creation
- ConfigLoader with YAML and JSON schema validation
- pytest test suite structure

### Known Issues
- Generator constructor incompatibility with MainGenerator
- Function redefinitions in pdf.py and toc.py
- Three failing PDF generator tests
- Missing Optional type hints
- Monolithic EPUB component functions (legacy debt)

### Architecture
- Component-based design goals established
- Unified quantity specification for probabilistic features
- Configuration-driven generation approach
- Modular generator pattern with inheritance

---

## Release Planning

### v0.2.0 - Emergency Stabilization (Target: This Week)
- Fix all generator constructor compatibility issues
- Remove function redefinitions
- Achieve green test suite status
- Complete transition to systematic development workflow

### v0.5.0 - Test Suite Modernization (Target: Next Week)  
- Complete unittest to pytest migration
- Implement proper test isolation
- Fix probabilistic test issues
- Establish CI/CD pipeline

### v1.0.0 - Component Architecture (Target: This Month)
- Implement complete component-based EPUB generation
- Remove legacy monolithic functions
- Full configuration-driven feature generation
- Complete documentation and specifications update