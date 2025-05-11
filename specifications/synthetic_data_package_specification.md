# Synthetic Data Package Specification

## 1. Introduction

This document outlines the detailed specifications for a Python package designed to generate synthetic test data, primarily focusing on EPUB, PDF, and Markdown formats. The package aims to be configurable, extensible, and capable of producing a wide variety of complex and realistic test files based on the analyses in [`docs/synthetic_data_requirements.md`](docs/synthetic_data_requirements.md) and [`docs/epub_formatting_analysis_report.md`](docs/epub_formatting_analysis_report.md).

## 2. Package API

The package will be named `synth_data_gen`.

### 2.1. Main Public Function

```python
def generate_data(config_path: str = None, config_obj: dict = None, output_dir: str = "synthetic_output") -> list[str]:
    """
    Generates synthetic data files based on the provided configuration.

    Either 'config_path' (path to a YAML/JSON configuration file) or 
    'config_obj' (a Python dictionary representing the configuration) must be provided.
    If both are provided, 'config_obj' takes precedence.
    If neither is provided, default data generation will occur.

    Args:
        config_path (str, optional): Path to the YAML or JSON configuration file. 
                                     Defaults to None.
        config_obj (dict, optional): A Python dictionary representing the configuration.
                                     Defaults to None.
        output_dir (str, optional): The root directory where generated files will be saved.
                                    Defaults to "synthetic_output".

    Returns:
        list[str]: A list of paths to the generated files.

    Raises:
        ValueError: If both config_path and config_obj are None and no default 
                    configuration is set up for "out-of-the-box" behavior.
        FileNotFoundError: If config_path is provided but the file does not exist.
        InvalidConfigError: If the configuration (from file or object) is invalid 
                            (e.g., missing required fields, incorrect data types).
        GeneratorError: If an error occurs within a specific data generator.
    """
    pass
```

**Example Usage:**

```python
import synth_data_gen
import os

# Option 1: Using a configuration file for deterministic output
# Assume my_deterministic_config.yaml uses exact integers for all _config parameters
try:
    generated_files_from_file = synth_data_gen.generate_data(config_path="config/my_deterministic_config.yaml", output_dir="custom_output_deterministic")
    print(f"Generated deterministic files: {generated_files_from_file}")
except Exception as e:
    print(f"Error generating data from file: {e}")

# Option 2: Using a Python dictionary configuration object
my_config = {
    "output_directory_base": "python_config_output",
    "global_settings": {
        "default_author": "Dr. Synth",
        "default_language": "en-US"
    },
    "file_types": [
        {
            "type": "epub",
            "count": 1, 
            "output_subdir": "epubs_generated/exact_counts_showcase",
            "epub_specific_settings": {
                "chapters_config": 5, # Exact number of chapters
                "sections_per_chapter_config": 2, # Exact sections per chapter
                "toc_style": "ncx_deeply_nested",
                "include_images": True,
                "images_config": 3, # Exact number of images
                "notes_config": 10 # Exactly 10 notes in the document
            }
        },
        {
            "type": "epub",
            "count": 1, 
            "output_subdir": "epubs_generated/ranged_counts_showcase",
            "epub_specific_settings": {
                "chapters_config": { "min": 2, "max": 4 }, # Ranged chapters
                "sections_per_chapter_config": { "min": 1, "max": 3 }, # Ranged sections
                "toc_style": "navdoc_full",
                "include_images": True,
                "images_config": { "min": 1, "max": 5 }, # Ranged images
                "notes_config": { "min": 5, "max": 15 } # Ranged notes
            }
        },
        {
            "type": "epub",
            "count": 1, 
            "output_subdir": "epubs_generated/probabilistic_counts_showcase",
            "epub_specific_settings": {
                "chapters_config": { "min": 3, "max": 5 }, # Using range for chapters here as an example
                "sections_per_chapter_config": { "chance": 0.8, "per_unit_of": "chapter", "max_total": 4 },
                "toc_style": "navdoc_basic",
                "include_images": True,
                "images_config": { "chance": 0.6, "per_unit_of": "chapter", "max_total": 7 },
                "notes_config": { "chance": 0.25, "per_unit_of": "paragraph", "max_total": 30 }
            }
        },
        {
            "type": "markdown",
            "count": 1,
            "output_subdir": "markdown_docs/deterministic_md",
            "markdown_specific_settings": {
                "include_frontmatter": True,
                "frontmatter_type": "yaml",
                "headings_config": 5, # Exact 5 headings
                "max_heading_depth": 3,
                "gfm_features": {
                    "md_tables_occurrence_config": 1, # Exactly 1 table
                    "md_table_rows_config": 4,       # With 4 rows
                    "md_table_cols_config": 3        # And 3 columns
                }
            }
        }
    ]
}
try:
    generated_files_from_obj = synth_data_gen.generate_data(config_obj=my_config)
    print(f"Generated files from object: {generated_files_from_obj}")
except Exception as e:
    print(f"Error generating data from object: {e}")

# Option 3: Using default "out-of-the-box" generation (should be deterministic)
try:
    default_files = synth_data_gen.generate_data(output_dir="default_run_output")
    print(f"Default generated files: {default_files}")
except Exception as e:
    print(f"Error generating default data: {e}")

```

### 2.2. Core Classes (Internal, but relevant for extensibility)

While not directly public for typical users, the following conceptual classes will form the backbone and will be key for extensibility:

*   `BaseGenerator`: An abstract base class for all data generators.
    *   `generate(self, specific_config: dict, global_config: dict, output_path: str) -> str`: Abstract method to generate a single file.
    *   `validate_config(self, specific_config: dict, global_config: dict) -> bool`: Method to validate the specific configuration for this generator.
*   `EpubGenerator(BaseGenerator)`: Generator for EPUB files.
*   `PdfGenerator(BaseGenerator)`: Generator for PDF files.
*   `MarkdownGenerator(BaseGenerator)`: Generator for Markdown files.
*   `ConfigLoader`: Class responsible for loading and validating configuration files or objects.
*   `PluginManager`: Class responsible for discovering and loading custom generator plugins.

### 2.3. Custom Exceptions

*   `InvalidConfigError(ValueError)`: Raised for issues with the configuration structure or values.
*   `GeneratorError(RuntimeError)`: Base class for errors occurring within a specific generator.
    *   `EpubGenerationError(GeneratorError)`
    *   `PdfGenerationError(GeneratorError)`
    *   `MarkdownGenerationError(GeneratorError)`
