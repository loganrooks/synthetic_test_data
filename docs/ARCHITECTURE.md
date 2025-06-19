# synth_data_gen: System Architecture
**Version:** 1.1
**Last Updated:** 2025-06-19

## 1. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        synth_data_gen                          │
├─────────────────────────────────────────────────────────────────┤
│  Entry Point: generate_data()                                  │
│  ├── ConfigLoader (YAML + Schema Validation)                   │
│  └── MainGenerator (Orchestration)                             │
│      ├── EpubGenerator ──► Component System                    │
│      │   ├── ProseComponent                                    │
│      │   ├── HeaderComponent                                   │
│      │   ├── NotesComponent                                    │
│      │   ├── TableOfContentsComponent                          │
│      │   ├── ImageComponent                                    │
│      │   └── CitationComponent                                 │
│      ├── PdfGenerator ──► ReportLab Integration                │
│      └── MarkdownGenerator ──► Text Processing                 │
├─────────────────────────────────────────────────────────────────┤
│  BaseGenerator (Abstract Pattern)                              │
│  ├── _determine_count() (Unified Quantity Processing)          │
│  ├── validate_config()                                         │
│  └── get_default_specific_config()                             │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Component Responsibilities & Dependencies

### Core Layer (`synth_data_gen/core/`)
- **Purpose:** Foundational classes and configuration management
- **Components:** 
  - `BaseGenerator`: Abstract base for all format generators
  - `ConfigLoader`: YAML loading and JSON schema validation
  - `InvalidConfigError`: Exception handling
- **Dependencies:** PyYAML, jsonschema

### Generator Layer (`synth_data_gen/generators/`)
- **Purpose:** Format-specific document generation
- **Components:**
  - `MainGenerator`: Orchestrates multi-format generation
  - `EpubGenerator`: EPUB document creation with component system
  - `PdfGenerator`: PDF document creation with ReportLab
  - `MarkdownGenerator`: Markdown document creation
- **Dependencies:** ebooklib, reportlab, BaseGenerator

### EPUB Component Layer (`synth_data_gen/generators/epub_components/`)
- **Purpose:** Modular EPUB feature generation
- **Components:**
  - `EpubComponent`: Abstract base for all components
  - `ProseComponent`: Text content generation
  - `HeaderComponent`: Chapter headers with multiple styles
  - `NotesComponent`: Footnotes, endnotes, and annotations
  - `TableOfContentsComponent`: Navigation structure
  - `ImageComponent`: Multimedia content integration
  - `CitationComponent`: Bibliography and reference management
- **Dependencies:** ebooklib, EpubGenerator

### Utilities Layer (`synth_data_gen/common/`)
- **Purpose:** Shared functionality across generators
- **Components:** 
  - `utils.py`: Common helper functions
- **Dependencies:** None (internal utilities)

## 3. System Invariants (Non-Negotiable Rules)

1. **Generator Constructor Compatibility:** All generators MUST implement `__init__(self, global_config: dict, specific_config: dict)` to be compatible with MainGenerator orchestration.

2. **Component Interface Compliance:** All EPUB components MUST implement `render(self, book: epub.EpubBook, config: Dict[str, Any], chapters: List[epub.EpubHtml]) -> None` for the component system.

3. **Configuration-Driven Generation:** NO hardcoded variations allowed. All features must be configurable through the configuration system using the Unified Quantity Specification.

4. **Test Coverage Requirement:** All new generators and components MUST have corresponding test coverage with pytest before integration.

5. **BaseGenerator Inheritance:** All format generators MUST inherit from BaseGenerator and implement the required abstract methods.

6. **Probabilistic Determinism:** All probabilistic features MUST use the `_determine_count()` method from BaseGenerator to ensure consistent, testable behavior.

## 4. Data Flow Architecture

### Configuration Flow
```
YAML Config File → ConfigLoader → Schema Validation → MainGenerator → Format-Specific Generators → Components
```

### Generation Flow  
```
generate_data() → MainGenerator.generate() → {
  EpubGenerator.generate() → Component.render() loop → .epub file
  PdfGenerator.generate() → ReportLab operations → .pdf file  
  MarkdownGenerator.generate() → Text processing → .md file
}
```

### Error Handling Flow
```
Configuration Error → ConfigLoader → InvalidConfigError → User feedback
Generation Error → Generator → Logging → Graceful degradation
Component Error → Component → Logging → Feature skipping
```

## 5. Component Architecture (EPUB-Specific)

### Current State (Legacy)
- Monolithic functions like `create_epub_taylor_hegel_headers()`
- One function per style/variation
- Massive code duplication
- Non-combinatorial approach

### Target State (Component-Based)
```python
# Configuration-driven approach
chapter_config = {
    "title": "Chapter 1",
    "components": [
        {"type": "header", "style": "taylor_hegel", "number": "1"},
        {"type": "prose", "paragraphs": 5},
        {"type": "notes", "style": "footnotes_same_page", "count": {"min": 2, "max": 4}}
    ]
}
```

### Component Interaction Pattern
1. EpubGenerator creates empty EpubBook
2. For each chapter configuration:
   - Create EpubHtml chapter item
   - For each component in chapter:
     - Instantiate component class
     - Call component.render(book, component_config, chapters)
