# 🎯 CURRENT TASK: Stabilize and refactor synth_data_gen architecture
- **PLAN:** docs/DEBUG_PLAN_130625_0602.md
- **STATUS:** Phase 1 - Test Suite Overhaul (19 failing tests to fix)

---

## 🧠 CORE DIRECTIVES (VERIFY ON EVERY ACTION)

1. **SPARC-V-L³ Protocol:** You MUST follow the full SPARC-V-L³ cycle for all non-trivial changes as detailed in `DEVELOPMENT_GUIDE.md`.
2. **Pytest TDD is Non-Negotiable:** All changes must have corresponding tests. Run `python -m pytest` before any commit. Fix test failures immediately.
3. **Component-Based Architecture Compliance:** Follow the modular generator pattern with BaseGenerator inheritance and component-based EPUB generation.
4. **Verification is Mandatory:** Run tests (`python -m pytest`), check syntax (`python -m py_compile <file>`), and verify generator constructor compatibility.
5. **Log All Anomalies:** Any deviation from the plan, unexpected error, or user correction MUST be logged with structured detail in `FEEDBACK_LOG.md`.
6. **Log Your Actions:** At the end of every response, you MUST append a structured entry to `ACTIVITY_LOG.md`.
7. **Self-Critique:** After completing a significant task, you MUST perform a self-analysis and log it in `SELF_ANALYSIS_LOG.md`.

---

## 🔄 CONTEXT INITIALIZATION PROTOCOL (CRITICAL)

**MANDATORY:** Execute this protocol at the start of EVERY conversation and whenever context may have been compacted/refreshed.

### Context Refresh Detection Triggers:
- Beginning of any new conversation
- When you cannot recall recent task details or decisions
- When foundational documents are not in working memory
- When working on generator constructor compatibility issues
- When debugging test failures or architectural refactoring
- **CRITICAL: When `/compact` or memory reset occurs**
- **CRITICAL: Before ANY file deletion or destructive operation**

### IMMEDIATE INITIALIZATION SEQUENCE:
1. **ALWAYS READ FIRST:** 
   - `DEVELOPMENT_GUIDE.md` - Core principles, patterns, and methodologies
   - `docs/ARCHITECTURE.md` - System design and component relationships  
   - `PROJECT_STATUS.md` - Current project state and progress
   - `FEEDBACK_LOG.md` - Recent lessons and workflow decisions
   - `docs/DEBUG_PLAN_130625_0602.md` - Current refactoring plan and critical issues

2. **VERIFY UNDERSTANDING:**
   - Component-based architecture requirements
   - Pytest TDD methodology
   - SPARC-V-L³ protocol compliance
   - Generator constructor signature requirements (MainGenerator compatibility)
   - Current critical issues: TypeError constructor mismatches, function redefinitions, test failures

3. **LOAD PROJECT CONTEXT:**
   - Current phase of DEBUG_PLAN_130625_0602.md
   - Status of generator constructor fixes
   - Test suite health and failing tests
   - Component refactoring progress

**NEVER SKIP THIS PROTOCOL** - Inconsistent decisions result from missing foundational context.

---

## 📚 KNOWLEDGE BASE INTERACTION PROTOCOL

You are required to read the following documents at specific trigger points:

- **WHEN:** Starting *any* new task.
  - **READ:** `DEVELOPMENT_GUIDE.md` to refresh core principles.
  - **READ:** `docs/ARCHITECTURE.md` to understand the system context.
  - **READ:** `PROJECT_STATUS.md` to understand the current state.

- **WHEN:** Working on generator classes or MainGenerator integration.
  - **READ:** `synth_data_gen/generators/main_generator.py` and `synth_data_gen/core/base.py`.
  - **READ:** Current generator implementations to understand constructor patterns.

- **WHEN:** Debugging test failures or writing new tests.
  - **READ:** `tests/` directory structure and existing test patterns.
  - **READ:** `pylance_issues.txt` for current type and syntax issues.

- **WHEN:** Working on EPUB component refactoring.
  - **READ:** `synth_data_gen/generators/epub_components/` to understand current implementation.
  - **READ:** DEBUG_PLAN_130625_0602.md Phase 2 component architecture details.

- **WHEN:** A significant architectural decision is needed.
  - **ACTION:** Propose a new Architecture Decision Record (ADR) in `docs/decisions/`.

