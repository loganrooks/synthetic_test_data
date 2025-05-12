# Code Specific Memory
<!-- Entries below should be added reverse chronologically (newest first) -->
### [2025-05-11 05:01:49] BaseGenerator Class
- **Purpose**: Abstract base class for all synthetic data generators. Defines the common interface.
- **Files**: [`synth_data_gen/core/base.py`](synth_data_gen/core/base.py)
- **Status**: Implemented
- **Dependencies**: `abc` (Abstract Base Classes), `typing`
- **API Surface**: `GENERATOR_ID` (class attr), `generate()` (abstract), `validate_config()`, `get_default_specific_config()` (abstract)
- **Tests**: To be created by `tdd` mode.

### [2025-05-11 05:01:49] EpubGenerator Class
- **Purpose**: Concrete generator for creating EPUB files.
- **Files**: [`synth_data_gen/generators/epub.py`](synth_data_gen/generators/epub.py)
- **Status**: Implemented (initial refactor, `epub_components` integration is conceptual)
- **Dependencies**: `os`, `typing`, `ebooklib`, `synth_data_gen.core.base.BaseGenerator`, `synth_data_gen.common.utils`, `synth_data_gen.generators.epub_components`
- **API Surface**: Implements `BaseGenerator` interface.
- **Tests**: To be created by `tdd` mode.

### [2025-05-11 05:01:49] PdfGenerator Class
- **Purpose**: Concrete generator for creating PDF files.
- **Files**: [`synth_data_gen/generators/pdf.py`](synth_data_gen/generators/pdf.py)
- **Status**: Implemented (initial refactor, existing PDF functions moved into class structure)
- **Dependencies**: `os`, `typing`, `reportlab`, `synth_data_gen.core.base.BaseGenerator`, `synth_data_gen.common.utils`
- **API Surface**: Implements `BaseGenerator` interface. Internal methods for different PDF variants.
- **Tests**: To be created by `tdd` mode.

### [2025-05-11 05:01:49] MarkdownGenerator Class
- **Purpose**: Concrete generator for creating Markdown files.
- **Files**: [`synth_data_gen/generators/markdown.py`](synth_data_gen/generators/markdown.py)
- **Status**: Implemented (initial refactor, existing Markdown functions moved into class structure)
- **Dependencies**: `os`, `json`, `random`, `typing`, `synth_data_gen.core.base.BaseGenerator`, `synth_data_gen.common.utils`
- **API Surface**: Implements `BaseGenerator` interface. Internal methods for different MD variants and frontmatter.
- **Tests**: To be created by `tdd` mode.

### [2025-05-11 05:01:49] ConfigLoader Stub
- **Purpose**: Stub class for loading and validating configurations (YAML, JSON, Python dict).
- **Files**: [`synth_data_gen/__init__.py`](synth_data_gen/__init__.py) (defined within)
- **Status**: Implemented (Stub with basic loading for YAML/JSON/dict and default config generation)
- **Dependencies**: `os`, `yaml`, `json`, `typing`
- **API Surface**: `load_config()`
- **Tests**: To be created by `tdd` mode when fully implemented.
## Components Implemented

### [2025-05-11 04:47:37] Initial Code Migration to `synth_data_gen` Package
- **Purpose**: To organize existing Python scripts into a proper package structure.
- **Files**:
    - `synth_data_gen/__init__.py`: Main package entry point, now contains orchestrated calls to generator functions.
    - `synth_data_gen/common/__init__.py`: Package marker.
    - `synth_data_gen/common/utils.py`: Migrated from `common.py`, contains shared utility functions.
    - `synth_data_gen/generators/__init__.py`: Package marker.
    - `synth_data_gen/generators/epub.py`: Migrated from `generate_epubs.py`.
    - `synth_data_gen/generators/markdown.py`: Migrated from `generate_markdown.py`.
    - `synth_data_gen/generators/pdf.py`: Migrated from `generate_pdfs.py`.
    - `synth_data_gen/generators/epub_components/__init__.py`: Package marker.
    - `synth_data_gen/generators/epub_components/citations.py`: Migrated from `epub_generators/citations.py`.
    - `synth_data_gen/generators/epub_components/content_types.py`: Migrated from `epub_generators/content_types.py`.
    - `synth_data_gen/generators/epub_components/headers.py`: Migrated from `epub_generators/headers.py`.
    - `synth_data_gen/generators/epub_components/multimedia.py`: Migrated from `epub_generators/multimedia.py`.
    - `synth_data_gen/generators/epub_components/notes.py`: Migrated from `epub_generators/notes.py`.
    - `synth_data_gen/generators/epub_components/page_numbers.py`: Migrated from `epub_generators/page_numbers.py`.
    - `synth_data_gen/generators/epub_components/structure.py`: Migrated from `epub_generators/structure.py`.
    - `synth_data_gen/generators/epub_components/toc.py`: Migrated from `epub_generators/toc.py`.
- **Status**: Implemented (Initial migration and import fixing).
- **Dependencies**: `os`, `ebooklib`, `reportlab`. (Existing dependencies, no new ones added in this step).
- **API Surface**: The main `synth_data_gen.generate_data()` function is now populated with the orchestration logic. Internal structure of generators is largely unchanged beyond file relocation and import updates.
- **Tests**: Not part of this task. To be addressed by `tdd` mode.