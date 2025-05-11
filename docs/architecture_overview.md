# Synthetic Data Package - Architecture Overview

This document outlines key architectural patterns and decisions for the `synthetic_test_data` package.

## Core Architectural Goals

*   **Configurability**: Allow users to define a wide variety of synthetic data generation tasks through a clear and flexible configuration system.
*   **Extensibility**: Enable the addition of new data generators (e.g., for new file formats or content types) and new formatting options with minimal friction.
*   **Testability**: Ensure that generated data can be precisely controlled for reliable unit and integration testing.
*   **Realism**: Produce synthetic data that mimics the complexity and variety of real-world documents.

## Key System Patterns

### System Pattern: Dual-Mode Quantity Specification
- **Date**: 2025-05-11
- **Description**: A unified configuration pattern for specifying the quantity of generated sub-elements (e.g., chapters, footnotes, images, list items). This pattern allows for both deterministic (exact counts) and flexible (ranged or probabilistic) generation.
- **Structure**: For a configuration key representing a countable element (e.g., `num_chapters`, `footnote_config`), the value can be:
    1.  **Integer**: For an exact, deterministic count.
        *Example*: `num_chapters: 5`
    2.  **Object with `min` and `max` keys**: For a random count within an inclusive range.
        *Example*: `num_chapters: { "min": 3, "max": 7 }`
    3.  **Object with `chance` key**: For probabilistic generation.
        - `chance`: (float, 0.0-1.0) Probability of occurrence.
        - `per_unit_of`: (string, optional) Defines the scope of the `chance` (e.g., "paragraph", "chapter", "document"). Context-dependent.
        - `max_total`: (integer, optional) An overall cap on the number of generated elements.
        *Example*: `num_footnotes: { "chance": 0.1, "per_unit_of": "paragraph", "max_total": 20 }`
- **Rationale**: This pattern addresses the need for precise control for unit testing and scenario generation, while retaining the flexibility of probabilistic/ranged generation for creating diverse datasets. It standardizes how quantities are defined across different generator types and elements. This was introduced to resolve the issue where purely probabilistic generation (e.g., `note_occurrence_chance` in the initial specification) made it difficult to write reliable unit tests.
- **Impact**: Requires updates to the configuration schema definition in the package specification ([`specifications/synthetic_data_package_specification.md`](specifications/synthetic_data_package_specification.md)) and modifications to generator logic to interpret this flexible quantity type.

*(Further architectural patterns and decisions will be added here as the project evolves.)*