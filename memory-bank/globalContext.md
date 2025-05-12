# Product Context
<!-- Entries below should be added reverse chronologically (newest first) -->
[2025-05-11 02:14:27] - SpecPseudo - Product Context - The Synthetic Data Package will generate configurable and extensible synthetic test data (EPUB, PDF, Markdown) for testing RAG pipelines. Key features include a hybrid configuration system (YAML/Python), plugin architecture for new generators, and detailed control over EPUB formatting.

[2025-05-11 02:14:27] - SpecPseudo - Decision - Adopted a hybrid configuration approach (YAML for ease of use, Python dictionaries for programmatic control) for the Synthetic Data Package.
[2025-05-11 02:14:27] - SpecPseudo - Decision - Extensibility for new data generators will be handled via a plugin architecture using Python package entry points.

# System Patterns
<!-- Entries below should be added reverse chronologically (newest first) -->
### System Pattern: Class-Based Generator Architecture - 2025-05-11 05:01:49
- **Description**: A class-based architecture for synthetic data generation, featuring an abstract `BaseGenerator` and concrete implementations (`EpubGenerator`, `PdfGenerator`, `MarkdownGenerator`). The main `generate_data` function orchestrates these generators based on a configuration object.
- **Components**:
    - `synth_data_gen.core.base.BaseGenerator`: Abstract base class defining the generator interface (`generate`, `validate_config`, `get_default_specific_config`, `GENERATOR_ID`).
    - `synth_data_gen.generators.epub.EpubGenerator`: Concrete generator for EPUB files.
    - `synth_data_gen.generators.pdf.PdfGenerator`: Concrete generator for PDF files.
    - `synth_data_gen.generators.markdown.MarkdownGenerator`: Concrete generator for Markdown files.
    - `synth_data_gen.ConfigLoader` (stub): Responsible for loading and validating configurations.
    - `synth_data_gen.generate_data()`: Main entry point, uses `ConfigLoader` and dispatches to appropriate generators.
- **Rationale**: Aligns with the package specification, promotes modularity, extensibility (for future generators and plugins), and better organization of code compared to the previous script-based approach. Facilitates easier testing of individual generator components.
- **Impact**: Significant refactoring of the `synth_data_gen` package. Existing generation logic is now encapsulated within classes. The main entry point is simplified.
- **Files Affected**: `synth_data_gen/__init__.py`, `synth_data_gen/core/base.py`, `synth_data_gen/generators/epub.py`, `synth_data_gen/generators/pdf.py`, `synth_data_gen/generators/markdown.py`.
### System Pattern: Dual-Mode Quantity Specification - 2025-05-11 02:35:00
- **Description**: A unified configuration pattern for specifying the quantity of generated sub-elements (e.g., chapters, footnotes, images, list items). This pattern allows for both deterministic (exact counts) and flexible (ranged or probabilistic) generation.
- **Structure**: For a configuration key representing a countable element (e.g., `num_chapters`, `footnote_config`), the value can be:
    1.  **Integer**: For an exact, deterministic count.
        Example: `num_chapters: 5`
    2.  **Object with `min` and `max` keys**: For a random count within an inclusive range.
        Example: `num_chapters: { min: 3, max: 7 }`