*   `PluginError(RuntimeError)`: Raised for issues related to loading or executing plugins.

## 3. Configuration Mechanism

A **hybrid approach** is proposed for configuration, prioritizing YAML files for ease of use and version control, but allowing programmatic configuration via Python dictionaries for advanced use cases or integration into other systems.

**Justification:**
*   **YAML files:** Human-readable, easy to edit, support comments, good for complex nested structures, and well-supported by Python libraries. Ideal for defining standard test sets.
*   **Python Dictionaries:** Offers maximum flexibility for dynamic configuration generation, scripting, and integration within larger Python applications.

If both a `config_path` (YAML/JSON) and a `config_obj` (Python dict) are provided to `generate_data`, the `config_obj` will take precedence.

### 3.1. YAML/JSON Configuration File Schema

The configuration file will have a root structure. JSON will also be supported, following the same schema.

**Note on "Unified Quantity Specification":** Many parameters below that control counts or occurrences (often ending in `_config`) accept a "Unified Quantity Specification". This is a critical feature for **testability**, allowing precise control. The value can be:
1.  An **exact integer** (e.g., `chapters_config: 5`): For deterministic, precise counts, ideal for unit testing. This is often the preferred method for baseline tests.
2.  A **range object** with `min` and `max` integer keys (e.g., `chapters_config: { "min": 3, "max": 7 }`): For generating a random count within an inclusive range, useful for creating varied datasets.
3.  A **probabilistic object** (e.g., `notes_config: { "chance": 0.1, "per_unit_of": "paragraph", "max_total": 20 }`): For flexible, chance-based generation. It includes:
    *   `chance`: (float, 0.0-1.0) Probability of occurrence.
    *   `per_unit_of`: (string, optional) Defines the scope of the `chance` (e.g., "paragraph", "chapter", "document"). This is context-dependent based on the parameter.
    *   `max_total`: (integer, optional) An overall cap on the number of generated elements if `chance` is used.

Default values for `_config` parameters are specified below; many will default to exact integers to support out-of-the-box testability.

```yaml
# Root Configuration Schema

output_directory_base: "path/to/output" # string, optional

global_settings:
  default_author: "Synthetic Data Corp." # string, optional
  default_language: "en" # string, optional (ISO 639-1 code)
  default_publisher: "SynthPress" # string, optional
  base_seed: null # integer or null, optional. If set, used for reproducible randomness.

file_types:
  - type: "epub" 
    count: 5      
    output_subdir: "my_epubs" 
    filename_pattern: "book_{index}_{slug_title}.epub" 
    content_source_theme: "philosophy_excerpts" 
    epub_specific_settings: { ... } 

  - type: "pdf"
    count: 10
    output_subdir: "academic_papers"
    pdf_specific_settings: { ... }
```

#### 3.1.1. `epub_specific_settings` Schema
Parameters ending in `_config` accept the "Unified Quantity Specification". Default values prioritize deterministic counts for testability.

