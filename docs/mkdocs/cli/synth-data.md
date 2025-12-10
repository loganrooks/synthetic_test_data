# synth-data CLI

Command-line interface for generating synthetic test data.

## Usage

```bash
synth-data [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--config PATH` | Path to YAML/JSON configuration file |
| `--output DIR` | Override output directory |
| `--count N` | Override file count for all types |
| `--seed N` | Set random seed for reproducibility |
| `--help` | Show help message |

## Examples

### Generate with Defaults

```bash
synth-data
```

Generates files using default configuration to `./synthetic_output/default/`.

### Custom Configuration File

```bash
synth-data --config my_config.yaml
```

### Override Output Directory

```bash
synth-data --output ./test_fixtures
```

### Reproducible Generation

```bash
synth-data --seed 42
```

Using the same seed produces identical output.

### Quick Test Generation

```bash
synth-data --count 3
```

Generate only 3 files of each type.

## Configuration File Format

See [Configuration](../user-guide/configuration.md) for full details.

Example `config.yaml`:

```yaml
output_directory_base: ./my_output
output_set_name: batch_001

file_types:
  - type: epub
    count: 10
  - type: pdf
    count: 5
  - type: markdown
    count: 20
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Configuration error |
| 2 | Generation error |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SYNTH_DATA_CONFIG` | Default configuration file path |
| `SYNTH_DATA_OUTPUT` | Default output directory |
