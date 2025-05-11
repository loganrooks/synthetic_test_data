# synth_data_gen/__init__.py
import os
from .common.utils import ensure_output_directories
from .generators.epub_components import toc as epub_toc_generators
from .generators.epub_components import headers as epub_header_generators
from .generators.epub_components import notes as epub_note_generators
from .generators.epub_components import citations as epub_citation_generators
from .generators.epub_components import page_numbers as epub_page_number_generators
from .generators.epub_components import multimedia as epub_multimedia_generators
from .generators.epub_components import structure as epub_structure_generators
from .generators.epub_components import content_types as epub_content_type_generators
from .generators import pdf as pdf_generators # Renamed to avoid conflict
from .generators import markdown as markdown_generators # Renamed to avoid conflict

def generate_data(config_path: str = None, config_obj: dict = None, output_dir: str = "synthetic_output") -> list[str]:
    """
    Generates synthetic data files based on the provided configuration.

    Either 'config_path' (path to a YAML/JSON configuration file) or 
    'config_obj' (a Python dictionary representing the configuration) must be provided.
    If both are provided, 'config_obj' takes precedence.
    If neither is provided, default data generation will occur (as currently implemented).

    Args:
        config_path (str, optional): Path to the YAML or JSON configuration file. 
                                     Defaults to None.
        config_obj (dict, optional): A Python dictionary representing the configuration.
                                     Defaults to None.
        output_dir (str, optional): The root directory where generated files will be saved.
                                    Defaults to "synthetic_output". This is currently
                                    overridden by the common.utils.ensure_output_directories logic.

    Returns:
        list[str]: A list of paths to the generated files (currently not implemented, returns placeholder).

    Raises:
        ValueError: If both config_path and config_obj are None and no default 
                    configuration is set up for "out-of-the-box" behavior.
        FileNotFoundError: If config_path is provided but the file does not exist.
        InvalidConfigError: If the configuration (from file or object) is invalid 
                            (e.g., missing required fields, incorrect data types).
        GeneratorError: If an error occurs within a specific data generator.
    """
    print(f"Starting synthetic data generation (config_path='{config_path}', config_obj provided: {config_obj is not None}, output_dir='{output_dir}')...")
    
    # Ensure all output directories exist (uses paths defined in common.utils)
    ensure_output_directories()

    # EPUBs - TOC
    epub_toc_generators.create_epub_ncx_simple()
    epub_toc_generators.create_epub_ncx_nested()
    epub_toc_generators.create_epub_html_toc_linked()
    epub_toc_generators.create_epub_ncx_with_pagelist()
    epub_toc_generators.create_epub_missing_ncx()
    epub_toc_generators.create_epub_navdoc_full()
    epub_toc_generators.create_epub_ncx_links_to_anchors()
    epub_toc_generators.create_epub_ncx_problematic_entries()
    epub_toc_generators.create_epub_ncx_inconsistent_depth()
    epub_toc_generators.create_epub_ncx_lists_footnote_files()
    epub_toc_generators.create_epub_html_toc_p_tags()
    epub_toc_generators.create_epub_html_toc_non_linked()

    # EPUBs - Headers
    epub_header_generators.create_epub_p_tag_headers()
    epub_header_generators.create_epub_headers_with_edition_markers()
    epub_header_generators.create_epub_taylor_hegel_headers()
    epub_header_generators.create_epub_sennet_style_headers()
    epub_header_generators.create_epub_div_style_headers()
    epub_header_generators.create_epub_header_mixed_content()
    epub_header_generators.create_epub_header_rosenzweig_hegel()
    epub_header_generators.create_epub_header_derrida_gift_death()
    epub_header_generators.create_epub_header_bch_p_strong()
    epub_header_generators.create_epub_header_derrida_specters_p()
    epub_header_generators.create_epub_header_kaplan_div()
    epub_header_generators.create_epub_header_descartes_dict_p()
    epub_header_generators.create_epub_header_foucault_style()

    # EPUBs - Notes
    epub_note_generators.create_epub_same_page_footnotes()
    epub_note_generators.create_epub_endnotes_separate_file()
    epub_note_generators.create_epub_kant_style_footnotes()
    epub_note_generators.create_epub_hegel_sol_style_footnotes()
    epub_note_generators.create_epub_dual_note_system()
    epub_note_generators.create_epub_pippin_style_endnotes()
    epub_note_generators.create_epub_heidegger_ge_style_endnotes()
    epub_note_generators.create_epub_heidegger_metaphysics_style_footnotes()
    epub_note_generators.create_epub_footnote_hegel_sol_ref()
    epub_note_generators.create_epub_footnote_hegel_por_author()
    epub_note_generators.create_epub_footnote_marx_engels_reader()
    epub_note_generators.create_epub_footnote_marcuse_dual_style()
    epub_note_generators.create_epub_footnote_adorno_unlinked()
    epub_note_generators.create_epub_footnote_derrida_grammatology_dual()

    # EPUBs - Citations & Bibliography
    epub_citation_generators.create_epub_citation_kant_intext()
    epub_citation_generators.create_epub_citation_taylor_intext_italic()
    epub_citation_generators.create_epub_citation_rosenzweig_biblioref()

    # EPUBs - Page Numbers & Edition Markers
    epub_page_number_generators.create_epub_pagenum_semantic_pagebreak()
    epub_page_number_generators.create_epub_pagenum_kant_anchor()
    epub_page_number_generators.create_epub_pagenum_taylor_anchor()
    epub_page_number_generators.create_epub_pagenum_deleuze_plain_text()
    
    # EPUBs - Images & Fonts
    epub_multimedia_generators.create_epub_image_as_special_text()
    epub_multimedia_generators.create_epub_font_obfuscated()

    # EPUBs - Structure & Metadata
    epub_structure_generators.create_epub_minimal_metadata()
    epub_structure_generators.create_epub2_with_guide()
    epub_structure_generators.create_epub_opf_specific_meta()
    epub_structure_generators.create_epub_spine_pagemap_ref()
    epub_structure_generators.create_epub_structure_split_files()
    epub_structure_generators.create_epub_structure_calibre_artifacts()
    epub_structure_generators.create_epub_structure_adobe_artifacts()
    epub_structure_generators.create_epub_accessibility_epub_type()
    
    # EPUBs - Content Types & Misc
    epub_content_type_generators.create_epub_poetry()
    epub_content_type_generators.create_epub_content_dialogue()
    epub_content_type_generators.create_epub_content_epigraph()
    epub_content_type_generators.create_epub_content_blockquote_styled()
    epub_content_type_generators.create_epub_content_internal_cross_refs()
    epub_content_type_generators.create_epub_content_forced_page_breaks()

    # PDFs
    pdf_generators.create_pdf_text_single_column()
    pdf_generators.create_pdf_text_multi_column()
    pdf_generators.create_pdf_text_flow_around_image()
    pdf_generators.create_pdf_simulated_ocr_high_quality()
    pdf_generators.create_pdf_with_bookmarks()
    pdf_generators.create_pdf_visual_toc_hyperlinked()
    pdf_generators.create_pdf_running_headers_footers()
    pdf_generators.create_pdf_bottom_page_footnotes()
    pdf_generators.create_pdf_simple_table()

    # Markdown
    markdown_generators.create_md_basic_elements()
    markdown_generators.create_md_extended_elements()
    markdown_generators.create_md_json_frontmatter()
    markdown_generators.create_md_error_frontmatter()
    markdown_generators.create_md_no_frontmatter()
    markdown_generators.create_md_with_embedded_html()
    markdown_generators.create_md_with_latex()
    
    print("Synthetic data generation script finished.")
    # Actual paths of generated files are not tracked by these low-level functions yet.
    # This will need to be implemented when the generators are refactored.
    return [] # Placeholder return

__all__ = ['generate_data']