```yaml
epub_specific_settings:
  # --- Content & Structure ---
  chapters_config: 5 # UnifiedQuantitySpecification, optional, default: 5 (exact)
  sections_per_chapter_config: 2 # UnifiedQuantitySpecification, optional, default: 2 (exact)
  epigraph_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (disabled by default, meaning exactly zero epigraphs)
                     # Example if enabled: epigraph_config: 1 (exactly one per scope)
                     # Example probabilistic: epigraph_config: { "chance": 0.05, "per_unit_of": "chapter_or_section" }


  # --- Metadata ---
  author: "Custom EPUB Author" # string, optional
  title_prefix: "Synthetic Study: " # string, optional
  language: "fr" # string, optional
  publisher: "EPUB Gen Inc." # string, optional
  isbn: "978-3-16-148410-0" # string, optional (can be placeholder)
  publication_date: "YYYY-MM-DD" # string, optional (can be "random")
  series_name: "Test Series" # string, optional
  series_number: 1 # integer or string, optional
  
  # --- EPUB Version & Technical ---
  epub_version: 3 # integer, optional, default: 3 (Allowed: 2, 3)
  include_ncx: "auto" # string, optional, default: "auto" 
  include_nav_doc: "auto" # string, optional, default: "auto" 
  font_embedding: # optional, default: no embedding
    enable: True # boolean
    fonts: # list of font families
      - "Liberation Serif"
      - "DejaVu Sans"
    obfuscation: "none" # string, optional, default: "none"

  # --- Table of Contents (ToC) ---
  toc_settings:
    style: "navdoc_full" # string, optional, default: "navdoc_full" for EPUB3, "ncx_deeply_nested" for EPUB2
    max_depth: 3 # integer, optional, default: 3
    include_landmarks: True # boolean, optional, default: True
    include_page_list_in_toc: True # boolean, optional, default: True
    ncx_problematic_label_chance: 0.0 # float, optional, default: 0.0
    ncx_list_footnote_files_chance: 0.0 # float, optional, default: 0.0

  # --- Page Numbering ---
  page_numbering:
    style: "epub3_semantic" # string, optional, default: "epub3_semantic" for EPUB3, "anchor_based" for EPUB2
    link_to_page_markers: True # boolean, optional, default: True
    text_page_number_format: "arabic" # string, optional, default: "arabic"
    text_page_number_prefix: "p. " # string, optional
    text_page_number_suffix: "" # string, optional

  # --- Headers/Footers (Visual) ---
  content_headers: 
    enable: False # boolean, optional, default: False
  content_footers: 
    enable: False # boolean, optional, default: False

  # --- Citations/Footnotes/Endnotes ---
  notes_system:
    type: "footnotes_same_page" # string, optional, default: "footnotes_same_page"
    notes_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (disabled by default, meaning exactly zero notes)
                    # Example if enabled for testing: notes_config: 10 (exactly 10 notes)
                    # Example probabilistic: notes_config: { "chance": 0.1, "per_unit_of": "paragraph", "max_total": 20 }
    secondary_note_type: "endnotes_book" # string, optional
    secondary_note_marker_style: "editorial_symbol" # string, optional
    secondary_notes_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (disabled)
    reference_style: # How note references appear in text
      style: "linked_superscript_number" # string, optional, default: "linked_superscript_number"
      symbols: ["*", "†", "‡", "§", "||"] # list of strings, optional
    note_text_structure: # How note text is formatted
      style: "paragraph_with_backlink" # string, optional, default: "paragraph_with_backlink"
    include_translator_notes_chance: 0.0 # float, optional, default: 0.0
    translator_note_prefix: "{TN: " # string, optional
    translator_note_suffix: "}" # string, optional

  # --- Citations & Bibliography ---
  citations_bibliography:
    in_text_citation_style: "none" # string, optional, default: "none"
    bibliography_style:
      style: "dedicated_file_list" # string, optional, default: "dedicated_file_list"
      include_cite_tags: True # boolean, optional, default: False
      biblio_entry_backlink_chance: 0.0 # float, optional, default: 0.0

  # --- Multimedia ---
  multimedia:
    include_images: True # boolean, optional, default: True
    images_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (no images by default)
                     # Example if enabled for testing: images_config: 2 (exactly 2 images)
    image_types: ["jpeg", "png"] # list of strings, optional, default: ["jpeg", "png", "gif"]
    image_usage_profile: "placeholder_images" # string, optional, default: "placeholder_images"
    image_caption_style: "none" # string, optional, default: "none"
    include_audio_video: False # boolean, optional, default: False (EPUB3 only)

  # --- Content Element Styling & Variety ---
  content_elements:
    paragraph_styles: # Defines variety in paragraph styling
      - { class_name: "indent", chance: 0.7 }
      - { class_name: "noindent", chance: 0.2 }
      - { class_name: "epigraph", chance: 0.0 } # Disabled by default, occurrence linked to epigraph_config
    heading_styles: # How H1-H6 are represented
      chapter_title_style: "standard_h_tags" # string, optional, default: "standard_h_tags"
      section_header_style: "standard_h_tags" # string, optional, default: "standard_h_tags"
    blockquote_styles:
      style: "standard_blockquote" # string, optional, default: "standard_blockquote"
    list_styles:
      include_ordered_lists: True # boolean, optional, default: True
      include_unordered_lists: True # boolean, optional, default: True
      list_items_config: 5 # UnifiedQuantitySpecification, optional, default: 5 (exact items per list)
      max_list_nesting_depth: 2 # integer, optional, default: 2
    table_styles: # For generating tables within content
      tables_occurrence_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (no tables by default)
                                  # Example for testing: tables_occurrence_config: 1 (exactly one table)
      table_rows_config: 3        # UnifiedQuantitySpecification, default: 3 (exact rows if table occurs)
      table_cols_config: 3        # UnifiedQuantitySpecification, default: 3 (exact columns if table occurs)
    code_block_styles:
      code_blocks_occurrence_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (no code blocks by default)
                                       # Example for testing: code_blocks_occurrence_config: 1 (exactly one code block)
    poetry_formatting:
      poetry_occurrence_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (no poetry by default)
      style: "style_hegel_por" # string, optional

  # --- Structural Elements (EPUB specific) ---
  structural_elements:
    include_front_matter: True # boolean, optional, default: True
    include_back_matter: True # boolean, optional, default: True
    include_calibre_metadata_files: "none" # string, optional, default: "none"
    include_sigil_metadata_files: "none" # string, optional, default: "none"
    include_adobe_xpgt_adept_tags: "none" # string, optional, default: "none"
    split_content_files_chance: 0.0 # float, optional, default: 0.0
    split_filename_suffix: "_split_" # string, optional
    segment_chapter_files_chance: 0.0 # float, optional, default: 0.0
    segment_suffix_pattern: ["", "a", "b"] # list of strings, optional

  # --- Typography & Layout (CSS driven) ---
  typography_layout:
    base_font_family: ["Liberation Serif", "Georgia", "serif"] # list of strings, optional
    heading_font_family: ["Liberation Sans", "Arial", "sans-serif"] # list of strings, optional
    margins_cm: 2.0 # float or object {top, bottom, left, right}, optional, default: 2.0
    line_spacing_multiplier: 1.5 # float, optional, default: 1.5
    text_alignment: "justify" # string, optional, default: "justify"

  # --- Edge Cases & Miscellaneous ---
  edge_cases: # All default to 0.0 (disabled) for baseline predictability
    minimal_opf_metadata_chance: 0.0 
    conflicting_metadata_chance: 0.0 
    malformed_html_chance: 0.0 
    unusual_css_class_usage_chance: 0.0 
    empty_content_file_chance: 0.0 
    image_only_file_chance: 0.0 
    non_ascii_chars_chance: 0.0 
    doi_link_chance: 0.0 
    index_term_markers_chance: 0.0 
    forced_page_break_div_chance: 0.0 
    bracketed_numbers_paragraph_chance: 0.0 
```

#### 3.1.2. `pdf_specific_settings` Schema
Default values prioritize deterministic counts.
```yaml
pdf_specific_settings:
  generation_method: "from_html" # string, optional, default: "from_html"
  page_count_config: 10 # UnifiedQuantitySpecification, optional, default: 10 (exact pages)
  layout:
    columns: 1 # integer, optional, default: 1
    margins_mm: # object, optional, default: { top: 20, bottom: 20, left: 25, right: 25 }
      top: 20
      bottom: 20
      left: 25
      right: 25
  base_font_family: "Times New Roman" # string, optional
  base_font_size_pt: 12 # integer, optional
  ligature_simulation_chance: 0.0 # float, optional, default: 0.0
  running_header: # object, optional
    enable: True
    left_content: "{book_title}" 
    center_content: ""
    right_content: "Page {page_number}"
    font_size_pt: 9
    include_on_first_page: False
  running_footer: # object, optional
    enable: True
    left_content: "© {year} {publisher}"
    center_content: ""
    right_content: ""
    font_size_pt: 9
    include_on_first_page: True
  visual_toc: # object, optional
    enable: True
    max_depth: 3
    style: "hyperlinked_text" 
    page_number_style: "dot_leader" 
  author: "PDF Author" # string, optional
  title: "Synthetic PDF Document" # string, optional
  subject: "Test Data" # string, optional
  keywords: ["synthetic", "pdf", "test"] # list of strings, optional
  creator_tool: "SynthDataGen PDF Module" # string, optional
  ocr_simulation_settings: # Only if generation_method is "ocr_simulation"
    base_image_quality: "high" 
    ocr_accuracy_level: 0.98 # Default for high quality
    include_skew_chance: 0.0 # Default to no skew
    include_noise_chance: 0.0 # Default to no noise
    include_handwritten_annotations_chance: 0.0 # Default to no annotations
  table_generation: 
    pdf_tables_occurrence_config: 0 # UnifiedQuantitySpecification, default: 0 (no tables)
                                    # Example: pdf_tables_occurrence_config: 1 (exactly one table)
  figure_generation: 
    pdf_figures_occurrence_config: 0 # UnifiedQuantitySpecification, default: 0 (no figures)
                                     # Example: pdf_figures_occurrence_config: 2 (exactly two figures)
  include_rotated_pages_chance: 0.0 # float, default: 0.0
  mixed_page_sizes_orientations_chance: 0.0 # float, default: 0.0
```

