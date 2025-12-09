# ADR-001: Combinatoric Test Generation Architecture

## Status
Proposed

## Context

The `synth_data_gen` library needs to generate synthetic test data that covers the enormous variety of real-world document formats. Analysis of real EPUB files (see `docs/epub_formatting_analysis_report.md`) reveals:

- **9+ ToC styles**: NCX flat, NCX nested, HTML ToC with `<p>` tags, HTML ToC with `<ul>/<ol>`, NavDoc basic, NavDoc with landmarks, NavDoc with page-list, non-hyperlinked, etc.
- **20+ header patterns**: `<h1>`-`<h6>`, styled `<p>` tags, `<div>` headers, combined number/title elements, headers with edition markers, etc.
- **16+ footnote reference styles**: Same-file links, different-file links, EPUB3 `noteref`, unlinked superscripts, symbol markers, dual systems, etc.
- **10+ note text structures**: Same-page footnotes, chapter-end notes, document endnotes, segment-end notes, granular note files, etc.
- **Multiple**: citation styles, page marker formats, image handling patterns, font embedding approaches...

The current configuration system allows specifying counts (exact, range, probabilistic), but users need:

1. **Comprehensive coverage** - "Generate EPUBs testing ALL ToC variations"
2. **Specific targeting** - "Generate an EPUB exactly like Kant's Critique formatting"
3. **Easy configuration** - Not require deep knowledge of every option
4. **Combinatoric flexibility** - "Vary ToC styles, keep everything else default"

## Decision

Implement a **three-tier configuration system**:

### Tier 1: Presets (Named Profiles)

Pre-defined configurations that capture real-world formatting patterns:

```yaml
# Using a preset
preset: "kant_critique_style"

# Or combine presets with overrides
preset: "epub3_semantic"
overrides:
  notes_system:
    type: "chapter_end_notes"
```

**Preset examples:**
- `epub2_calibre_basic` - Simple Calibre-converted EPUB2
- `epub3_semantic` - Modern EPUB3 with semantic markup
- `kant_critique_style` - Scholarly with dual footnote systems, edition markers
- `ocr_scanned_book` - PDF-like with page images, OCR artifacts

### Tier 2: Feature Matrix (Combinatoric Generation)

Generate all combinations of specified features:

```yaml
matrix:
  toc_style: ["ncx_flat", "ncx_nested", "navdoc_basic", "html_toc_p_tags"]
  notes_system: ["footnotes_same_page", "endnotes_collected"]
  # Other features use defaults

# Generates: 4 × 2 = 8 EPUB files covering all combinations
```

**With constraints:**
```yaml
matrix:
  toc_style: ["ncx_flat", "ncx_nested", "navdoc_*"]  # Wildcards
  notes_system: ["footnotes_*"]
exclude:
  - toc_style: "navdoc_*"
    notes_system: "footnotes_granular"  # Invalid combination
```

### Tier 3: Direct Configuration (Full Control)

The existing detailed configuration for precise control:

```yaml
epub:
  toc_settings:
    style: "ncx_deeply_nested"
    max_depth: 4
    include_page_list: true
  notes_system:
    type: "dual_footnotes_endnotes"
    footnote_marker_style: "symbol"
    endnote_marker_style: "numeric"
```

### Priority Resolution

```
Tier 3 (Direct) > Tier 2 (Matrix) > Tier 1 (Preset) > Defaults
```

## Implementation

### 1. Preset Registry

```python
# synth_data_gen/presets/__init__.py
PRESETS = {
    "epub2_calibre_basic": {
        "epub_version": 2,
        "toc_settings": {"style": "ncx_flat"},
        "notes_system": {"type": "footnotes_same_page"},
        ...
    },
    "epub3_semantic": {
        "epub_version": 3,
        "toc_settings": {"style": "navdoc_full", "include_landmarks": True},
        "notes_system": {"type": "epub3_aside_notes"},
        ...
    },
    # Derived from real EPUB analysis
    "kant_critique_style": {...},
    "taylor_hegel_style": {...},
    ...
}
```

### 2. Matrix Expander

