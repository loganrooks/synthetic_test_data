# Markdown Generation

Generate Markdown files following GitHub Flavored Markdown (GFM) specification.

## Basic Usage

```python
from synth_data_gen import generate_data

config = {
    "file_types": [
        {
            "type": "markdown",
            "count": 10,
            "markdown_specific_settings": {
                "flavor": "gfm"
            }
        }
    ]
}

files = generate_data(config_obj=config)
```

## Markdown Settings

### Flavor

```yaml
markdown_specific_settings:
  flavor: gfm  # gfm (GitHub Flavored Markdown)
```

### Document Structure

```yaml
markdown_specific_settings:
  sections:
    min: 3
    max: 8
  subsections_per_section:
    min: 1
    max: 4
  paragraphs_per_subsection:
    min: 2
    max: 6
```

### Headings

```yaml
markdown_specific_settings:
  heading_style: atx    # atx (#) or setext (underlined)
  max_heading_level: 4
  include_toc: true     # Generate table of contents
```

### Code Blocks

```yaml
markdown_specific_settings:
  code_blocks:
    enabled: true
    count:
      min: 1
      max: 5
    languages: [python, javascript, bash, json]
    style: fenced  # fenced (```) or indented
```

### Lists

```yaml
markdown_specific_settings:
  lists:
    enabled: true
    types: [unordered, ordered, task]
    count:
      min: 2
      max: 6
    items_per_list:
      min: 3
      max: 8
```

### Tables

```yaml
markdown_specific_settings:
  tables:
    enabled: true
    count:
      min: 1
      max: 3
    rows:
      min: 3
      max: 10
    columns:
      min: 2
      max: 5
```

### Blockquotes

```yaml
markdown_specific_settings:
  blockquotes:
    enabled: true
    count:
      min: 1
      max: 4
```

### Links and Images

```yaml
markdown_specific_settings:
  links:
    enabled: true
    types: [inline, reference]
    count:
      min: 2
      max: 8

  images:
    enabled: true
    count:
      min: 0
      max: 3
```

## Complete Example

```yaml
file_types:
  - type: markdown
    count: 20
    markdown_specific_settings:
      flavor: gfm

      sections:
        min: 4
        max: 10

      heading_style: atx
      max_heading_level: 4
      include_toc: true

      code_blocks:
        enabled: true
        count:
          min: 2
          max: 6
        languages: [python, javascript, bash]

      tables:
        enabled: true
        count:
          min: 1
          max: 2

      lists:
        enabled: true
        types: [unordered, ordered, task]

      blockquotes:
        enabled: true
        count:
          min: 1
          max: 3
```

## Generated Output Example

A generated Markdown file might look like:

```markdown
# Document Title

## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)

## Section 1

Lorem ipsum dolor sit amet...

### Subsection 1.1

Content with a code block:

\`\`\`python
def example():
    return "Hello, World!"
\`\`\`

## Section 2

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

> This is a blockquote with important information.
```
