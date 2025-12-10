# Configuration

The configuration system supports YAML and JSON formats with schema validation and deep merging.

## Configuration Structure

```yaml
# Global settings
output_directory_base: ./output
output_set_name: synthetic_data
random_seed: 42  # Optional: for reproducible output

# File type definitions
file_types:
  - type: epub
    count: 5
    epub_specific_settings:
      # EPUB-specific options

  - type: pdf
    count: 3
    pdf_specific_settings:
      # PDF-specific options

  - type: markdown
    count: 10
    markdown_specific_settings:
      # Markdown-specific options
```

## Quantity Specification

All count/quantity fields support three specification modes:

### Exact Count

```yaml
chapters: 5  # Always generates exactly 5 chapters
```

### Range

```yaml
chapters:
  min: 3
  max: 7  # Generates between 3 and 7 chapters
```

### Probabilistic

```yaml
chapters:
  chance: 0.6        # 60% chance to generate
  if_true:
    min: 1
    max: 3           # If triggered, generate 1-3
  if_false: 0        # Otherwise, generate none
  max_total: 10      # Optional cap
```

## Configuration Loading

### From File

```python
from synth_data_gen import generate_data

files = generate_data(config_path="config.yaml")
```

### From Object

```python
config = {
    "output_directory_base": "./output",
    "file_types": [{"type": "epub", "count": 5}]
}
files = generate_data(config_obj=config)
```

### Merging Configs

User config is deep-merged with defaults. Specify only what you want to change:

```python
# Only override specific settings - everything else uses defaults
config = {
    "file_types": [
        {
            "type": "epub",
            "count": 10,
            "epub_specific_settings": {
                "epub_version": 3
                # All other EPUB settings use defaults
            }
        }
    ]
}
```

## Common Settings

### Output Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `output_directory_base` | string | `./synthetic_output` | Base output directory |
| `output_set_name` | string | `default` | Subdirectory name |
| `random_seed` | int | None | Seed for reproducibility |

### File Type Settings

| Setting | Type | Required | Description |
|---------|------|----------|-------------|
| `type` | string | Yes | `epub`, `pdf`, or `markdown` |
| `count` | int/range | Yes | Number of files to generate |
| `*_specific_settings` | object | No | Format-specific options |

## Environment Variables

Configuration can also reference environment variables:

```yaml
output_directory_base: ${OUTPUT_DIR:-./default_output}
```

## Validation

Invalid configurations raise `ConfigurationError` with details:

```python
from synth_data_gen import generate_data
from synth_data_gen.core.config_loader import ConfigurationError

try:
    generate_data(config_obj={"invalid": "config"})
except ConfigurationError as e:
    print(f"Config error: {e}")
```
