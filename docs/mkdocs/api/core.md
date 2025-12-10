# Core API Reference

Core modules for configuration and base generator functionality.

## generate_data

The main entry point for generating synthetic data.

::: synth_data_gen.generate_data
    options:
      show_root_heading: true

## ConfigLoader

Configuration loading and validation.

::: synth_data_gen.core.config_loader.ConfigLoader
    options:
      show_root_heading: true
      members:
        - load_and_validate_config
        - get_default_config

## BaseGenerator

Abstract base class for all generators.

::: synth_data_gen.core.base.BaseGenerator
    options:
      show_root_heading: true
      members:
        - generate
        - get_default_specific_config
        - validate_config
        - _determine_count

## Constants

Enums and constants used throughout the library.

### GeneratorType

```python
from synth_data_gen.constants import GeneratorType

GeneratorType.EPUB      # EPUB generator
GeneratorType.PDF       # PDF generator
GeneratorType.MARKDOWN  # Markdown generator
```

### PdfVariant

```python
from synth_data_gen.constants import PdfVariant

PdfVariant.VISUAL_TOC  # PDF with visual table of contents
PdfVariant.SIMPLE      # Simple PDF without ToC
PdfVariant.ACADEMIC    # Academic paper format
```

### EpubVersion

```python
from synth_data_gen.constants import EpubVersion

EpubVersion.EPUB2  # EPUB version 2
EpubVersion.EPUB3  # EPUB version 3
```

## Exceptions

### ConfigurationError

Raised when configuration is invalid.

```python
from synth_data_gen.core.config_loader import ConfigurationError

try:
    generate_data(config_obj=invalid_config)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```
