# Known Issues and Technical Debt

This document tracks known issues, bugs, and technical debt in the `synth_data_gen` project.

## Open Issues

### High Priority

#### ISS-001: PDF Visual ToC uses placeholder page numbers
- **Location:** `synth_data_gen/generators/pdf.py`
- **Description:** The Visual Table of Contents currently uses placeholders like `(PAGE_REF:ch_alpha_key)` instead of actual page numbers.
- **Root Cause:** Actual page numbers require a two-pass PDF generation approach where content is laid out first, then page numbers are calculated.
- **Impact:** ToC page numbers are not functional in generated PDFs.
- **Suggested Fix:** Implement two-pass PDF generation using ReportLab's `doctemplate` callbacks or post-processing.

#### ISS-002: Probabilistic test assertion count mismatches
- **Location:** `tests/generators/test_pdf_generator.py`
- **Description:** Some probabilistic tests expect 1 call to `random()` but receive 2 calls.
- **Affected Tests:**
  - `test_single_column_with_probabilistic_table_occurrence` (Scenario 2)
  - `test_single_column_with_probabilistic_figure_occurrence` (Scenario 2)
- **Status:** Diagnostic fixes applied (changed assertions to expect 2 calls). Root cause unclear.
- **Impact:** Tests pass but the underlying behavior may not be as intended.

#### ISS-003: Visual ToC dot leader rendering
- **Location:** `synth_data_gen/generators/pdf.py`
- **Description:** Dot leaders use a simple `...DOTS...` placeholder instead of proper ReportLab dot leader fill.
- **Suggested Fix:** Use ReportLab's `<seq id="dot"/>` or Table-based approach for proper dot leader rendering.

### Medium Priority

#### ISS-004: 180-degree page rotation not implemented
- **Location:** `synth_data_gen/generators/pdf.py:158`
- **Description:** TODO comment indicates 180-degree rotation handling is incomplete.
- **Code:**
  ```python
  # TODO: Handle 180 rotation if it means flipping content,
  # for now, it doesn't change dimensions.
  ```

#### ISS-005: Annotation font styling not used
- **Location:** `synth_data_gen/generators/pdf.py:534`
- **Description:** `annotation_font_family` and other style settings are not applied to handwritten annotations.
- **Code:**
  ```python
  # TODO: Use annotation_font_family and other style settings
  ```

#### ISS-006: Print statements remain in some modules
- **Location:** Various files in `synth_data_gen/`
- **Description:** Some modules still use `print()` instead of proper logging.
- **Affected Files:**
  - `synth_data_gen/core/base.py` - validation warnings
  - `synth_data_gen/generators/pdf.py` - various warnings
  - `synth_data_gen/generators/markdown.py` - error messages
- **Suggested Fix:** Replace with `logging` module calls.

### Low Priority

#### ISS-007: Duplicate test files for ConfigLoader
- **Location:** `tests/`
- **Description:** Multiple test files exist for ConfigLoader:
  - `tests/core/test_config_loader.py`
  - `tests/test_config_loader.py`
  - `tests/test_integration_config_loader.py`
- **Suggested Fix:** Consolidate into a single location with clear unit vs integration separation.

#### ISS-008: Missing default_config.yaml
- **Location:** `synth_data_gen/core/`
- **Description:** `ConfigLoader` references a `default_config.yaml` that doesn't exist.
- **Impact:** Falls back to empty config, which may cause issues.
- **Suggested Fix:** Create a comprehensive default configuration file.

#### ISS-009: Magic strings throughout codebase
- **Description:** Configuration values like `"single_column_text"`, `"footnotes_same_page"`, `"yaml"` are scattered as string literals.
- **Suggested Fix:** Create `constants.py` or use `Enum` classes.

---

## Resolved Issues

### RES-001: Duplicate `_determine_count()` in EpubGenerator
- **Resolved:** 2025-12-09
- **Commit:** `e0f99c5`
- **Description:** EpubGenerator had its own simplified `_determine_count()` that didn't support full probabilistic logic.
- **Fix:** Removed duplicate, now inherits from BaseGenerator.

### RES-002: ConfigLoader signature mismatch
- **Resolved:** 2025-12-09
- **Commit:** `071738a`
- **Description:** `__init__.py` called `load_and_validate_config()` with `config_override_object` parameter that didn't exist.
- **Fix:** Added `config_override_object` parameter to ConfigLoader.

### RES-003: Missing runtime dependencies in pyproject.toml
- **Resolved:** 2025-12-09
- **Commit:** `6dd7add`
- **Description:** pyproject.toml listed test dependencies as runtime deps and was missing actual runtime deps.
- **Fix:** Added ebooklib, reportlab, PyYAML, jsonschema; moved test deps to `[dev]` extras.

---

## Contributing

When adding new issues:
1. Use the next available ISS-XXX number
2. Include location, description, impact, and suggested fix
3. Update status when work begins
4. Move to Resolved section when fixed, noting the commit hash