#### 3.1.3. `markdown_specific_settings` Schema
Default values prioritize deterministic counts.
```yaml
markdown_specific_settings:
  headings_config: 5 # UnifiedQuantitySpecification, optional, default: 5 (exact headings)
  max_heading_depth: 3 # integer, optional, default: 3
  include_emphasis_styles: True # boolean, optional, default: True
  include_lists: True # boolean, optional, default: True
  md_list_items_config: 4 # UnifiedQuantitySpecification, optional, default: 4 (exact items per list)
  list_max_nesting_depth: 2 # integer, optional, default: 2
  list_type_mix_chance: 0.0 # float, optional, default: 0.0 (no mix by default)
  include_links: True # boolean, optional, default: True
  link_style_mix_chance: 0.0 # float, optional, default: 0.0 (consistent link style)
  include_images: True # boolean, optional, default: True
  md_images_config: 1 # UnifiedQuantitySpecification, optional, default: 1 (exactly one image)
  include_blockquotes: True # boolean, optional, default: True
  blockquote_max_nesting_depth: 1 # integer, optional, default: 1
  include_horizontal_rules: True # boolean, optional, default: True
  gfm_features:
    md_tables_occurrence_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (no tables)
                                   # Example: md_tables_occurrence_config: 1 (exactly one table)
    md_table_rows_config: 3        # Default if table occurs
    md_table_cols_config: 3        # Default if table occurs
    table_include_alignment_chance: 0.0 
    table_inline_markdown_chance: 0.0 
    md_footnotes_occurrence_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (no GFM footnotes)
                                      # Example: md_footnotes_occurrence_config: 3 (exactly 3 footnotes)
    footnote_multi_paragraph_chance: 0.0 
    md_task_lists_occurrence_config: 0 # UnifiedQuantitySpecification, optional, default: 0 (no task lists)
    include_code_blocks: True # boolean, optional, default: True
    md_code_blocks_config: 1 # UnifiedQuantitySpecification, optional, default: 1 (exactly one code block)
    code_block_style_mix_chance: 0.0 
    code_block_fenced_include_language_chance: 1.0 # Default to include language for fenced blocks
  frontmatter:
    include_chance: 1.0 # Default to include frontmatter
    style: "yaml" 
    fields: 
      title: True
      author: True
      date: "2025-01-01" # Fixed date for default
      tags: ["synthetic", "test", "deterministic"] 
      custom_fields: []
    syntax_error_chance: 0.0 
  embed_html_chance: 0.0 
  embed_latex_chance: 0.0 
  mixed_line_endings_chance: 0.0 
  encoding_issues_chance: 0.0 
  max_overall_nesting_depth: 3 
```

### 3.2. Python API-based Configuration

Users can pass a Python dictionary structured identically to the YAML schema directly to the `config_obj` parameter of `generate_data`. This allows for dynamic generation of configurations.

```python
# Example of programmatic configuration (already shown in API usage)
detailed_python_config = {
    "output_directory_base": "api_driven_output",
    "global_settings": {"default_language": "de"},
    "file_types": [
        {
            "type": "epub",
            "count": 1,
            "epub_specific_settings": {
                "chapters_config": 1, 
                "toc_settings": {"style": "ncx_simple"},
                "notes_system": {"type": "none", "notes_config": 0}, # Explicitly 0 notes
                "typography_layout": {"text_alignment": "left"}
            }
        }
        # ... more configurations
    ]
}
# synth_data_gen.generate_data(config_obj=detailed_python_config)
```

### 3.3. User Specification Details

The configuration schema addresses how users specify:
*   **Types of synthetic data:** Via the `file_types.[].type` field.
*   **Number of files:** Via the `file_types.[].count` field.
*   **Specific parameters for each generator:** Via `file_types.[].<type>_specific_settings` (e.g., `epub_specific_settings`). These nested objects contain all the granular controls, including those using the "Unified Quantity Specification".
*   **Output directory structure:** Via `output_directory_base` and `file_types.[].output_subdir`.

## 4. Extensibility Points

### 4.1. Adding New Synthetic Data Generators

Users can add generators for new file formats (e.g., DOCX, XML) or new variations of existing ones.

1.  **Abstract Base Class/Interface:**
    Custom generators must inherit from `synth_data_gen.core.BaseGenerator` (actual path TBD) and implement its abstract methods:
    ```python
    from synth_data_gen.core import BaseGenerator # Hypothetical path
    import os 

    class MyCustomDocxGenerator(BaseGenerator):
        GENERATOR_ID = "custom_docx" # Unique identifier used in config

        def generate(self, specific_config: dict, global_config: dict, output_path_base: str, file_index: int, common_vars: dict) -> str:
            """
            Generates a single DOCX file.
            'specific_config' contains settings from 'custom_docx_settings' in the main config.
            'global_config' contains 'global_settings'.
            'output_path_base' is the directory for this generator job.
            'file_index' is the current index of the file being generated (0 to count-1).
            'common_vars' can include things like a pre-generated slug_title, uuid.
            Should return the full path to the generated file.
            """
            # ... implementation using python-docx or similar ...
            filename = self.construct_filename(specific_config.get("filename_pattern"), 
                                               self.GENERATOR_ID, 
                                               common_vars.get("slug_title", "doc"), 
                                               file_index, 
                                               "docx", # extension
                                               common_vars.get("uuid"),
                                               common_vars.get("timestamp"))
            full_output_path = os.path.join(output_path_base, filename)
            # ... logic to create and save DOCX at full_output_path ...
            # Example:
            # from docx import Document
            # document = Document()
            # document.add_heading('Document Title', 0)
            # document.save(full_output_path)
            return full_output_path

        def validate_config(self, specific_config: dict, global_config: dict) -> bool:
            """
            Validates the 'custom_docx_settings' part of the configuration.
            Raise InvalidConfigError if issues are found.
            Return True if valid.
            """
            # ... validation logic ...
            # Example:
            # if "my_required_docx_param" not in specific_config:
            #     raise InvalidConfigError(f"Missing 'my_required_docx_param' for {self.GENERATOR_ID}")
            return True
        
        def get_default_specific_config(self) -> dict:
            """
            Returns a dictionary of default settings for this generator if 
            <type>_specific_settings is not provided in the main config.
            """
            return {"default_custom_param": "value", "my_required_docx_param": "default_val"}

    ```

