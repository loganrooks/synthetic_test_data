# synth-analyze CLI

Command-line interface for analyzing EPUB files and managing pattern definitions.

## Commands

### discover

Analyze EPUB files to discover formatting patterns.

```bash
synth-analyze discover <EPUB_PATH> [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `EPUB_PATH` | Path to EPUB file or directory |

**Options:**

| Option | Description |
|--------|-------------|
| `--output PATH` | Output file for candidates (default: candidates.yaml) |

**Example:**

```bash
# Analyze a single EPUB
synth-analyze discover book.epub

# Analyze all EPUBs in a directory
synth-analyze discover ./epub_collection/
```

**Output:**

```
Analyzing: book.epub
  EPUB Version: 3
  Detected Patterns:
    - ncx_flat (toc_style)
    - footnotes_linked (notes_system)
  Unknown Features:
    - Custom navigation structure

Candidates written to: candidates.yaml
```

### list

List registered patterns.

```bash
synth-analyze list [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--category NAME` | Filter by category |

**Example:**

```bash
# List all patterns
synth-analyze list

# List only ToC patterns
synth-analyze list --category toc_style
```

### add-patterns

Add new patterns from discovery candidates.

```bash
synth-analyze add-patterns <CANDIDATES_FILE> [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `CANDIDATES_FILE` | Path to candidates YAML file |

**Options:**

| Option | Description |
|--------|-------------|
| `--validate` | Run validation after adding |

**Example:**

```bash
synth-analyze add-patterns candidates.yaml --validate
```

### validate

Validate patterns through round-trip testing.

```bash
synth-analyze validate [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--category NAME` | Validate only specified category |
| `--pattern ID` | Validate specific pattern |

**Example:**

```bash
# Validate all patterns
synth-analyze validate

# Validate specific category
synth-analyze validate --category toc_style
```

**Output:**

```
============================================================
EPUB Pattern Round-Trip Validation Report
============================================================

Total patterns: 15
Passed: 14
Failed: 1

----------------------------------------
PASSED:
  ✓ ncx_flat
  ✓ ncx_hierarchical
  ✓ navdoc_basic
  ...

----------------------------------------
FAILED:
  ✗ custom_toc
    Error: Pattern not detected. Found: ['ncx_flat']

============================================================
```

### coverage

Generate pattern coverage report for EPUB files.

```bash
synth-analyze coverage <EPUB_PATH>
```

Shows which registered patterns are detected in the analyzed files.

## Workflow Example

Complete workflow for adding patterns from real EPUBs:

```bash
# 1. Discover patterns in sample EPUBs
synth-analyze discover ./samples/ --output new_patterns.yaml

# 2. Edit new_patterns.yaml to set decisions (new_pattern/variant/skip)

# 3. Add approved patterns
synth-analyze add-patterns new_patterns.yaml --validate

# 4. Verify all patterns work
synth-analyze validate
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error or validation failures |