### Progress: PDF Generator Test `test_generate_single_column_unified_chapters_range` Fixed - 2025-05-11 19:00:00
- **Status**: Completed
- **Details**: The test `test_generate_single_column_unified_chapters_range` in `tests/generators/test_pdf_generator.py` was fixed. The primary issue was a duplicated block of test code causing `PdfGenerator.generate()` to be called twice, leading to an `AssertionError` for `random.randint` call count. Subsequent `NameError` issues were also resolved. All 10 tests in `tests/generators/test_pdf_generator.py` now pass.
- **Impact**: Corrected a failing test, ensuring `PdfGenerator`'s chapter generation with range-based config is accurately tested.
- **Next Steps**: Continue with TDD for PDF generator, focusing on probabilistic chapter counts, then other generator features. [See Active Context: 2025-05-11 19:00:00]
### Progress: EPUB Generator Test `test_generate_adds_basic_toc_items` Fixed - 2025-05-11 07:47:46
- **Status**: Completed
- **Details**: The failing test `test_generate_adds_basic_toc_items` in `tests/generators/test_epub_generator.py` was investigated and fixed. The root cause was a misconfiguration in the test setup for EPUB 3 when EPUB 2 NCX generation behavior was intended. The test was updated to correctly reflect an EPUB 2 scenario, and its assertions were adjusted accordingly. All 21 tests in the suite now pass.
- **Impact**: Corrected a failing test, ensuring the EPUB generator's ToC logic for EPUB 2 (NCX primary) is accurately tested.
- **Next Steps**: Continue with TDD for EPUB generator components. [See Active Context: 2025-05-11 07:46:20]
### Progress: Refactor to Class-Based Generator Architecture - 2025-05-11 05:01:49
- **Status**: Completed
- **Details**: Refactored the `synth_data_gen` package to align with the class-based architecture defined in [`specifications/synthetic_data_package_specification.md`](specifications/synthetic_data_package_specification.md).
  - Created `synth_data_gen.core.base.BaseGenerator` abstract class.
  - Implemented `synth_data_gen.generators.epub.EpubGenerator`.
  - Implemented `synth_data_gen.generators.pdf.PdfGenerator`.
  - Implemented `synth_data_gen.generators.markdown.MarkdownGenerator`.
  - Updated `synth_data_gen.__init__.py` to use these generator classes, along with a stubbed `ConfigLoader`.
  - Existing generation logic from individual functions/scripts moved into the respective generator classes.
- **Impact**: The package now follows a more modular and extensible class-based design. The main `generate_data` function orchestrates generation through these classes.
- **Next Steps**: Detailed integration of `epub_components` into `EpubGenerator`, full implementation of `ConfigLoader` and `PluginManager`, followed by comprehensive unit testing for each generator class. [See Active Context: 2025-05-11 04:56:18]
    3.  **Object with `chance` key**: For probabilistic generation.
        - `chance`: (float, 0.0-1.0) Probability of occurrence.
        - `per_unit_of`: (string, optional) Defines the scope of the `chance` (e.g., "paragraph", "chapter", "document"). Context-dependent.
        - `max_total`: (integer, optional) An overall cap on the number of generated elements.
        Example: `num_footnotes: { chance: 0.1, per_unit_of: "paragraph", max_total: 20 }`
- **Rationale**: This pattern addresses the need for precise control for unit testing and scenario generation, while retaining the flexibility of probabilistic/ranged generation for creating diverse datasets. It standardizes how quantities are defined across different generator types and elements.
- **Impact**: Requires updates to the configuration schema definition in the package specification and modifications to generator logic to interpret this flexible quantity type.

# Decision Log
<!-- Entries below should be added reverse chronologically (newest first) -->

