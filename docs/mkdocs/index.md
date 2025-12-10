# Synthetic Data Generator

A Python library for generating high-quality, configurable synthetic test data in **EPUB**, **PDF**, and **Markdown** formats.

## Why synth_data_gen?

Testing document processing pipelines requires realistic test data that covers edge cases and format variations. Creating this data manually is time-consuming and error-prone. `synth_data_gen` automates this process with:

- **Format Variety**: Generate EPUB 2/3, PDF with visual ToC, and GFM Markdown
- **Configurable Output**: Control structure, styling, and content through YAML/JSON configs
- **Realistic Patterns**: Based on analysis of real-world documents
- **Reproducible Results**: Seed-based random generation for consistent test fixtures

## Use Cases

- Testing document parsers and converters
- Generating sample data for ML/NLP pipelines
- Creating test fixtures for e-reader applications
- Validating PDF processing workflows
- Testing Markdown renderers and editors

## Quick Example

```python
from synth_data_gen import generate_data

# Generate with default settings
files = generate_data()

# Generate with custom config
config = {
    "output_directory_base": "./test_output",
    "file_types": [
        {"type": "epub", "count": 5},
        {"type": "pdf", "count": 3},
        {"type": "markdown", "count": 10}
    ]
}
files = generate_data(config_obj=config)
```

## Installation

```bash
pip install synth_data_gen
```

For development:

```bash
pip install synth_data_gen[dev]
```

## Features

### EPUB Generation
- EPUB 2 and EPUB 3 formats
- Multiple ToC styles (NCX, Navigation Document, HTML ToC)
- Footnotes and endnotes systems
- Font embedding with obfuscation
- Chapter/section header variations

### PDF Generation
- Visual Table of Contents with dot leaders
- Configurable page layouts and margins
- Headers, footers, and page numbers
- Page rotation support
- Annotations and bookmarks

### Markdown Generation
- GitHub Flavored Markdown (GFM)
- Various heading structures
- Code blocks with syntax highlighting
- Tables, lists, and blockquotes

### EPUB Pattern Analyzer
- Discover formatting patterns in existing EPUBs
- Build pattern definitions for generation
- Round-trip validation testing

## License

MIT License - see [LICENSE](https://github.com/synth-data-gen/synth_data_gen/blob/main/LICENSE) for details.
