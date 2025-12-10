# Analyzer API Reference

EPUB pattern analysis and validation tools.

## EpubAnalyzer

Analyzes EPUB files to detect formatting patterns.

::: synth_data_gen.analyzer.epub_analyzer.EpubAnalyzer
    options:
      show_root_heading: true
      members:
        - analyze
        - detect_patterns

### AnalysisResult

::: synth_data_gen.analyzer.epub_analyzer.AnalysisResult
    options:
      show_root_heading: true

## PatternRegistry

Manages pattern definitions and constraints.

::: synth_data_gen.analyzer.registry.PatternRegistry
    options:
      show_root_heading: true
      members:
        - get_pattern
        - get_patterns_by_category
        - get_all_categories
        - list_patterns
        - validate_pattern_combination
        - add_pattern
        - save_pattern_to_file

### PatternDefinition

::: synth_data_gen.analyzer.registry.PatternDefinition
    options:
      show_root_heading: true

### PatternConstraint

::: synth_data_gen.analyzer.registry.PatternConstraint
    options:
      show_root_heading: true

## Validation

Round-trip validation for patterns.

::: synth_data_gen.analyzer.validation
    options:
      show_root_heading: false
      members:
        - round_trip_validate
        - validate_all_patterns
        - generate_validation_report

### ValidationResult

::: synth_data_gen.analyzer.validation.ValidationResult
    options:
      show_root_heading: true

## Usage Example

```python
from synth_data_gen.analyzer.registry import PatternRegistry
from synth_data_gen.analyzer.epub_analyzer import EpubAnalyzer
from synth_data_gen.analyzer.validation import round_trip_validate

# Load patterns
registry = PatternRegistry()

# Analyze an EPUB
analyzer = EpubAnalyzer(registry)
result = analyzer.analyze("sample.epub")

print(f"EPUB Version: {result.epub_version}")
print(f"Matched Patterns: {result.get_matched_pattern_ids()}")

# Validate a pattern
validation = round_trip_validate("ncx_flat", registry)
if validation.success:
    print("Pattern validates successfully")
else:
    print(f"Validation failed: {validation.error}")
```

## Pattern Definition Format

Patterns are defined in YAML files in the `patterns/` directory:

```yaml
patterns:
  pattern_id:
    category: toc_style
    description: "Description of the pattern"
    detection_signature:
      ncx:
        required: true
        max_depth: 2
    epub_versions: [2, 3]
    generator_config:
      toc_settings:
        style: ncx
```

### Detection Signature

The detection signature defines what to look for in an EPUB:

| Key | Type | Description |
|-----|------|-------------|
| `ncx` | object | NCX file requirements |
| `navdoc` | object | Navigation Document requirements |
| `reference` | object | Note reference patterns |
| `fonts` | object | Embedded font patterns |
