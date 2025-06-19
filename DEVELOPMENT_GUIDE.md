# synth_data_gen: Development & Contribution Guide
**Version:** 1.0
**Last Updated:** 2025-01-06

This document contains the core principles, workflows, and patterns for synth_data_gen. Adherence is mandatory for all contributions.

## 1. The SPARC-V-L³ Development Protocol
Every non-trivial task must follow this cycle:
1. **S - Specification:** Fully understand the goal and requirements.
2. **P - Plan:** Create detailed, step-by-step plan with TDD approach.
3. **A - Architecture:** Consult `docs/ARCHITECTURE.md` and analyze impact.
4. **R - Refine:** Implement following TDD cycle.
5. **C - Complete:** Ensure all tests pass (`python -m pytest`).
6. **V - Verify:** Run syntax checks, verify generator compatibility, check type hints.
7. **L¹ - Log:** Update `ACTIVITY_LOG.md` with detailed record.
8. **L² - Learn:** Self-analysis in `SELF_ANALYSIS_LOG.md`.
9. **L³ - Level Up:** Update this guide if systemic lessons learned.

## 2. Pytest TDD Requirements

### Test Execution
- **Primary:** `python -m pytest`
- **Verbose:** `python -m pytest -v`
- **Specific:** `python -m pytest tests/generators/test_epub_generator.py`
- **Component:** `python -m pytest tests/generators/epub_components/`

### Test Writing Standards
- All new functionality requires corresponding tests BEFORE implementation
- Use pytest fixtures for setup/teardown, especially `tmp_path` for file operations
- Mock external dependencies (ebooklib, reportlab) consistently
- Follow existing patterns in test structure and naming

### Test Migration Standards
- Convert unittest.TestCase to pytest functions
- Replace `self.assertEqual(a, b)` with `assert a == b`
- Replace `self.assertTrue(x)` with `assert x`
- Replace `with self.assertRaises(Error):` with `with pytest.raises(Error):`
- Use pytest fixtures instead of setUp/tearDown methods

### Probabilistic Testing
- When testing `_determine_count()` probabilistic behavior, ensure only ONE feature has probabilistic config
- Set all other features to exact integer values to avoid multiple `random.random()` calls
- Mock `random.random` with predictable return values for deterministic testing

## 3. Component-Based Architecture Patterns

### Generator Pattern
All generators must follow this pattern:
```python
class NewGenerator(BaseGenerator):
    GENERATOR_ID = "new_format"
    
    def __init__(self, global_config: dict, specific_config: dict):
        self.global_config = global_config
        self.specific_config = specific_config
    
    def generate(self, specific_config: dict, global_config: dict, output_path: str) -> str:
        # Implementation
        return output_path
    
    def get_default_specific_config(self) -> dict:
        return {...}
```

### EPUB Component Pattern
EPUB components must follow this pattern:
```python
class NewComponent(EpubComponent):
    def render(self, book: epub.EpubBook, config: dict, chapters: List[epub.EpubHtml]) -> None:
        # Configure based on config dictionary
        # Apply changes to book or chapters
        pass
```

### Configuration-Driven Design
- NO hardcoded variations (e.g., no `create_epub_taylor_hegel_headers`)
- Use configuration dictionaries to drive behavior
- Support combinatorial feature generation
- Follow Unified Quantity Specification for counts

## 4. Version Control & Workflow

**Branching Strategy:**
- `main`: Stable, deployable code
- `develop`: Integration branch for features
- `feature/ISSUE-123-description`: Individual features and fixes

**Commit Message Format:**
```
type(scope): brief description

- Detailed explanation of changes
- Why the change was made
- Any breaking changes or migration notes

Fixes #123
```

**Workflow Decision Matrix:**
- **Use PR workflow for:** Major architectural changes, component refactoring, breaking changes
- **Use direct merge for:** Bug fixes, documentation updates, test improvements (after review)

## 5. The Triple-Log System
1. **Application Log:** Python logging to console/files for runtime debugging
2. **`ACTIVITY_LOG.md`:** Immutable development action log
3. **`FEEDBACK_LOG.md` & `SELF_ANALYSIS_LOG.md`:** Learning and improvement logs

## 6. Verification Protocols (Prevents Critical Errors)

### High-Risk Operations Verification Protocol

