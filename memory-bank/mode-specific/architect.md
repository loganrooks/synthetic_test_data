# Architect Specific Memory
<!-- Entries below should be added reverse chronologically (newest first) -->
## Data Models

### Data Model: UnifiedQuantitySpecification - 2025-05-11 02:35:00
- **Purpose**: To provide a flexible and unified way to specify the quantity of sub-elements (e.g., chapters, footnotes, images, list items) within generated synthetic data. This model supports deterministic counts for testing and probabilistic/ranged counts for varied data generation.
- **Structure**:
  ```json
  {
    "description": "A configuration value that can be an exact integer, a min/max range object, or a probabilistic generation object.",
    "oneOf": [
      {
        "type": "integer",
        "description": "An exact, deterministic count."
      },
      {
        "type": "object",
        "description": "A range for a random count (inclusive).",
        "properties": {
          "min": { "type": "integer", "description": "Minimum count." },
          "max": { "type": "integer", "description": "Maximum count." }
        },
        "required": ["min", "max"]
      },
      {
        "type": "object",
        "description": "Probabilistic generation parameters.",
        "properties": {
          "chance": { "type": "number", "format": "float", "minimum": 0.0, "maximum": 1.0, "description": "Probability of occurrence (0.0 to 1.0)." },
          "per_unit_of": { "type": "string", "description": "Context unit for the chance (e.g., 'paragraph', 'chapter', 'document'). Optional." },
          "max_total": { "type": "integer", "description": "Overall cap on the number of elements generated this way. Optional." }
        },
        "required": ["chance"]
      }
    ]
  }
  ```
- **Relationships**: This data model will be used for various configuration keys within the `synth_data_gen` package specification, such as those defining the number of chapters, sections, notes, images, list items, table rows/columns, etc. It directly influences the `ConfigLoader` and the `generate` methods of `BaseGenerator` and its subclasses.
- **Examples in Configuration**:
  - `number_of_chapters: 5` (Exact)
  - `footnotes_per_chapter: { "min": 0, "max": 3 }` (Range)
  - `images_in_document: { "chance": 0.25, "per_unit_of": "chapter", "max_total": 10 }` (Probabilistic)