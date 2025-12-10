# Quick Start

This guide walks you through generating your first synthetic test files.

## Basic Usage

### Python API

```python
from synth_data_gen import generate_data

# Generate files with default settings
files = generate_data()
print(f"Generated {len(files)} files")
```

### Command Line

```bash
# Generate with defaults
synth-data

# Generate with a config file
synth-data --config my_config.yaml
```

## Customizing Output

### Inline Configuration

```python
from synth_data_gen import generate_data

config = {
    "output_directory_base": "./my_test_data",
    "output_set_name": "test_batch_1",
    "file_types": [
        {
            "type": "epub",
            "count": 3,
            "epub_specific_settings": {
                "epub_version": 3,
                "toc_settings": {"style": "navdoc"}
            }
        },
        {
            "type": "pdf",
            "count": 2,
            "pdf_specific_settings": {
                "variant": "visual_toc",
                "page_settings": {"size": "letter"}
            }
        }
    ]
}

files = generate_data(config_obj=config)
```

### YAML Configuration File

Create `config.yaml`:

```yaml
output_directory_base: ./synthetic_output
output_set_name: my_test_set

file_types:
  - type: epub
    count: 5
    epub_specific_settings:
      epub_version: 3
      chapters:
        min: 3
        max: 10

  - type: pdf
    count: 3
    pdf_specific_settings:
      variant: visual_toc

  - type: markdown
    count: 10
```

Then run:

```python
from synth_data_gen import generate_data

files = generate_data(config_path="config.yaml")
```

## Output Structure

Generated files are organized as:

```
output_directory_base/
└── output_set_name/
    ├── epub/
    │   ├── synthetic_0001.epub
    │   ├── synthetic_0002.epub
    │   └── ...
    ├── pdf/
    │   ├── synthetic_0001.pdf
    │   └── ...
    └── markdown/
        ├── synthetic_0001.md
        └── ...
```

## Next Steps

- Learn about [Configuration](../user-guide/configuration.md) options
- Explore [EPUB Generation](../user-guide/epub.md) features
- Check the [API Reference](../api/core.md)
