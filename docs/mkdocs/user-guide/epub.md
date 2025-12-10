# EPUB Generation

Generate EPUB 2 or EPUB 3 files with configurable structure and formatting.

## Basic Usage

```python
from synth_data_gen import generate_data

config = {
    "file_types": [
        {
            "type": "epub",
            "count": 5,
            "epub_specific_settings": {
                "epub_version": 3
            }
        }
    ]
}

files = generate_data(config_obj=config)
```

## EPUB Settings

### Version

```yaml
epub_specific_settings:
  epub_version: 3  # 2 or 3
```

### Table of Contents

```yaml
epub_specific_settings:
  toc_settings:
    style: ncx       # ncx, navdoc, html_toc
    depth: 3         # Maximum nesting depth
    include_landmarks: true  # EPUB3 landmarks
```

**ToC Styles:**

| Style | EPUB Version | Description |
|-------|--------------|-------------|
| `ncx` | 2, 3 | NCX navigation file |
| `navdoc` | 3 only | Navigation Document (EPUB3) |
| `html_toc` | 2, 3 | HTML table of contents page |

### Chapters

```yaml
epub_specific_settings:
  chapters:
    min: 5
    max: 15
  sections_per_chapter:
    min: 2
    max: 8
  paragraphs_per_section:
    min: 3
    max: 10
```

### Headers

```yaml
epub_specific_settings:
  header_style: centered  # centered, left_aligned, numbered
  include_chapter_numbers: true
```

### Notes System

```yaml
epub_specific_settings:
  notes_system:
    type: footnotes  # footnotes, endnotes, sidenotes
    style: linked    # linked, inline, popup
    placement: end_of_chapter  # end_of_chapter, end_of_book
```

### Font Embedding

```yaml
epub_specific_settings:
  fonts:
    embed: true
    obfuscation: idpf  # none, idpf, adobe
    families:
      - name: "DejaVu Sans"
        path: "/path/to/font.ttf"
```

### Images

```yaml
epub_specific_settings:
  images:
    include: true
    count:
      min: 1
      max: 5
    types: [jpg, png]
```

## Complete Example

```yaml
file_types:
  - type: epub
    count: 10
    epub_specific_settings:
      epub_version: 3

      toc_settings:
        style: navdoc
        depth: 3

      chapters:
        min: 8
        max: 20

      header_style: centered
      include_chapter_numbers: true

      notes_system:
        type: footnotes
        style: linked

      fonts:
        embed: true
        obfuscation: idpf
```

## Pattern Analyzer

Discover patterns in existing EPUBs and use them for generation:

```bash
# Analyze an EPUB
synth-analyze discover sample.epub

# List known patterns
synth-analyze list
```

See the [CLI Reference](../cli/synth-analyze.md) for details.
