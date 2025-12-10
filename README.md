# Synthetic Test Data Generator

[![CI](https://github.com/synth-data-gen/synth_data_gen/actions/workflows/ci.yml/badge.svg)](https://github.com/synth-data-gen/synth_data_gen/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for generating high-quality, configurable synthetic test data in **EPUB**, **PDF**, and **Markdown** formats. Designed to help developers test document processing pipelines, including parsing, preprocessing, chunking, metadata extraction, and content analysis.

## Features

- **Multi-format support**: Generate EPUB 2/3, PDF, and Markdown documents
- **Highly configurable**: Control every aspect of document generation
- **Realistic content**: Produces valid, well-formed documents
- **Pattern-based generation**: Supports various formatting patterns found in real documents
- **EPUB Pattern Analyzer**: Detect and validate formatting patterns in existing EPUBs

## Use Cases

- Testing document parsers and converters
- Generating sample data for ML/NLP pipelines
- Creating test fixtures for e-reader applications
- Validating PDF processing workflows
- Testing Markdown renderers and editors
- Benchmark testing with controlled document complexity

## Installation

### From PyPI (when published)

```bash
pip install synth-data-gen
```

### From source (development)

```bash
# Clone the repository
git clone https://github.com/synth-data-gen/synth_data_gen.git
cd synth_data_gen

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from synth_data_gen import generate_data

# Generate a simple EPUB
config = {
    "output_directory_base": "./output",
    "output_set_name": "my_test_data",
    "file_types": [
        {
            "type": "epub",
            "count": 1,
            "epub_specific_settings": {
                "title": "Test Book",
                "author": "Test Author",
                "chapters_config": 5,
            }
        }
    ]
}

generated_files = generate_data(config_obj=config)
print(f"Generated: {generated_files}")
```

### Generate Multiple Formats

```python
from synth_data_gen import generate_data

config = {
    "output_directory_base": "./test_data",
    "output_set_name": "multi_format_test",
    "file_types": [
        {
            "type": "epub",
            "count": 3,
            "epub_specific_settings": {
                "title": "EPUB Test",
                "chapters_config": {"min": 3, "max": 7},
                "epub_version": 3,
            }
        },
        {
            "type": "pdf",
            "count": 2,
            "pdf_specific_settings": {
                "title": "PDF Test",
                "page_count_config": {"min": 10, "max": 20},
            }
        },
        {
            "type": "markdown",
            "count": 5,
            "markdown_specific_settings": {
                "title": "Markdown Test",
                "sections_config": 4,
            }
        }
    ]
}

files = generate_data(config_obj=config)
```

### Using YAML Configuration

```python
from synth_data_gen import generate_data

# Load from YAML file
files = generate_data(config_path="my_config.yaml")
```

Example `my_config.yaml`:

```yaml
output_directory_base: ./output
output_set_name: yaml_test

file_types:
  - type: epub
    count: 1
    epub_specific_settings:
      title: "My Test Book"
      author: "Test Author"
      language: "en"
      epub_version: 3
      chapters_config:
        min: 5
        max: 10
      toc_settings:
        style: navdoc
        max_depth: 3
      notes_system:
        enable: true
        type: footnotes_same_page
```

### Advanced: Probabilistic Configuration

Control generation with probability distributions:

```python
config = {
    "output_directory_base": "./output",
    "output_set_name": "probabilistic_test",
    "file_types": [
        {
            "type": "epub",
            "count": 10,
            "epub_specific_settings": {
                "title": "Probabilistic Test",
                # 60% chance of footnotes
                "notes_system": {
                    "enable": {
                        "chance": 0.6,
                        "if_true": {"type": "footnotes_same_page"},
                        "if_false": {"enable": False}
                    }
                },
                # Random chapter count between 3-8
                "chapters_config": {"min": 3, "max": 8},
            }
        }
    ]
}
```

## EPUB Features

### Table of Contents

- NCX (EPUB 2)
- Navigation Document (EPUB 3)
- HTML ToC with various styles
- Nested structures with configurable depth

### Notes System

- Footnotes (same page)
- Footnotes (end of chapter)
- Endnotes (end of book)
- EPUB 3 semantic noteref

### Content Types

- Standard prose
- Poetry/verse
- Blockquotes
- Code blocks
- Lists

### Multimedia

- Image embedding
- Font embedding with obfuscation
- CSS styling

## PDF Features

- Configurable page layouts
- Visual Table of Contents with page numbers
- Headers and footers
- Page rotation support
- Annotations
- Multiple column layouts

## EPUB Pattern Analyzer

Analyze existing EPUB files to detect formatting patterns:

```python
from synth_data_gen.analyzer import EpubAnalyzer, PatternRegistry

# Create analyzer with pattern registry
registry = PatternRegistry()
analyzer = EpubAnalyzer(registry)

# Analyze an EPUB
result = analyzer.analyze("path/to/book.epub")

# Get detected patterns
print(f"EPUB Version: {result.epub_version}")
print(f"Matched patterns: {result.get_matched_pattern_ids()}")

# Get coverage report
coverage = result.get_coverage_report()
for category, patterns in coverage.items():
    print(f"{category}: {patterns}")
```

## Configuration Reference

### Quantity Specification

The library supports three ways to specify quantities:

```yaml
# Exact: generates exactly 5 chapters
chapters_config: 5

# Ranged: generates random 3-7 chapters
chapters_config:
  min: 3
  max: 7

# Probabilistic: 60% chance to generate
chapters_config:
  chance: 0.6
  if_true:
    min: 1
    max: 3
  if_false: 0
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=synth_data_gen --cov-report=term-missing

# Run specific test file
pytest tests/generators/test_epub_generator.py -v
```

### Project Structure

```
synth_data_gen/
├── core/                    # Core infrastructure
│   ├── base.py             # BaseGenerator abstract class
│   ├── config_loader.py    # Configuration loading
│   └── default_config.yaml # Default values
├── generators/              # Format-specific generators
│   ├── epub.py             # EPUB generator
│   ├── pdf.py              # PDF generator
│   ├── markdown.py         # Markdown generator
│   └── epub_components/    # EPUB-specific modules
├── analyzer/               # EPUB Pattern Analyzer
│   ├── epub_analyzer.py    # Pattern detection
│   ├── registry.py         # Pattern registry
│   └── patterns/           # Pattern definitions
└── common/                 # Shared utilities
```

## Contributing

Contributions are welcome! Please see our [ROADMAP.md](ROADMAP.md) for planned features and priorities.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [ebooklib](https://github.com/aerkalov/ebooklib) for EPUB generation
- [ReportLab](https://www.reportlab.com/) for PDF generation
