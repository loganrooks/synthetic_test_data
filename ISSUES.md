# Known Issues and Technical Debt

This document tracks known issues, bugs, and technical debt in the `synth_data_gen` project.

## Open Issues

### Low Priority

#### ISS-007: Duplicate test files for ConfigLoader
- **Location:** `tests/`
- **Description:** Multiple test files exist for ConfigLoader:
  - `tests/core/test_config_loader.py`
  - `tests/test_config_loader.py`
  - `tests/test_integration_config_loader.py`
- **Suggested Fix:** Consolidate into a single location with clear unit vs integration separation.

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

### RES-004: Missing default_config.yaml (ISS-008)
- **Resolved:** 2025-12-09
- **Description:** `ConfigLoader` referenced a `default_config.yaml` that didn't exist, causing fallback to empty config.
- **Fix:** Created comprehensive `synth_data_gen/core/default_config.yaml` with:
  - All configuration options documented with inline comments
  - EPUB, PDF, and Markdown defaults matching specification
  - Preset definitions for future combinatoric generation (ADR-001)
  - Sensible deterministic defaults for testability

### RES-005: Print statements replaced with logging (ISS-006)
- **Resolved:** 2025-12-09
- **Description:** Multiple modules used `print()` instead of proper logging.
- **Files Updated:**
  - `synth_data_gen/core/base.py` - 11 print statements
  - `synth_data_gen/common/utils.py` - 3 print statements
  - `synth_data_gen/generators/epub.py` - 8 print statements
  - `synth_data_gen/generators/pdf.py` - 11 print statements
  - `synth_data_gen/generators/markdown.py` - 3 print statements
- **Fix:** Replaced all print statements with appropriate `logger.error()`, `logger.warning()`, `logger.info()`, or `logger.debug()` calls.

### RES-006: 180-degree page rotation implemented (ISS-004)
- **Resolved:** 2025-12-09
- **Description:** PDF generator had TODO for handling 180-degree page rotation.
- **Fix:** Implemented using `canvas.setPageRotation()` in onPage handler. This sets the PDF /Rotate property which tells PDF readers to display the page rotated. Added page_rotation handling to combined_on_page_items system.

### RES-007: Annotation font styling now applied (ISS-005)
- **Resolved:** 2025-12-09
- **Description:** `_apply_handwritten_annotation` had duplicated code and a TODO section that used hardcoded "Helvetica" 10pt font instead of the configured annotation_font_family and other style settings.
- **Fix:** Removed ~60 lines of duplicated/incomplete code. The first implementation (lines 467-504) already correctly reads and applies:
  - `annotation_font_family`
  - `annotation_font_size_pt_range`
  - `annotation_color_rgb`
  - `annotation_opacity_range`
  - `annotation_rotation_degrees_range`
  - `annotation_text_options`

### RES-008: PDF Visual ToC now shows real page numbers (ISS-001)
- **Resolved:** 2025-12-09
- **Description:** Visual ToC used placeholders like `(PAGE_REF:ch_alpha_key)` instead of actual page numbers.
- **Root Cause:** PDF generation is sequential - ToC was built before chapter positions were known.
- **Fix:** Implemented two-pass PDF generation:
  - Created `TocAnchor` flowable class that records page numbers when rendered
  - Created `TocPlaceholder` flowable to reserve space in first pass
  - First pass builds to BytesIO, capturing page numbers via `TocAnchor.draw()`
  - Second pass rebuilds with actual page numbers from captured data
  - Updated `get_visual_toc_flowables()` to accept optional `page_numbers` dict

### RES-009: Probabilistic test random() call count fixed (ISS-002)
- **Resolved:** 2025-12-09
- **Description:** Tests expected 1 call to `random.random()` but received 2 calls. The issue was misdiagnosed as test flakiness.
- **Root Cause:** Line 142 in `pdf.py` called `random.random()` unconditionally:
  ```python
  if random.random() < mixed_chance:  # Always called even when mixed_chance is 0.0
  ```
- **Fix:** Added guard check to short-circuit when chance is zero:
  ```python
  if mixed_chance > 0.0 and random.random() < mixed_chance:
  ```
- **Tests Updated:** Changed expected call counts from 2 to 1 in:
  - `test_single_column_with_probabilistic_table_occurrence`
  - `test_generate_single_column_unified_chapters_probabilistic`

### RES-010: Visual ToC dot leaders properly rendered (ISS-003)
- **Resolved:** 2025-12-09
- **Description:** Dot leaders used static `" ..... "` or `...DOTS...` placeholder strings instead of proper fill.
- **Fix:** Implemented Table-based approach for proper dot leader rendering:
  - Created `_create_toc_entry_table()` helper method
  - Uses 3-column Table: [title, dot leaders, page number]
  - Calculates proper column widths based on available space
  - Generates dynamic dot patterns (` . ` repeated to fill space)
  - Updated Canvas-based implementation to calculate actual dot count based on stringWidth
  - Applies proper TableStyle for alignment (left, center, right)

---

## Contributing

When adding new issues:
1. Use the next available ISS-XXX number
2. Include location, description, impact, and suggested fix
3. Update status when work begins
4. Move to Resolved section when fixed, noting the commit hash