1. **Generator Constructor Changes:**
   ```bash
   python -c "from synth_data_gen.generators.main_generator import MainGenerator; print('Import success')"
   python -c "from synth_data_gen.generators.epub import EpubGenerator; print('EPUB import success')"
   python -c "from synth_data_gen.generators.pdf import PdfGenerator; print('PDF import success')"
   python -c "from synth_data_gen.generators.markdown import MarkdownGenerator; print('Markdown import success')"
   ```

2. **Function Redefinition Fixes:**
   - Backup original file before changes
   - Run `python -m py_compile <file_path>` after each fix
   - Verify no duplicate function definitions with `grep -n "^def " <file_path>`

3. **Test Suite Health:**
   ```bash
   python -m pytest --tb=short
   python -m pytest tests/generators/test_pdf_generator.py -v
   ```

### Constructor Compatibility Verification
Before any generator changes:
1. Verify MainGenerator can instantiate the generator with `(global_config, specific_config)`
2. Test with minimal valid config dictionaries
3. Ensure no import errors occur

## 7. Context Awareness Protocol

### Before Making Decisions:
1. **Project Context Assessment:**
   - What phase of DEBUG_PLAN_130625_0602.md are we in?
   - Are there any constructor compatibility issues?
   - What is the current test suite health?

2. **Technology Context Assessment:**
   - What Python version does this project use (>=3.8)?
   - What are the existing patterns in generator implementations?
   - What pyproject.toml dependencies are available?

### Before Implementation:
1. **Pattern Analysis:** Understand existing solutions in codebase
2. **Dependency Verification:** Confirm all required packages (PyYAML, pytest, reportlab, ebooklib, jsonschema)
3. **Constraint Assessment:** Component-based architecture requirements, backward compatibility

## 8. Requirement Analysis Protocol

### Before Starting Tasks:
1. **Complete Requirement Reading:**
   - Read entire task description and linked documents
   - Read all test files (`test_*.py`) that define expected behavior
   - Read all error messages completely, especially TypeError messages

2. **Comprehension Verification:**
   - Can you explain the requirement clearly?
   - What are the acceptance criteria?
   - What is the expected outcome?

### For Python Package Specific Issues:
- Always check `pylance_issues.txt` for current type and syntax issues
- Verify import compatibility after any changes
- Test generator instantiation with MainGenerator pattern
- Check for function redefinitions using syntax validation

## 9. Python/pytest Specific Patterns

### Import Management
```python
# Relative imports within package
from .base import BaseGenerator
from ..common.utils import utility_function

# External imports
import pytest
from ebooklib import epub
from typing import Dict, Any, List, Optional
```

### Configuration Handling
```python
def _determine_count(self, config_value: Any, context_key_name: str) -> int:
    # Use inherited method from BaseGenerator
    # Handles integers, ranges, and probabilistic configs
```

### Mocking Patterns
```python
def test_generator_function(mocker):
    mock_random = mocker.patch('module.random.random', return_value=0.5)
    mock_external = mocker.patch('module.external_library.function')
    # Test implementation
    assert mock_random.called
```

## 10. Synthetic Data Generation Specific Guidelines

### Generator Responsibilities
- **EpubGenerator:** Complex document structure with components (headers, notes, ToC, citations)
- **PdfGenerator:** Layout-based documents with text, images, and formatting
- **MarkdownGenerator:** Structured text with frontmatter and content sections

### Component Design Principles
- Each component handles one aspect of document generation
- Components are composable and configurable
- No hardcoded content variations - use configuration parameters
- Support for probabilistic feature inclusion

### Configuration Schema Adherence
- Follow Unified Quantity Specification for all count-based configs
- Support both exact values and range/probabilistic specifications
- Validate configuration at multiple levels (schema, generator, component)

### Error Handling Standards
- Graceful degradation when optional features fail
- Comprehensive logging for debugging issues
- Clear error messages for configuration problems
- Never fail silently - always provide feedback

## 11. Systematic Verification Protocols (L³ Lesson: 2025-06-15)

### Mandatory Tool-Based Verification
**CRITICAL:** Never claim completion of complex fixes without tool verification.

#### Two-Phase Verification Protocol
```bash
# Phase 1: Implement fixes
# [perform fixes]

# Phase 2: MANDATORY verification
python -m pytest --tb=short
npx pyright . --outputjson | jq '.summary'
# OR: pylance diagnostic re-run

# Only claim completion AFTER Phase 2 verification
```

#### Completion Criteria Definition
- **"Fixed all X issues":** Must be verified by re-running the diagnostic tool that identified them
- **"Resolved type errors":** Must show reduced error count in tool output
- **"Tests passing":** Must show pytest success output