2.  **Registration/Discovery:**
    *   **Entry Points:** The preferred method. Plugins will register themselves using Python package entry points (e.g., in their `pyproject.toml` or `setup.py`) under a specific group like `synth_data_gen.generators`. The main package will use `importlib.metadata` to discover these.
      ```toml
      # In plugin's pyproject.toml
      [project.entry-points."synth_data_gen.generators"]
      custom_docx = "my_plugin_package.generators:MyCustomDocxGenerator"
      ```
    *   **Environment Variable:** Alternatively, an environment variable (e.g., `SYNTH_DATA_GEN_PLUGIN_DIRS`) could point to directories containing plugin modules. The `PluginManager` would scan these.

3.  **Helper Utilities/Context:**
    *   `BaseGenerator` will provide access to a shared logging instance.
    *   A utility for constructing filenames based on patterns.
    *   Access to common content generation utilities (e.g., lorem ipsum generator, random data utilities, philosophical text snippet provider if implemented).
    *   The `common_vars` dict passed to `generate` will include pre-processed values like a unique ID, a slugified title for the document, current timestamp, etc., which can be used in filename patterns or content.

### 4.2. Defining New Output Formats/Variations

This is largely covered by creating a new generator. If it's a variation of an *existing* format (e.g., "EPUB_scientific_article_style"), it would still be a new generator class inheriting from `BaseGenerator` (or potentially `EpubGenerator` if deep inheritance makes sense and provides useful base functionality). Its unique `GENERATOR_ID` would be used in the configuration.

### 4.3. Custom Styling and Content Parameters for Extensions

These are managed through the configuration system:
*   When a custom generator `MyCustomDocxGenerator` with `GENERATOR_ID = "custom_docx"` is registered, the main configuration can include a `custom_docx_settings: { ... }` block.
*   The `MyCustomDocxGenerator.validate_config()` method is responsible for validating this block.
*   The `MyCustomDocxGenerator.generate()` method receives this `specific_config` dictionary to control its behavior.

## 5. Default Data Set & "Out-of-the-Box" Behavior

If `generate_data()` is called with no `config_path` and no `config_obj`, it will produce a default set of files in `./synthetic_output/default_set/`.
The default configuration prioritizes **deterministic counts** for core elements to ensure testability and predictable baseline output.

The default configuration will be hardcoded within the package and will be equivalent to the following conceptual YAML:

```yaml
# Conceptual Default Configuration (internal to the package)
# Prioritizes deterministic counts for testability.
output_directory_base: "synthetic_output" 

global_settings:
  default_author: "Synth Default Author"
  default_language: "en"
  default_publisher: "Default Press"
  base_seed: 12345 # Ensure reproducibility for default set

file_types:
  - type: "epub"
    count: 1
    output_subdir: "default_set/epubs"
    filename_pattern: "default_epub_deterministic_{index}.epub"
    epub_specific_settings:
      chapters_config: 3 
      sections_per_chapter_config: 2 
      toc_settings: { style: "navdoc_full", max_depth: 2 } 
      notes_system: { 
          type: "footnotes_same_page", 
          notes_config: 5, # Exactly 5 notes
          reference_style: "linked_superscript_number" 
      }
      multimedia: { 
          include_images: True, 
          images_config: 2, # Exactly 2 images
          image_usage_profile: "placeholder_images" 
      }
      content_elements:
        heading_styles: { chapter_title_style: "standard_h_tags", section_header_style: "standard_h_tags" }
        table_styles: { 
            tables_occurrence_config: 1, 
            table_rows_config: 4,
            table_cols_config: 3
        }
        code_block_styles: { 
            code_blocks_occurrence_config: 1
        }
      epub_version: 3

  - type: "pdf"
    count: 1
    output_subdir: "default_set/pdfs"
    filename_pattern: "default_pdf_deterministic_{index}.pdf"
    pdf_specific_settings:
      generation_method: "from_html" 
      page_count_config: 10 
      layout: { columns: 1 }
      base_font_family: "Liberation Serif" 
      visual_toc: { enable: True, style: "hyperlinked_text", max_depth: 2 }
      running_header: { enable: True, right_content: "Page {page_number}" }
      table_generation: { 
          pdf_tables_occurrence_config: 1
      }

  - type: "markdown"
    count: 1 
    output_subdir: "default_set/markdown"
    filename_pattern: "default_md_deterministic_{index}.md"
    markdown_specific_settings:
      headings_config: 5 
      max_heading_depth: 3
      include_lists: True
      md_list_items_config: 4, 
      include_code_blocks: True
      md_code_blocks_config: 1, 
      gfm_features:
        md_tables_occurrence_config: 1 
        md_table_rows_config: 3,
        md_table_cols_config: 2,
        md_footnotes_occurrence_config: 3 
      frontmatter:
        include_chance: 1.0 # Keep as 1.0 for default, as frontmatter is common
        style: "yaml"
        fields: { title: True, author: True, date: "2025-01-01", tags: ["default", "deterministic_example"] }
```

**Characteristics of Default Files (Revised for Determinism):**

*   **One EPUB 3:**
    *   3 chapters, each with 2 sections.
    *   EPUB3 Navigation Document with ToC (2 levels), landmarks, and page list.
    *   Exactly 5 same-page footnotes (linked superscript numbers).
    *   Exactly 2 placeholder images.
    *   Exactly 1 table and 1 code block.
    *   Standard H1/H2 for chapter/section titles.
    *   Content: Lorem ipsum mixed with some philosophical keywords.
