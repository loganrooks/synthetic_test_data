# Synthetic Test Data Generator (synth_data_gen)

## Project Overview

A Python library for generating high-quality, configurable synthetic test data in EPUB, PDF, and Markdown formats. Designed to help developers test document processing pipelines, including parsing, preprocessing, chunking, metadata extraction, and content analysis.

**Use Cases:**
- Testing document parsers and converters
- Generating sample data for ML/NLP pipelines
- Creating test fixtures for e-reader applications
- Validating PDF processing workflows
- Testing Markdown renderers and editors

## Tech Stack

- **Python**: 3.8+
- **Testing**: pytest, pytest-mock
- **EPUB Generation**: ebooklib
- **PDF Generation**: ReportLab
- **Configuration**: PyYAML, jsonschema

## Project Structure

```
synth_data_gen/
├── core/                    # Core infrastructure
│   ├── base.py             # BaseGenerator abstract class
│   └── config_loader.py    # YAML/JSON config loading and validation
├── generators/              # Format-specific generators
│   ├── epub.py             # EPUB generator
│   ├── pdf.py              # PDF generator (most complex)
│   ├── markdown.py         # Markdown generator
│   └── epub_components/    # EPUB-specific modules
│       ├── toc.py          # Table of Contents
│       ├── headers.py      # Chapter/section headers
│       ├── notes.py        # Footnotes/endnotes
│       ├── citations.py    # Bibliography
│       ├── structure.py    # EPUB file structure
│       ├── page_numbers.py # Page number markers
│       ├── content_types.py# Poetry, blockquotes
│       └── multimedia.py   # Images and fonts
├── common/                  # Shared utilities
│   └── utils.py            # Helper functions
└── __init__.py             # Main API: generate_data()

tests/                       # Test suite (mirrors src structure)
├── core/
├── generators/
│   └── epub_components/
└── test_*.py

docs/                        # Documentation
specifications/              # Package specifications
memory-bank/                 # Development tracking
```

## Commands

```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/generators/test_pdf_generator.py -v

# Run specific test
pytest tests/generators/test_pdf_generator.py::test_visual_toc_is_integrated_into_pdf_story -v

# Run with coverage
pytest --cov=synth_data_gen --cov-report=term-missing

# Run only failed tests from last run
pytest --lf
```

## Code Style

- **Type hints**: Required for all function signatures
- **Naming**: Follow PEP 8 (snake_case for functions/variables, PascalCase for classes)
- **Docstrings**: Required for all public methods and classes
- **Imports**: Group as stdlib, third-party, local; alphabetize within groups
- **Line length**: 120 characters max

## Key Patterns

### Unified Quantity Specification

The `_determine_count()` method in `BaseGenerator` handles three specification modes:

```python
# Exact: generates exactly 5 chapters
chapters_config: 5

# Ranged: generates random 3-7 chapters
chapters_config: {"min": 3, "max": 7}

# Probabilistic: 60% chance to generate, with nested options
chapters_config: {
    "chance": 0.6,
    "if_true": {"min": 1, "max": 3},
    "if_false": 0,
    "max_total": 10
}
```

### Generator Architecture

All generators inherit from `BaseGenerator` and must implement:
- `generate(specific_config, global_config, output_path) -> str`
- `get_default_specific_config() -> Dict[str, Any]`
- Optionally override `validate_config()`

### Configuration System

- **ConfigLoader**: Loads YAML/JSON configs with schema validation
- **Merging**: User config overrides default config recursively
- **Generator-specific**: Each generator type has its own config section

## Testing Conventions

- **Approach**: TDD (Test-Driven Development) with RED -> GREEN -> REFACTOR cycles
- **Structure**: Test files mirror source structure
- **Mocking**: Use pytest-mock for external dependencies (file I/O, random)
- **Naming**: `test_<feature>_<scenario>` or `test_<method>_<condition>_<expected>`

## Important Files

- `specifications/synthetic_data_package_specification.md` - Official API spec
- `docs/architecture_overview.md` - Architecture patterns
- `docs/synthetic_data_requirements.md` - Requirements for all formats
- `docs/epub_formatting_analysis_report.md` - Real EPUB analysis

## Known Issues / TODOs

- PDF Visual ToC uses placeholders for page numbers (needs two-pass implementation)
- Some probabilistic tests may have assertion count mismatches
- `pdf.py` line ~520: Handle 180-degree page rotation
- `pdf.py` line ~610: Use annotation font styling settings

## Development Workflow

This project uses an agent-based development tracking system in `memory-bank/`:
- Check `globalContext.md` for high-level progress
- Check `activeContext.md` for detailed activity logs
- Mode-specific notes in `memory-bank/mode-specific/`