#### Verification Failure Protocol
If verification reveals remaining issues:
1. **Acknowledge Gap:** "Found X remaining issues after verification"
2. **Categorize Remaining:** Identify what was missed in original analysis
3. **Update Approach:** Modify methodology to address gaps
4. **Never Minimize:** Don't downplay significance of remaining issues

### Pattern Recognition Methodologies

#### Exhaustive Pattern Discovery Protocol
When fixing "all instances" of a pattern:

1. **Use Automated Search Tools:**
   ```bash
   # Find ALL instances, don't rely on memory
   rg -n "pattern_to_fix" path/
   rg -n "book\.toc = \(" .  # Example: find all tuple literals
   ```

2. **Differentiate Similar Patterns:**
   - `tuple()` function calls ≠ `(item1, item2)` literal syntax
   - CSS in headers.py ≠ CSS in other files
   - Same error message ≠ same fix approach

3. **Systematic File Coverage:**
   ```bash
   # Check all relevant files, not just first found
   find . -name "*.py" -exec rg -l "pattern" {} \;
   ```

#### Pattern Taxonomy Creation
Before starting complex fixes:
1. **Inventory All Error Types:** Create comprehensive list from diagnostic output
2. **Group by Fix Strategy:** Separate patterns requiring different approaches
3. **Estimate Scope:** Count instances per pattern type
4. **Prioritize by Impact:** Fix critical type errors before warnings

### User Signal Recognition Protocols

#### Signal Interpretation Guide
- **"Think ultra hard"** = "Your current approach is insufficient, reassess methodology"
- **"Think harder"** = "Step back, analyze more thoroughly"
- **Emphasis/caps** = Methodology critique, not intensity request
- **Questions about remaining issues** = Verification failure

#### Response Protocol for User Signals
1. **Pause Current Approach:** Don't continue with same methodology
2. **Assess Gaps:** What was missed in original analysis?
3. **Change Strategy:** Use different tools/approaches
4. **Communicate Understanding:** Acknowledge the signal explicitly

### Complex Task Management Protocols

#### TodoWrite-Driven Systematic Approach
For any task with >3 distinct fix categories:

```bash
# Create systematic tracking
TodoWrite: 
- Fix X issues in category A (N locations)
- Fix Y issues in category B (M locations)
- Verify completion with tool Z
```

#### Sequential Category Completion
- **Complete each category fully** before moving to next
- **Verify each category** with targeted searches
- **Update todo status** immediately after completion
- **Never batch multiple categories** in completion claims

#### Category Definition Standards
- **High Priority:** Type errors, compilation failures, critical functionality breaks
- **Medium Priority:** API misuse, deprecated patterns, performance issues  
- **Low Priority:** Style warnings, optional member access hints

## 12. Failure Recovery Protocols (L³ Lesson: 2025-06-15)

### When User Indicates Incomplete Work
1. **Immediate Acknowledgment:** "You're right, let me reassess..."
2. **Systematic Re-analysis:** Use tool output as ground truth
3. **Gap Identification:** What patterns were missed?
4. **Methodology Change:** Different approach than originally used
5. **Comprehensive Resolution:** Fix ALL identified issues

### Learning from Verification Failures
After any "completion" that proves incomplete:
1. **Document in FEEDBACK_LOG.md:** What went wrong and why
2. **Update methodology:** Add protocols to prevent recurrence  
3. **Self-analysis in SELF_ANALYSIS_LOG.md:** Deep understanding of failure patterns
4. **Guide Updates:** Add lessons to this development guide (L³ protocol)

### Success Redefinition
- **Success = Tool verification confirms completion**
- **Not success = Assumption-based claims**
- **Not success = "Mostly fixed" or "Primarily resolved"**
- **Not success = Fixing some instances without verifying all**

## 13. Quality Assurance Integration

### Pre-Commit Verification Checklist
- [ ] Syntax validation: `python -m py_compile affected_files`
- [ ] Type checking: `npx pyright affected_files`
- [ ] Test verification: `python -m pytest relevant_tests`
- [ ] Import verification: `python -c "import module; print('Import success')"`

### Complex Fix Quality Gates
1. **Initial State Documentation:** Record baseline error counts
2. **Incremental Verification:** Verify each fix category completion
3. **Final State Verification:** Re-run all diagnostic tools
4. **Regression Testing:** Ensure no new issues introduced
5. **Completion Documentation:** Tool output proving success

This systematic approach prevents the verification failures and incomplete analysis patterns identified in the 2025-06-15 Pylance crisis resolution.