*   **One PDF:**
    *   10 pages, single column.
    *   Generated from an intermediate HTML representation.
    *   Basic font (e.g., Liberation Serif).
    *   Hyperlinked visual Table of Contents (2 levels).
    *   Running header with page numbers.
    *   Exactly 1 table.
    *   Content: Lorem ipsum.
*   **One Markdown File:**
    *   5 headings (up to H3).
    *   Mix of ordered and unordered lists, each with 4 items.
    *   Exactly 1 GFM table (3 rows, 2 cols).
    *   Exactly 3 GFM footnotes.
    *   Exactly 1 fenced code block (with language specifier).
    *   YAML front matter (title, author, fixed date, tags).
    *   Content: Lorem ipsum with structural elements.

## 6. EPUB Generation Flexibility (Crucial Detail)

The `epub_specific_settings` schema provides the foundation for combinatorial complexity and generalization from the examples in [`docs/epub_formatting_analysis_report.md`](docs/epub_formatting_analysis_report.md). The goal is to allow users to configure the generation of EPUBs that can match any example feature or combine them in novel ways by using the "Unified Quantity Specification" for relevant parameters. **Using an exact integer for `_config` parameters is the primary way to achieve deterministic output for testing.**

Below, each feature area is detailed, referencing how it's configured via `epub_specific_settings` keys. Textual descriptions should be understood in light of parameters like `chapters_config`, `notes_config`, `images_config`, etc., now controlling quantities.

### 6.1. Table of Contents (ToC)
*   **Configuration:** `toc_settings` object.
    *   `toc_settings.style`: (string) Controls the primary ToC type.
        *   `"ncx_simple"`: Flat NCX.
        *   `"ncx_deeply_nested"`: NCX with `toc_settings.max_depth` levels.
        *   `"ncx_with_anchors"`: NCX `navPoint/content@src` will include `#anchor_id`.
        *   `"ncx_with_pagelist"`: NCX includes a `<pageList>` if `toc_settings.include_page_list_in_toc` is true.
        *   `"html_basic_list"`: Generates a separate HTML ToC file using `<ul>/<ol>`.
        *   `"html_styled_paragraphs"`: HTML ToC using `<p class="toc_level_X">`.
        *   `"navdoc_basic"`: EPUB3 NavDoc with `epub:type="toc"`.
        *   `"navdoc_full"`: EPUB3 NavDoc with `toc`, `landmarks` (if `toc_settings.include_landmarks` is true), and `page-list` (if `toc_settings.include_page_list_in_toc` is true).
        *   `"none"`: No ToC.
    *   `toc_settings.max_depth`: (integer) Controls nesting depth for NCX and HTML ToCs.
    *   `toc_settings.include_landmarks`: (boolean) For `navdoc_full`.
    *   `toc_settings.include_page_list_in_toc`: (boolean) For NCX `pageList` or NavDoc `page-list`.
    *   `toc_settings.ncx_problematic_label_chance`: (float) Chance for an NCX `navLabel` to contain a long text excerpt instead of a title (Adorno example).
    *   `toc_settings.ncx_list_footnote_files_chance`: (float) Chance for NCX to list individual footnote files (Derrida - Of Grammatology example). This would interact with `notes_system.type = "endnotes_granular_files"`.
*   **Combinations:**
    *   An EPUB2 can have an NCX (`include_ncx: "yes"`) and an HTML ToC (if `toc_settings.style` is `html_basic_list` or `html_styled_paragraphs`, and an HTML ToC file is generated and referenced in OPF guide).
    *   An EPUB3 typically has a NavDoc (`include_nav_doc: "yes"`, `toc_settings.style` one of `navdoc_*`). It can *also* have an NCX for backward compatibility (`include_ncx: "yes"`).
    *   The content of the ToC (which chapters/sections are included) is derived from the generated document structure (controlled by `chapters_config`, `sections_per_chapter_config`, up to `max_depth`).

### 6.2. Page Numbering
*   **Configuration:** `page_numbering` object.
    *   `page_numbering.style`: (string)
        *   `"epub3_semantic"`: Uses `<span aria-label="X" epub:type="pagebreak" id="Page_X" role="doc-pagebreak"/>` (Heidegger - Metaphysics, Sartre). Or `<span epub:type="pagebreak" id="pgX" title="X"/>` within `<a>` (Jameson). The exact semantic markup can be a sub-option or chosen based on `epub_version`.
        *   `"anchor_based"`: Uses `<a id="page_XXX"></a>` with optional classes (Kant, Taylor, Marcuse, etc.).
        *   `"text_embedded"`: Inserts plain text page numbers into content flow (Deleuze style). Configure with `text_page_number_format`, `text_page_number_prefix`, `text_page_number_suffix`.
        *   `"none"`: No explicit page markers.
    *   `page_numbering.link_to_page_markers`: (boolean) If true, and if a `pageList` (NCX) or `page-list` (NavDoc) is generated, its entries will link to these markers.
*   **Edition Markers (Kant style `[A 19/B 33]`):**
    *   Configured via `content_elements.heading_styles` or a new specific section like `edition_markers: { enable: true, style: "kant_ab", chance_per_header: 0.2 }`. These would be injected as text near/in headers.
*   **Page/Section Markers in Text/Headers (Hegel - Science of Logic `21.27`):**
    *   Configured via `content_elements.heading_styles` (to embed in headers) or a new `inline_section_markers: { enable: true, format: "decimal_dot", chance_per_paragraph: 0.05 }`.

### 6.3. Headers/Footers (Visual Running Heads - Simulated for EPUB)
*   **Configuration:** `content_headers`, `content_footers` objects.
    *   As EPUBs are reflowable, true running headers/footers are not standard in XHTML content. This configuration can simulate them by:
        *   Styling the first `<h1>` of each chapter file to appear like a running head.
        *   If `generation_method` for PDF is `from_html`, these settings could inform the PDF's running headers/footers.
    *   `enable`: (boolean)
    *   `text_left`, `text_center`, `text_right`: (string) with placeholders like `{book_title}`, `{chapter_title}`, `{current_section_title}` (if available), `{page_number_placeholder}` (visual only, not linked to EPUB pagination).
    *   `font_style`: (object) `{ family, size, color }`.