# Progress
### Progress: PDF Test `test_generate_single_column_unified_chapters_range` NameError Fixed - 2025-05-11 18:24:30
- **Status**: Completed
- **Details**: Resolved `NameError: name 'mock_determine_count' is not defined` in `tests.generators.test_pdf_generator.TestPdfGenerator.test_generate_single_column_unified_chapters_range` (at line 302). The error occurred because `mock_determine_count` was used without being defined in the test method's scope. The fix involved commenting out the problematic line: `mock_determine_count.side_effect = None`. Issue ID: PDF_TEST_NAMEERROR_MOCK_DETERMINE_COUNT. This followed a previous fix for Issue ID: PDF_RANDINT_DOUBLE_CALL in the same test.
- **Impact**: Corrected a `NameError` in the test, allowing it to proceed further. The original intent of the line was likely to ensure the original `_determine_count` method runs, which is the default if not mocked.
- **Next Steps**: Re-run the test to confirm the fix and ensure no other errors surface.
### Progress: PDF Generator Test `test_generate_single_column_unified_chapters_range` randint Double Call Fixed - 2025-05-11 18:48:00
- **Status**: Completed
- **Details**: Resolved `AssertionError: Expected 'randint' to be called once. Called 2 times.` in `tests.generators.test_pdf_generator.TestPdfGenerator.test_generate_single_column_unified_chapters_range`. Initial diagnosis pointing to a commented-out duplicate call at line 255 of the test was incorrect. Logging revealed the true root cause: the test method contained a second, distinct block of code (lines 306-321) that re-configured and called `self.generator.generate()` again. This second block was removed from [`tests/generators/test_pdf_generator.py`](tests/generators/test_pdf_generator.py:306). This ensures `synth_data_gen.core.base.random.randint` is called only once as expected. Issue ID: PDF_RANDINT_DOUBLE_CALL. [See Debug Issue History: PDF_RANDINT_DOUBLE_CALL]
- **Impact**: Corrected a failing test by removing an erroneous duplicate test execution within the same test method, ensuring accurate testing of range-based `chapters_config` in `PdfGenerator`.
- **Next Steps**: Verify fix by re-running the test. Remove temporary logging statements.
### Progress: Code Migration to Package Structure - 2025-05-11 04:47:17
- **Status**: Completed
- **Details**: Migrated all Python source files from the project root and `epub_generators/` subdirectory into the `synth_data_gen` package.
  - `common.py` -> `synth_data_gen/common/utils.py`
  - `generate_*.py` scripts -> `synth_data_gen/generators/*.py`
  - `epub_generators/*` -> `synth_data_gen/generators/epub_components/*`
  - Created `__init__.py` files in new subdirectories.
  - Updated all relative import statements to reflect the new package structure.
  - Integrated the main orchestration logic from `generate_all_data.py` into `synth_data_gen/__init__.py`'s `generate_data` function.
  - Deleted original (now redundant) files from the project root and `epub_generators/`.
  - All changes committed to Git.
- **Impact**: Code is now organized within the `synth_data_gen` package, making it a proper Python package. Import paths are corrected. The main entry point `synth_data_gen.generate_data()` now encapsulates the previous top-level script's functionality.
- **Next Steps**: Further refactoring of the migrated code into classes as per the specification ([`specifications/synthetic_data_package_specification.md`](specifications/synthetic_data_package_specification.md)).
### Decision: Adopt Dual-Mode Quantity Specification for Element Counts - 2025-05-11 02:35:00
- **Decision**: The configuration system for the `synthetic_test_data` package will adopt a "Dual-Mode Quantity Specification" pattern for all sub-element counts (e.g., chapters, footnotes, images).
- **Rationale**: This addresses a critical requirement highlighted by `spec-pseudocode` feedback ([`memory-bank/feedback/spec-pseudocode-feedback.md:3`](memory-bank/feedback/spec-pseudocode-feedback.md:3)). The previous specification's reliance on purely probabilistic counts (e.g., `note_occurrence_chance`) was insufficient for unit testing, which requires deterministic control. The dual-mode approach allows users to specify:
    1.  An exact integer for precise counts.
    2.  A min/max range for bounded random counts.
    3.  A probabilistic configuration (chance, per_unit_of, max_total) for flexible, varied generation.
- **Alternatives Considered**:
    - Separate configuration keys for deterministic vs. probabilistic counts: Rejected as it would bloat the configuration schema and make it less intuitive.
    - Complex conditional logic within generators: Rejected as it would make generator implementation more complex and error-prone than a unified input structure.
- **Impact**:
    - The package specification ([`specifications/synthetic_data_package_specification.md`](specifications/synthetic_data_package_specification.md)) needs to be updated by `spec-pseudocode` to reflect this new configuration pattern for all relevant quantity-related fields.
    - Generator logic (`EpubGenerator`, `PdfGenerator`, `MarkdownGenerator`, and any custom generators) will need to be updated to parse and correctly interpret this unified quantity specification.
    - Improves testability and user control significantly.
- **Stakeholders**: `architect` (proposer), `spec-pseudocode` (implementer in spec), `code` (implementer in generators).
<!-- Entries below should be added reverse chronologically (newest first) -->