- **WHEN:** A task is complete.
  - **ACTION:** Update `CHANGELOG.md`, `PROJECT_STATUS.md`, and `SELF_ANALYSIS_LOG.md`.
  - **ACTION:** If systemic lesson learned, update `DEVELOPMENT_GUIDE.md`.

---

## 🛠️ PYTHON PACKAGE SPECIFIC GUIDELINES

### Testing Requirements
- **Primary Command:** `python -m pytest`
- **Specific Tests:** `python -m pytest tests/generators/test_epub_generator.py`
- **Verbose Mode:** `python -m pytest -v`
- **Component Tests:** `python -m pytest tests/generators/epub_components/`

### Installation & Development
- **Dev Install:** `pip install -e .`
- **Dependencies:** Managed via `pyproject.toml` - PyYAML, pytest, pytest-mock, reportlab, ebooklib, jsonschema

### Code Quality Verification
- **Syntax Check:** `python -m py_compile <file_path>`
- **Type Issues:** Review `pylance_issues.txt` for current issues
- **Import Verification:** Ensure all generator classes can be imported without errors

### Critical Constructor Pattern
All generators MUST follow this pattern:
```python
def __init__(self, global_config: dict, specific_config: dict):
    self.global_config = global_config
    self.specific_config = specific_config
```

### Component-Based Architecture Rules
- EPUB components inherit from `EpubComponent` base class
- Each component implements `render(book, config, chapters)` method
- Configuration-driven feature generation (no hardcoded variations)
- Modular, combinatorial approach for scalability

---

## 📝 IMPORTANT INSTRUCTION REMINDERS

### Current Critical Issues (Phase 1 Focus)
1. **Test Suite Instability:** 19 failing tests (9 PDF, 9 EPUB ToC, 1 EPUB Multimedia)
2. **Mocking Complexity:** `_determine_count()` mocking issues in PDF generator tests
3. **Mock Configuration:** EPUB ToC tests missing required mock attributes
4. **Unittest Legacy:** Migration to pytest needed for better test isolation

### Phase 1 Priority Focus
1. Fix PDF generator `_determine_count()` mocking issues FIRST
2. Fix EPUB ToC mock configuration problems SECOND
3. Complete unittest → pytest migration THIRD
4. Achieve 100% test suite passing FOURTH

### Phase Transition Criteria
- Phase 0 → Phase 1: ✅ COMPLETED (All constructors fixed, no redefinition errors, basic import functionality restored)
- Phase 1.5 → Phase 1: ✅ COMPLETED (Type safety improvements, 83% Pylance error reduction)
- Phase 1 → Phase 2: Full test suite passing, pytest migration complete
- Phase 2 → Phase 3: Component-based architecture implemented, old code removed

### Risk Management
- NEVER commit with failing tests
- ALWAYS verify test suite passes before major changes
- BACKUP complex test configurations before simplifying
- TEST each fix category in isolation before moving to next

---

## 🚨 CRITICAL FILE OPERATION SAFEGUARDS

### MANDATORY Pre-Deletion Analysis Protocol
**NEVER delete ANY file without completing ALL steps:**

1. **COMPLETE CONTENT READING:** Read entire file contents, understand every function/class
2. **NAMING PATTERN ANALYSIS:** 
   - `*_clean.py`, `*_fix.py` often indicate IMPROVED versions, not backups
   - `*_backup.py`, `*.backup` are typically safe to remove after verification
3. **DEPENDENCY IMPACT ANALYSIS:**
   - Search entire codebase for imports of the file
   - Check if file is referenced in any documentation
   - Analyze architectural role and relationships
4. **SIZE != REDUNDANCY:** Same file size does NOT indicate duplicate content
5. **JUSTIFICATION REQUIREMENT:** Must articulate WHY deletion is necessary and safe

### Dependency Analysis Requirements
**Before ANY destructive operation:**
- Create `docs/analysis/dependency-impact-FILENAME.md` documenting analysis
- Map all imports and references
- Understand architectural purpose and relationships
- Document potential impact of removal

### File Operation Verification Matrix
- **LOW RISK:** Documentation updates, adding new files
- **MEDIUM RISK:** Editing existing functionality with tests
- **HIGH RISK:** Renaming files, removing imports
- **CRITICAL RISK:** File deletion, removing functions, breaking interfaces

**CRITICAL RISK operations require explicit user confirmation after full analysis.**