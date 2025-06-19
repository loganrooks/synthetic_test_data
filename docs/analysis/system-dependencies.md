# System Dependencies Analysis
**Version:** 1.0  
**Last Updated:** 2025-01-06  
**Purpose:** Comprehensive mapping of architectural dependencies to prevent destructive operations

## Import Dependency Map

### Core Layer Dependencies
```
synth_data_gen/core/
├── base.py → No internal dependencies (foundational)
├── config_loader.py → Uses base.py exceptions, jsonschema
└── __init__.py → Imports InvalidConfigError from core
```

### Generator Layer Dependencies
```
synth_data_gen/generators/
├── main_generator.py → Imports ALL generators (epub, pdf, markdown)
├── epub.py → Imports epub_components.*, core.base, common.utils
├── pdf.py → Imports core.base, common.utils, reportlab.*
├── markdown.py → Imports core.base, common.utils
└── __init__.py → Empty (package marker)
```

### EPUB Components Dependencies
```
synth_data_gen/generators/epub_components/
├── citations.py → common.utils, ebooklib
├── content_types.py → common.utils, ebooklib  
├── headers.py → common.utils, ebooklib
├── multimedia.py → common.utils, ebooklib
├── notes.py → common.utils, ebooklib
├── page_numbers.py → common.utils, ebooklib
├── structure.py → common.utils, ebooklib
├── toc.py → common.utils, ebooklib (738 lines - main functions + examples)
├── toc_fix.py → ebooklib only (143 lines - clean implementations)
└── __init__.py → Empty (package marker)
```

## Critical Architectural Relationships

### MainGenerator Orchestration Pattern
```python
# main_generator.py instantiates generators with:
generator_instance = generator_class(self.config, format_config)

# This requires ALL generators to have compatible constructors:
def __init__(self, global_config: dict, specific_config: dict)
```

### EPUB Component System Pattern
```python
# epub.py imports components like:
from .epub_components import citations, headers, notes, toc, etc.

# Any missing component breaks epub.py imports
```

### Common Utilities Dependencies
```python
# Multiple generators depend on:
from ..common.utils import ensure_output_directories
from ..common.utils import EPUB_DIR, _create_epub_book, etc.
```

## File Naming Pattern Analysis

### Backup/Version Patterns
- `*.backup` → Original corrupted versions (safe to remove after verification)
- `*_clean.py` → **IMPROVED/FIXED versions** (NEVER delete without analysis)
- `*_fix.py` → **BUGFIX versions** (NEVER delete without analysis)  
- `*_old.py` → Deprecated versions (verify no references before removal)
- `*_temp.py` → Temporary work files (verify completion before removal)

### Current Critical Files
- `pdf.py` (1100 lines) → Current working PDF generator
- `pdf.py.backup` (1678 lines) → Original corrupted version with redefinitions
- `toc.py` (738 lines) → Main ToC functions + examples 
- `toc.py.backup` (902 lines) → Original with redefinitions
- `toc_fix.py` (143 lines) → Clean ToC implementations (potential replacement)

## Risk Assessment Matrix

### SAFE Operations
- Reading any file
- Creating new files
- Editing file contents with backup
- Adding imports or functions

### DANGEROUS Operations  
- Deleting any `.py` file
- Removing import statements
- Changing function signatures
- Renaming files that are imported

### CRITICAL Operations (Require Full Analysis)
- Deleting generator files (breaks MainGenerator)
- Removing epub_components (breaks epub.py imports)
- Deleting utility files (breaks multiple generators)
- Changing constructor signatures (breaks instantiation)

## Pre-Operation Checklist

### Before ANY file deletion:
1. ✅ Read complete file contents
2. ✅ Analyze naming pattern implications
3. ✅ Search codebase for all imports/references
4. ✅ Understand architectural role and purpose
5. ✅ Document analysis in `docs/analysis/dependency-impact-FILENAME.md`
6. ✅ Get explicit user confirmation for critical operations

### Before ANY import changes:
1. ✅ Map all dependent files
2. ✅ Test import compatibility
3. ✅ Verify no circular dependencies
4. ✅ Update documentation if needed

## Recovery Procedures

### If File Accidentally Deleted:
1. Check git history: `git log --oneline --name-only | grep FILENAME`
2. Check backup files in same directory
3. Recreate from backup or git restore
4. Document what was lost in FEEDBACK_LOG.md

### If Import Dependencies Broken:
1. Identify all affected files with import errors
2. Trace dependency chain to root cause
3. Fix imports or restore missing files
4. Test all affected generators/components

## Lessons Learned

### Critical Error (2025-01-06):
- Deleted `pdf_clean.py` without content analysis
- File naming suggested it was an IMPROVED version
- Could have contained cleaned implementations without redefinitions
- User intervention prevented potential architectural damage

### Prevention Strategy:
- This document exists to map dependencies
- CLAUDE.md updated with mandatory protocols
- FEEDBACK_LOG.md records all errors for learning
- Never assume file purpose without full analysis