3. Components modify book or chapters as needed
4. EpubGenerator finalizes and writes EPUB

## 6. Testing Architecture

### Test Structure
```
tests/
├── core/                    # BaseGenerator, ConfigLoader tests
├── generators/              # Format generator integration tests  
│   ├── epub_components/     # Component unit tests
│   ├── test_epub_generator.py
│   ├── test_pdf_generator.py
│   └── test_markdown_generator.py
├── data/                    # Test fixtures and sample configs
└── test_integration_*.py    # End-to-end workflow tests
```

### Current Test Suite Status
- **Total Tests:** 220 (201 passing, 19 failing)
- **Pass Rate:** 91.4%
- **Test Framework:** pytest 8.3.5
- **Critical Failures:** Mocking issues in PDF and EPUB ToC tests

### Mocking Strategy
- Mock external libraries (ebooklib, reportlab) for unit tests
- Use real libraries for integration tests with `tmp_path`
- Mock `random.random` for deterministic probabilistic testing
- Spy on component interactions for behavior verification

### Known Test Issues
1. **PDF Generator Tests:** `_determine_count()` mocking complexity
2. **EPUB ToC Tests:** Mock book instances missing attributes
3. **EPUB Multimedia Tests:** Font obfuscation XML generation

## 7. Configuration Architecture

### Schema Validation
- JSON Schema defines valid configuration structure
- ConfigLoader enforces schema compliance
- Generator-specific validation for complex rules

### Unified Quantity Specification
```python
# Supported formats for count-based configurations
exact: 5
range: {"min": 2, "max": 6}
probabilistic: {
    "chance": 0.7,
    "if_true": {"min": 1, "max": 3},
    "if_false": 0,
    "max_total": 5
}
```

### Configuration Hierarchy
1. Default configuration (embedded in generators)
2. Global configuration (applies to all generators)  
3. Format-specific configuration (overrides global)
4. Component-specific configuration (overrides format)

## 8. Migration Architecture (Current Refactoring)

### Phase 0: Emergency Stabilization ✅ COMPLETED
- ✅ Fix generator constructor signatures
- ✅ Remove function redefinitions  
- ✅ Resolve import compatibility issues
- ⏸️ Address critical test failures (moved to Phase 1)

### Phase 1.5: Type Safety Sprint ✅ COMPLETED
- ✅ Install available type stubs (types-reportlab, types-PyYAML)
- ✅ Fix 112 missing Optional type hints
- ✅ Resolve critical type mismatches
- ✅ Reduce Pylance errors from 850 to ~143 (83% reduction)

### Phase 1: Test Suite Modernization 🔴 IN PROGRESS
- 🔴 Fix 19 failing tests (9 PDF, 9 EPUB ToC, 1 EPUB Multimedia)
- ⏳ Migrate from unittest to pytest
- ⏳ Fix probabilistic test failures
- ⏳ Implement proper test isolation
- ⏳ Achieve full test suite passing state

### Phase 2: Component System Implementation 📋 PENDING
- 📋 Implement EpubComponent base class
- 📋 Refactor existing functions to components
- 📋 Update EpubGenerator to use component system
- 📋 Remove legacy monolithic functions

### Phase 3: Documentation and Finalization 📋 PENDING
- 📋 Update specifications to reflect new architecture
- 📋 Complete documentation overhaul
- 📋 Performance optimization and final review

## 9. Dependency Architecture & Risk Management

**⚠️ CRITICAL: Before ANY file operations, consult `docs/analysis/system-dependencies.md`**

### Import Dependency Chain
```
MainGenerator → All Generators (epub, pdf, markdown)
EpubGenerator → All epub_components.*
All Generators → core.base, common.utils
```

### Critical Architectural Dependencies
1. **Constructor Interface:** All generators MUST implement `__init__(global_config, specific_config)`
2. **Component Imports:** epub.py depends on ALL epub_components modules  
3. **Utility Dependencies:** Multiple generators depend on common.utils functions
4. **Base Class Inheritance:** All generators inherit from BaseGenerator

### File Operation Risk Assessment
- **CRITICAL RISK:** Deleting generator files, epub_components, or utility files
- **HIGH RISK:** Changing import statements or function signatures
- **MEDIUM RISK:** Editing file contents without breaking interfaces
- **LOW RISK:** Adding new files or documentation updates

### Naming Pattern Intelligence  
- `*_clean.py`, `*_fix.py` → Often indicate IMPROVED versions (NEVER delete without analysis)
- `*.backup`, `*_old.py` → Typically deprecated versions (verify before removal)
- File size similarity ≠ redundancy (could be different implementations)

**MANDATORY:** All file deletions require dependency impact analysis documented in `docs/analysis/dependency-impact-FILENAME.md`

## 10. Scalability Considerations

### Horizontal Scaling
- New generators can be added by implementing BaseGenerator
- New EPUB components can be added by implementing EpubComponent
- Configuration system automatically supports new features

### Vertical Scaling  
- Component system enables complex document generation
- Probabilistic features support varied output generation
- Configuration-driven approach reduces code complexity

### Maintainability
- Clear separation of concerns between layers
- Abstract base classes enforce consistent interfaces
- Component-based approach reduces code duplication
- Test-driven development ensures reliability