```python
# synth_data_gen/core/matrix.py
def expand_matrix(matrix_config: dict) -> List[dict]:
    """
    Expands a feature matrix into individual configurations.

    Input:
        matrix:
          toc_style: ["ncx_flat", "ncx_nested"]
          notes_system: ["footnotes", "endnotes"]

    Output:
        [
            {"toc_style": "ncx_flat", "notes_system": "footnotes"},
            {"toc_style": "ncx_flat", "notes_system": "endnotes"},
            {"toc_style": "ncx_nested", "notes_system": "footnotes"},
            {"toc_style": "ncx_nested", "notes_system": "endnotes"},
        ]
    """
```

### 3. Feature Catalog

Document all available features and their valid values:

```yaml
# synth_data_gen/catalog/epub_features.yaml
toc_style:
  description: "Table of Contents format"
  values:
    ncx_flat:
      description: "Simple flat NCX (EPUB2)"
      epub_version: [2, 3]
    ncx_nested:
      description: "Deeply nested NCX with 3+ levels"
      epub_version: [2, 3]
    navdoc_basic:
      description: "EPUB3 Navigation Document (basic)"
      epub_version: [3]
      requires: ["epub3"]
    # ... all 9+ styles

notes_system:
  description: "Footnote/endnote handling"
  values:
    footnotes_same_page:
      description: "Notes at bottom of same HTML file"
    endnotes_collected:
      description: "Notes in separate notes.xhtml file"
    # ... all 16+ patterns
```

### 4. Test Suite Generation

```python
# CLI or API for generating comprehensive test suites
from synth_data_gen import generate_test_suite

# Generate all ToC variations with default everything else
generate_test_suite(
    vary=["toc_style"],
    output_dir="test_data/toc_variations/"
)

# Generate comprehensive EPUB coverage
generate_test_suite(
    vary=["toc_style", "notes_system", "header_style"],
    sample_size=50,  # Random sample if full matrix too large
    output_dir="test_data/epub_comprehensive/"
)
```

## API Examples

### Simple: Use a Preset
```python
from synth_data_gen import generate_data

# Generate files like Kant's Critique formatting
generate_data(config_obj={
    "preset": "kant_critique_style",
    "file_types": [{"type": "epub", "count": 5}]
})
```

### Targeted: Specific Edge Case
```python
# Generate EPUB with unlinked footnotes (like Adorno)
generate_data(config_obj={
    "preset": "epub2_calibre_basic",
    "overrides": {
        "notes_system": {
            "type": "unlinked_superscript",
            "notes_config": 10
        }
    }
})
```

### Comprehensive: Feature Matrix
```python
# Generate all ToC × Notes combinations
generate_data(config_obj={
    "matrix": {
        "toc_style": ["ncx_*", "navdoc_*", "html_toc_*"],
        "notes_system": ["footnotes_*", "endnotes_*"]
    },
    "base_config": {
        "chapters_config": 3  # Keep documents small
    }
})
```

### Coverage Report
```python
from synth_data_gen import get_coverage_report

# See what features exist and what's been tested
report = get_coverage_report("test_data/generated/")
print(report)
# Output:
# toc_style: 7/9 covered (missing: html_toc_non_hyperlinked, ncx_with_pagelist)
# notes_system: 4/16 covered
# ...
```

## Consequences

### Positive
- **Easy onboarding**: New users can start with presets
- **Comprehensive testing**: Matrix generation ensures coverage
- **Specificity**: Direct config still available for precise control
- **Documentation**: Feature catalog serves as both config reference and coverage tracker
- **Real-world alignment**: Presets derived from actual EPUB analysis

### Negative
- **Complexity**: Three-tier system is more complex to implement
- **Preset maintenance**: Need to keep presets updated as formats evolve
- **Matrix explosion**: Large matrices can generate many files

### Mitigations
- Implement sampling for large matrices
- Auto-generate preset documentation from catalog
- Provide `--dry-run` to preview matrix expansion

## Related

- `docs/epub_formatting_analysis_report.md` - Source of formatting patterns
- `docs/synthetic_data_requirements.md` - Full requirements
- `specifications/synthetic_data_package_specification.md` - Current API spec
