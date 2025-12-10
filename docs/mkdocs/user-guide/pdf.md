# PDF Generation

Generate PDF files with visual tables of contents, configurable layouts, and various formatting options.

## Basic Usage

```python
from synth_data_gen import generate_data

config = {
    "file_types": [
        {
            "type": "pdf",
            "count": 3,
            "pdf_specific_settings": {
                "variant": "visual_toc"
            }
        }
    ]
}

files = generate_data(config_obj=config)
```

## PDF Settings

### Variant

```yaml
pdf_specific_settings:
  variant: visual_toc  # visual_toc, simple, academic
```

**Variants:**

| Variant | Description |
|---------|-------------|
| `visual_toc` | Includes visual table of contents with page numbers |
| `simple` | Basic PDF without ToC |
| `academic` | Academic paper format with abstract, sections |

### Page Settings

```yaml
pdf_specific_settings:
  page_settings:
    size: letter     # letter, a4, legal
    orientation: portrait  # portrait, landscape
    margins:
      top: 72        # Points (72 points = 1 inch)
      bottom: 72
      left: 72
      right: 72
```

### Headers and Footers

```yaml
pdf_specific_settings:
  headers:
    enabled: true
    content: "Document Title"
    font_size: 10
    alignment: center  # left, center, right

  footers:
    enabled: true
    include_page_numbers: true
    format: "Page {page} of {total}"
```

### Visual Table of Contents

```yaml
pdf_specific_settings:
  variant: visual_toc
  toc_settings:
    title: "Contents"
    include_page_numbers: true
    dot_leader: true          # Dotted line to page number
    indent_per_level: 20      # Points per nesting level
    max_depth: 3
```

### Content Structure

```yaml
pdf_specific_settings:
  chapters:
    min: 5
    max: 12
  sections_per_chapter:
    min: 2
    max: 6
  paragraphs_per_section:
    min: 3
    max: 8
```

### Page Rotation

```yaml
pdf_specific_settings:
  rotation:
    enabled: true
    angle: 90  # 90 or 180 degrees
    pages: [1, 5, 10]  # Specific pages, or "all"
```

### Annotations

```yaml
pdf_specific_settings:
  annotations:
    enabled: true
    types: [highlight, comment, link]
    count:
      min: 2
      max: 10
```

## Complete Example

```yaml
file_types:
  - type: pdf
    count: 5
    pdf_specific_settings:
      variant: visual_toc

      page_settings:
        size: letter
        orientation: portrait
        margins:
          top: 72
          bottom: 72
          left: 72
          right: 72

      headers:
        enabled: true
        content: "Generated Document"

      footers:
        enabled: true
        include_page_numbers: true

      toc_settings:
        title: "Table of Contents"
        dot_leader: true
        max_depth: 2

      chapters:
        min: 8
        max: 15

      annotations:
        enabled: true
        count:
          min: 5
          max: 15
```

## Implementation Notes

The PDF generator uses ReportLab and implements a two-pass generation approach for accurate page numbers in the visual ToC:

1. **First Pass**: Generate content and collect page number information
2. **Second Pass**: Generate final PDF with correct ToC page numbers

This ensures the table of contents always shows accurate page references.
