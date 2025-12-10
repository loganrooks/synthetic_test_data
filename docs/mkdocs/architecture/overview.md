# Architecture Overview

This document describes the high-level architecture of the Synthetic Data Generator.

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Python API  │  │ synth-data  │  │  synth-analyze CLI  │  │
│  │ generate()  │  │    CLI      │  │                     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                        Core Layer                            │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │  ConfigLoader   │  │         BaseGenerator           │   │
│  │  - YAML/JSON    │  │  - Abstract interface           │   │
│  │  - Validation   │  │  - Quantity specification       │   │
│  │  - Merging      │  │  - Config validation            │   │
│  └────────┬────────┘  └────────────────┬────────────────┘   │
└───────────┼────────────────────────────┼────────────────────┘
            │                            │
            ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Generator Layer                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────────┐  │
│  │ EpubGenerator │ │ PdfGenerator  │ │ MarkdownGenerator │  │
│  │  - ebooklib   │ │  - reportlab  │ │  - GFM output     │  │
│  │  - Components │ │  - Two-pass   │ │                   │  │
│  └───────────────┘ └───────────────┘ └───────────────────┘  │
│         │                                                    │
│         ▼                                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              EPUB Components                           │  │
│  │  toc │ headers │ notes │ citations │ multimedia       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Analyzer Module                          │
│  ┌─────────────────┐  ┌─────────────┐  ┌────────────────┐   │
│  │ PatternRegistry │  │ EpubAnalyzer│  │   Validation   │   │
│  │  - YAML patterns│  │  - Detection│  │  - Round-trip  │   │
│  │  - Constraints  │  │  - Matching │  │  - Reporting   │   │
│  └─────────────────┘  └─────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Patterns

### Unified Quantity Specification

All count/quantity fields use a common specification system:

```python
# Exact
count: 5

# Range
count: {min: 3, max: 7}

# Probabilistic
count:
  chance: 0.6
  if_true: {min: 1, max: 3}
  if_false: 0
```

Implemented in `BaseGenerator._determine_count()`.

### Configuration Deep Merge

User configuration is deep-merged with defaults:

```python
default = {"a": {"b": 1, "c": 2}}
user = {"a": {"b": 10}}
# Result: {"a": {"b": 10, "c": 2}}
```

### Generator Interface

All generators implement:

```python
class Generator(BaseGenerator):
    def generate(self, specific_config, global_config, output_path) -> str:
        """Generate a file, return its path."""
        pass

    def get_default_specific_config(self) -> Dict[str, Any]:
        """Return default settings for this generator."""
        pass
```

### Pattern Registry

Patterns are loaded from YAML files and matched against EPUB structures:

```
Pattern Definition ─────► Detection Signature
         │                       │
         ▼                       ▼
Generator Config ◄────── Pattern Matching
```

## Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `synth_data_gen/__init__.py` | Main API entry point |
| `core/config_loader.py` | Configuration loading/validation |
| `core/base.py` | Abstract generator base class |
| `generators/epub.py` | EPUB file generation |
| `generators/pdf.py` | PDF file generation |
| `generators/markdown.py` | Markdown file generation |
| `analyzer/registry.py` | Pattern management |
| `analyzer/epub_analyzer.py` | EPUB pattern detection |
| `analyzer/validation.py` | Round-trip validation |

## Data Flow

1. **Configuration**: Load YAML → Validate → Merge with defaults
2. **Generation**: For each file type, create generator → Generate file
3. **Analysis**: Load EPUB → Detect patterns → Match against registry
4. **Validation**: Get generator config → Generate EPUB → Detect patterns → Verify match