*   **Note:** This is distinct from HTML `<header>` and `<footer>` structural elements.

### 6.4. Citations/Footnotes/Endnotes
*   **Configuration:** `notes_system` object and `citations_bibliography.in_text_citation_style`. The number of notes is controlled by `notes_config` and `secondary_notes_config`.
    *   `notes_system.type`: (string) Defines the primary note system.
        *   `"footnotes_same_page"`: Notes at bottom of current XHTML.
        *   `"endnotes_chapter"`: Notes at end of current chapter's XHTML (Zizek style).
        *   `"endnotes_book"`: All notes in one separate `notes.xhtml`.
        *   `"endnotes_granular_files"`: Each note in its own file (Derrida - Grammatology symbol notes).
        *   `"dual_system_kant"`: Combines `footnotes_same_page` (for author) and `endnotes_book` (for editorial, using `secondary_note_type` and `secondary_note_marker_style`).
        *   `"dual_system_hegel_por"`: Combines `footnotes_same_page` (symbol markers) and `endnotes_book` (numbered markers).
        *   `"dual_system_derrida_grammatology"`: Combines `endnotes_granular_files` (symbol) and `endnotes_book` (numbered).
        *   `"none"`: No notes.
    *   `notes_system.reference_style.style`: (string) Defines how `<a>` or text markers appear.
        *   `"linked_superscript_number"` (default)
        *   `"linked_superscript_symbol"` (uses `reference_style.symbols`)
        *   `"unlinked_superscript_number"` (Adorno, Baudrillard, Derrida - Gift of Death)
        *   `"unlinked_bracketed_number"` (Hardt & Negri)
        *   Specific complex styles like `"complex_kant_style"`, `"complex_hegel_sol_style"`, etc., will map to the detailed HTML structures from the report.
    *   `notes_system.note_text_structure.style`: (string) Defines HTML for the note body.
        *   `"simple_paragraph"`
        *   `"paragraph_with_backlink"` (default)
        *   Specific complex styles like `"div_blockquote_hegel_sol"`, `"section_list_epub3"`, etc.
    *   `citations_bibliography.in_text_citation_style`: (string) For non-note citations.
        *   `"parenthetical_kant_style"`: `(EX, p. 15; 23:21)`
        *   `"plain_text_taylor_style"`: `See Kant’s <em>Critique...</em>, A70/B95.`
        *   `"biblioref_rosenzweig_style"`: `<a epub:type="biblioref"...>`
*   **Combinations:**
    *   A user can select `notes_system.type = "endnotes_book"` and `notes_system.reference_style.style = "unlinked_superscript_number"` to simulate Adorno.
    *   For Derrida's Of Grammatology, one would configure a primary `notes_system` (e.g., `type="endnotes_granular_files"`, `reference_style.style="linked_superscript_symbol"`) and a `secondary_note_system` (e.g., `type="endnotes_book"`, `reference_style.style="linked_superscript_number"`). The quantity of each type of note is controlled by `notes_config` and `secondary_notes_config` respectively (e.g., `notes_config: 50`, `secondary_notes_config: 20`).
    *   The content of notes can include citations by enabling a chance for bibliographic entries to be formatted within the note text.

### 6.5. Bibliography
*   **Configuration:** `citations_bibliography.bibliography_style` object.
    *   `style`: (string)
        *   `"dedicated_file_list"`: Standard bibliography in its own XHTML.
        *   `"section_in_content_file"`: Bibliography as a section within another file (e.g., foreword).
        *   `"rosenzweig_biblio_semantic"`: Uses `<section epub:type="bibliography">` with `<li epub:type="biblioentry">` and optional backlinks.
        *   `"none"`.
    *   `include_cite_tags`: (boolean) Whether to wrap titles in `<cite>`.
    *   `biblio_entry_backlink_chance`: (float) Chance for an entry to have an `epub:type="backlink"` if `in_text_citation_style` is `biblioref_rosenzweig_style`.

### 6.6. Multimedia (Images, Fonts)
*   **Configuration:** `multimedia` object and `font_embedding` object. Number of images controlled by `images_config`.
    *   `multimedia.include_images`: (boolean)
    *   `multimedia.image_types`: (list) e.g., `["jpeg", "png", "gif", "unknown_octet_stream"]`. The "unknown_octet_stream" would simulate Kant's example.
    *   `multimedia.image_usage_profile`: (string)
        *   `"placeholder_images"`: Generic placeholders.
        *   `"images_as_text_hegel_sol"`: Small images representing special text/symbols.
        *   `"full_page_images_rosenzweig_star"`: Images taking up a full page area.
        *   `"ornamental_images_jameson"`: Decorative images used as separators.
    *   `multimedia.image_caption_style`: (string) `none`, `below_image_paragraph`, etc.
    *   `font_embedding.enable`: (boolean)
    *   `font_embedding.fonts`: (list) List of font family names to attempt to embed.
    *   `font_embedding.obfuscation`: (string) `none`, `adobe`, `idpf`. If not `none`, `META-INF/encryption.xml` will be generated.
*   **Combinations:** Can have embedded fonts with or without obfuscation, and various types/usages of images, with quantities determined by `images_config`.

