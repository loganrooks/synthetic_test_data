# Product Context
<!-- Entries below should be added reverse chronologically (newest first) -->
[2025-05-11 02:14:27] - SpecPseudo - Product Context - The Synthetic Data Package will generate configurable and extensible synthetic test data (EPUB, PDF, Markdown) for testing RAG pipelines. Key features include a hybrid configuration system (YAML/Python), plugin architecture for new generators, and detailed control over EPUB formatting.

[2025-05-11 02:14:27] - SpecPseudo - Decision - Adopted a hybrid configuration approach (YAML for ease of use, Python dictionaries for programmatic control) for the Synthetic Data Package.
[2025-05-11 02:14:27] - SpecPseudo - Decision - Extensibility for new data generators will be handled via a plugin architecture using Python package entry points.

# System Patterns
<!-- Entries below should be added reverse chronologically (newest first) -->
### System Pattern: Dual-Mode Quantity Specification - 2025-05-11 02:35:00
- **Description**: A unified configuration pattern for specifying the quantity of generated sub-elements (e.g., chapters, footnotes, images, list items). This pattern allows for both deterministic (exact counts) and flexible (ranged or probabilistic) generation.
- **Structure**: For a configuration key representing a countable element (e.g., `num_chapters`, `footnote_config`), the value can be:
    1.  **Integer**: For an exact, deterministic count.
        Example: `num_chapters: 5`
    2.  **Object with `min` and `max` keys**: For a random count within an inclusive range.
        Example: `num_chapters: { min: 3, max: 7 }`
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