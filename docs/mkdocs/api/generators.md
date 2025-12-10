# Generators API Reference

Format-specific generator classes.

## EpubGenerator

Generates EPUB 2 and EPUB 3 files.

::: synth_data_gen.generators.epub.EpubGenerator
    options:
      show_root_heading: true
      members:
        - generate
        - get_default_specific_config

### EPUB Components

The EPUB generator uses several component modules:

#### ToC Module

Handles table of contents generation.

::: synth_data_gen.generators.epub_components.toc
    options:
      show_root_heading: false
      members:
        - create_ncx
        - create_nav_doc

#### Headers Module

Chapter and section header generation.

::: synth_data_gen.generators.epub_components.headers
    options:
      show_root_heading: false

#### Notes Module

Footnotes and endnotes handling.

::: synth_data_gen.generators.epub_components.notes
    options:
      show_root_heading: false

## PdfGenerator

Generates PDF files with ReportLab.

::: synth_data_gen.generators.pdf.PdfGenerator
    options:
      show_root_heading: true
      members:
        - generate
        - get_default_specific_config

### PDF Features

- **Visual ToC**: Table of contents with page numbers and dot leaders
- **Two-pass generation**: Accurate page numbers via pre-render pass
- **Page rotation**: 90 or 180 degree rotation support
- **Annotations**: Highlights, comments, and links

## MarkdownGenerator

Generates GitHub Flavored Markdown files.

::: synth_data_gen.generators.markdown.MarkdownGenerator
    options:
      show_root_heading: true
      members:
        - generate
        - get_default_specific_config

### Supported Elements

- ATX and Setext headings
- Fenced and indented code blocks
- Tables (GFM)
- Task lists
- Blockquotes
- Links and images

## Creating Custom Generators

Extend `BaseGenerator` to create custom format generators:

```python
from synth_data_gen.core.base import BaseGenerator
from typing import Dict, Any

class CustomGenerator(BaseGenerator):
    def generate(
        self,
        specific_config: Dict[str, Any],
        global_config: Dict[str, Any],
        output_path: str
    ) -> str:
        # Implementation
        return output_path

    def get_default_specific_config(self) -> Dict[str, Any]:
        return {
            "custom_option": "default_value"
        }
```
