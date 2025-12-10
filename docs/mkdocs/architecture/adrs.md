# Architecture Decision Records

This project uses Architecture Decision Records (ADRs) to document significant design decisions.

## ADR Index

### ADR-001: Combinatoric Test Generation

**Status**: Accepted

**Context**: Need to generate diverse test data covering all format combinations.

**Decision**: Implement a configuration-driven approach with probabilistic quantities.

**Consequences**:
- Flexible generation of varied test data
- Reproducible output with seed support
- Configuration complexity for users

[Full ADR](../../adr/ADR-001-combinatoric-test-generation.md)

---

### ADR-002: EPUB Pattern Analyzer

**Status**: Accepted

**Context**: Need to discover and catalog formatting patterns from real EPUB files.

**Decision**: Create an analyzer module with pattern registry, detection, and validation.

**Consequences**:
- Can learn patterns from real books
- Ensures generator can produce what analyzer detects
- Additional maintenance of pattern definitions

[Full ADR](../../adr/ADR-002-epub-pattern-analyzer.md)

---

## ADR Template

For new decisions, use this template:

```markdown
# ADR-NNN: Title

## Status

[Proposed | Accepted | Deprecated | Superseded]

## Context

What is the issue that we're seeing that is motivating this decision?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult to do because of this change?
```

## Guidelines

- Create a new ADR for significant architectural decisions
- ADRs are immutable once accepted; create new ones to supersede
- Keep ADRs concise but complete
- Link related ADRs to each other