### 6.7. Content Types (Paragraphs, Headings, Lists, Tables, etc.)
*   **Configuration:** `content_elements` object. Quantities of tables, code blocks, poetry sections are controlled by their respective `*_occurrence_config` parameters. Number of list items is controlled by `list_items_config`.
    *   `paragraph_styles`: (list of objects) Each object defines a paragraph style with `class_name`, `chance`, and optional `wrapper_div_class` / `inner_span` (for Heidegger - German Existentialism style).
    *   `heading_styles.chapter_title_style`, `heading_styles.section_header_style`: (string)
        *   `"standard_h_tags"`: Uses `<h1>` for chapters, `<h2>` for sections, etc.
        *   `"styled_p_tags_byung_chul_han"`: `<p class="c9"><strong>TITLE</strong></p>`
        *   `"styled_p_tags_derrida_specters"`: `<p class="chapter-number_1"><a><b>1</b></a></p> <p class="chapter-title_2"><a><b>TITLE</b></a></p>`
        *   `"styled_div_tags_kaplan"`: `<div class="chapter-number">ONE</div> <div class="chapter-title">TITLE</div>`
        *   `"combined_h_tag_hegel_metaphysics"`: `<h1><span class="chapterNumber">N</span><span class="chapterTitle">Title</span></h1>`
        *   `"combined_h_tag_foucault_arch"`: `<h1 class="paracenter">N<br/>___<br/>TITLE</h1>`
        *   `"separate_p_tags_rorty"`: `<p class="chno">CHAPTER N</p> <p class="chtitle">TITLE</p>`
        *   A `class_map` can be provided for more granular class control per heading level if using styled p/divs.
    *   `blockquote_styles.style`: (string) `standard_blockquote`, `styled_div_hegel_sol`.
    *   `list_styles`: Controls ordered/unordered lists, nesting depth, marker styles, and number of items via `list_items_config`.
    *   `table_styles`: Controls inclusion (via `tables_occurrence_config`), size (via `table_rows_config`, `table_cols_config`), content, and captioning of tables.
    *   `code_block_styles`: Controls inclusion (via `code_blocks_occurrence_config`) and formatting of code blocks.
    *   `poetry_formatting.style`: (string) `style_hegel_por`, `style_marx_engels_p_class`. Occurrence controlled by `poetry_occurrence_config`.
*   **Combinations:** A document can have standard H1 chapter titles but use styled `<p>` tags for H2/H3 sections. Paragraphs can vary between indented and non-indented.

### 6.8. Structural Elements (Front/Back Matter, Splits, Segments)
*   **Configuration:** `structural_elements` object.
    *   `include_front_matter`, `include_back_matter`: (boolean)
    *   `include_calibre_metadata_files`, `include_sigil_metadata_files`, `include_adobe_xpgt_adept_tags`: (string: "none", "random", "yes") To simulate publisher/converter artifacts.
    *   `split_content_files_chance`: (float) Chance to split main content XHTML files (e.g., `_split_YYY.html`).
    *   `segment_chapter_files_chance`: (float) Chance to segment chapters into `chapterX.html`, `chapterXa.html` (for notes), `chapterXb.html` (Heidegger Ponderings, Gadamer style).
*   **Combinations:** An EPUB3 could have a NavDoc, include Adobe Adept tags, and have its main content files split.

### 6.9. Font & Typography
*   **Configuration:** `typography_layout` object and `font_embedding` (covered in Multimedia).
    *   `base_font_family`, `heading_font_family`: (list of strings) CSS font stack.
    *   `element_fonts`: (list of objects) Allows specifying font family, size, weight, color for specific CSS selectors, enabling fine-grained control (e.g., making all `<em>` tags use a specific serif font).
    *   `margins_cm`, `line_spacing_multiplier`, `text_alignment`: General layout CSS.
*   **Combinations:** Can specify default fonts, then override for specific elements, and choose whether to embed these fonts.

### 6.10. Layout (Margins, Line Spacing, Alignment)
*   **Configuration:** `typography_layout` object.
    *   `margins_cm`: (float or object `{top, bottom, left, right}`)
    *   `line_spacing_multiplier`: (float)
    *   `text_alignment`: (string) `left`, `right`, `center`, `justify`.
*   These settings will primarily influence the generated CSS.

### 6.11. Simulating Report Examples
*   **Kant (Critique):**
    *   `epub_version: 2`
    *   `toc_settings: { style: "ncx_deeply_nested", ncx_problematic_label_chance: 0.0 }`
    *   `notes_system: { type: "dual_system_kant", notes_config: 50, secondary_notes_config: 15, reference_style: { style: "complex_kant_style" }, note_text_structure: { style: "simple_paragraph" } }`
    *   `page_numbering: { style: "anchor_based" }`
    *   `multimedia: { images_config: 0, image_types: ["unknown_octet_stream"], image_usage_profile: "images_as_text_hegel_sol" }`
    *   `structural_elements: { include_calibre_metadata_files: "yes", split_content_files_chance: 1.0 }`
    *   `content_elements: { heading_styles: { chapter_title_style: "standard_h_tags" } }`
*   **Derrida (Of Grammatology):**
    *   `epub_version: 2`
    *   `toc_settings: { style: "ncx_deeply_nested", ncx_list_footnote_files_chance: 1.0 }`
    *   `notes_system: { type: "dual_system_derrida_grammatology", notes_config: 75, secondary_notes_config: 30, reference_style: { style: "linked_superscript_symbol", symbols: ["*","†","§","||"] }, secondary_note_reference_style: { style: "linked_superscript_number"} }`
    *   `font_embedding: { enable: True, fonts: ["Charis SIL"] }`
*   **Adorno (Negative Dialectics):**
    *   `epub_version: 2`
    *   `toc_settings: { style: "ncx_deeply_nested", ncx_problematic_label_chance: 1.0 }`
    *   `notes_system: { type: "endnotes_book", notes_config: 45, reference_style: { style: "unlinked_superscript_number" } }`
    *   `edge_cases: { unusual_css_class_usage_chance: 1.0 }`
    *   `structural_elements: { split_content_files_chance: 1.0 }`
*   **General Approach:** By combining settings from `epub_specific_settings`, users can target specific features. The `*_config` parameters allow for precise (integer), ranged, or flexible (probabilistic) control over quantities. For testing, exact integers are preferred.

This detailed specification for `epub_specific_settings` allows for the generation of EPUBs that can match the complexity of the analyzed reports and create a vast array of new synthetic test cases.
The other file types (`pdf_specific_settings`, `markdown_specific_settings`) provide similar, albeit less complex, levels of control tailored to their respective formats, now also utilizing the "Unified Quantity Specification" with an emphasis on deterministic defaults.

## 7. Memory Bank Updates (Pre-completion)

This revised specification document will be updated in the Memory Bank.

*   **`memory-bank/activeContext.md`**:
    *   `[YYYY-MM-DD HH:MM:SS] - SpecPseudo - Action - Further revised Synthetic Data Package Specification to prioritize deterministic defaults for Unified Quantity Specification, per user feedback.`
*   **`memory-bank/globalContext.md`**:
    *   (No changes anticipated here beyond what was already logged for the pattern itself.)
*   **`memory-bank/mode-specific/spec-pseudocode.md`**:
    *   Under `## Functional Requirements` for "Synthetic Data Package Generation": Status reflects the latest revision.

(Actual update will use `insert_content` or `apply_diff` after user confirmation of this step).