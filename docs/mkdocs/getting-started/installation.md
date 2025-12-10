# Installation

## Requirements

- Python 3.8 or higher
- pip package manager

## Standard Installation

Install from PyPI:

```bash
pip install synth_data_gen
```

## Development Installation

For contributing or development work:

```bash
# Clone the repository
git clone https://github.com/synth-data-gen/synth_data_gen.git
cd synth_data_gen

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Optional Dependencies

### Documentation

To build the documentation locally:

```bash
pip install synth_data_gen[docs]
mkdocs serve
```

### All Development Tools

```bash
pip install synth_data_gen[dev,docs]
```

## Verifying Installation

After installation, verify everything works:

```python
from synth_data_gen import generate_data

# Should print the list of generated files
print(generate_data())
```

Or use the CLI:

```bash
# Show help
synth-data --help

# Generate with defaults
synth-data
```

## Dependencies

The library automatically installs these dependencies:

| Package | Purpose |
|---------|---------|
| ebooklib | EPUB file generation |
| reportlab | PDF file generation |
| PyYAML | Configuration file parsing |
| jsonschema | Configuration validation |
