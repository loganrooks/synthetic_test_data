---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description
A clear and concise description of the feature you'd like.

## Use Case
Describe the problem you're trying to solve or the use case this would enable.

**Example:**
> I'm testing a PDF parser that needs to handle documents with complex table layouts. Currently, synth_data_gen only generates simple tables...

## Proposed Solution
How you think this could be implemented (optional).

## Alternatives Considered
Any alternative solutions or workarounds you've considered.

## Configuration Example
If applicable, show what the configuration might look like:

```yaml
pdf:
  tables:
    complex_layouts:
      enable: true
      merged_cells_chance: 0.3
      nested_tables_chance: 0.1
```

## Output Example
If applicable, describe or show what the generated output should look like.

## Priority
How important is this feature to your use case?
- [ ] Critical - Blocking my work
- [ ] High - Would significantly improve my workflow
- [ ] Medium - Nice to have
- [ ] Low - Just an idea

## Additional Context
Add any other context, screenshots, or examples here.

## Related Issues
Link any related issues or discussions.
