from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter # Add import
from reportlab.lib.units import inch # Add import
import pytest
import os
import shutil # Added for tearDown equivalent
from pytest_mock import MockerFixture
from unittest.mock import call, MagicMock, patch # Keep call and MagicMock, ensure patch is imported
import inspect # For debugging module loading
from synth_data_gen.generators.pdf import PdfGenerator
from synth_data_gen.core.base import BaseGenerator
from typing import Dict, Any, cast
import random # For patching random.randint and random.random
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate # For ToC and integration tests
import re # Add import for regular expressions

@pytest.fixture
def pdf_generator_instance():
    global_config = {"test": "global"}
    specific_config = {"test": "specific"}
    return PdfGenerator(global_config, specific_config)

@pytest.fixture(autouse=True) # Apply to all tests in this module
def cleanup_pdf_test_output():
    # This fixture will run after each test in this file
    yield
    # General cleanup for this test file
    if os.path.exists("test_output"): 
        shutil.rmtree("test_output")
    # Specific cleanup for a directory created by one of the tests
    if os.path.exists("test_output_pdf_range_chapters_global"): 
        shutil.rmtree("test_output_pdf_range_chapters_global")


def test_get_default_specific_config(pdf_generator_instance: PdfGenerator):
    """Test that get_default_specific_config for PDF returns the expected structure."""
    defaults = pdf_generator_instance.get_default_specific_config()
    
    assert isinstance(defaults, dict)
    assert "generation_method" in defaults
    assert defaults["generation_method"] == "from_html"
    assert "page_count_config" in defaults
    assert defaults["page_count_config"] == 10
    assert "author" in defaults
    assert defaults["author"] == "Default PDF Author"
    assert "title" in defaults
    assert defaults["title"] == "Synthetic PDF Document"
    assert "pdf_variant" in defaults 
    assert defaults["pdf_variant"] == "single_column_text"

    assert "layout" in defaults
    assert isinstance(defaults["layout"], dict)
    assert "columns" in defaults["layout"]
    assert defaults["layout"]["columns"] == 1
    assert "margins_mm" in defaults["layout"]
    assert isinstance(defaults["layout"]["margins_mm"], dict)
    assert defaults["layout"]["margins_mm"]["top"] == 20

    assert "running_header" in defaults
    assert isinstance(defaults["running_header"], dict)
    assert defaults["running_header"]["enable"]
    assert defaults["running_header"]["right_content"] == "Page {page_number}"

def test_validate_config_valid(pdf_generator_instance: PdfGenerator):
    """Test validate_config with valid specific and global configs for PDF."""
    specific_config = pdf_generator_instance.get_default_specific_config()
    global_config = {"default_language": "en"}
    assert pdf_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_missing_pdf_variant(pdf_generator_instance: PdfGenerator):
    """Test validate_config when pdf_variant is missing (should still pass due to current implementation)."""
    specific_config = pdf_generator_instance.get_default_specific_config()
    del specific_config["pdf_variant"]
    global_config = {"default_language": "en"}
    assert pdf_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_invalid_base_specific_config(pdf_generator_instance: PdfGenerator):
    """Test validate_config when the specific_config is not a dict (handled by super)."""
    specific_config = cast(Dict[str, Any], "not_a_dict")  # Intentionally invalid for testing
    global_config = {"default_language": "en"}
    assert not pdf_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_invalid_base_global_config(pdf_generator_instance: PdfGenerator):
    """Test validate_config when the global_config is not a dict (handled by super)."""
    specific_config = pdf_generator_instance.get_default_specific_config()
    global_config = cast(Dict[str, Any], "not_a_dict")  # Intentionally invalid for testing
    assert not pdf_generator_instance.validate_config(specific_config, global_config)

def test_generate_minimal_pdf_single_column(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test the basic flow of the generate method for a minimal single-column PDF."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_single_column = mocker.patch.object(pdf_generator_instance, '_create_pdf_text_single_column')
    
    specific_config = {
        "title": "Test PDF", "author": "Test PDF Author", "pdf_variant": "single_column_text"
    }
    global_config = {"default_author": "Global PDF Author"}
    output_path = "test_output/minimal.pdf"
    expected_dir_to_ensure = "test_output"

    returned_path = pdf_generator_instance.generate(specific_config, global_config, output_path)

    mock_ensure_output_dirs.assert_called_once_with(expected_dir_to_ensure)
    mock_create_single_column.assert_called_once_with(output_path, specific_config, global_config)
    assert returned_path == output_path

def test_generate_minimal_pdf_multi_column(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test routing to a different PDF variant."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_multi_column = mocker.patch.object(pdf_generator_instance, '_create_pdf_text_multi_column')
    
    specific_config = {"title": "Multi Column Test", "pdf_variant": "multi_column_text"}
    global_config = {}
    output_path = "test_output/multi.pdf"
    
    pdf_generator_instance.generate(specific_config, global_config, output_path)
    
    mock_create_multi_column.assert_called_once_with(output_path, specific_config, global_config)

def test_generate_unknown_variant_falls_back_to_single_column(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test that an unknown pdf_variant falls back to single_column_text."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_single_column = mocker.patch.object(pdf_generator_instance, '_create_pdf_text_single_column')
    
    specific_config = {"title": "Unknown Variant Test", "pdf_variant": "this_variant_does_not_exist"}
    global_config = {}
    output_path = "test_output/unknown_variant.pdf"
    
    mock_print = mocker.patch('builtins.print')
    pdf_generator_instance.generate(specific_config, global_config, output_path)
    mock_print.assert_any_call("Warning: Unknown PDF variant 'this_variant_does_not_exist'. Generating single_column_text instead.")

    mock_create_single_column.assert_called_once_with(output_path, specific_config, global_config)

def test_generate_single_column_unified_chapters_exact(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'chapters_config' (exact int) for 'single_column_text' variant."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_determine_count = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mock_add_pdf_chapter_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
    
    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    exact_chapter_count = 2
    mock_determine_count.side_effect = [10, exact_chapter_count, 0,0,0, 0,0,0]

    specific_config = {
        "title": "PDF Exact Chapters Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "chapters_config": exact_chapter_count, "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0}, "multimedia": {"include_images": False, "images_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_exact_chapters.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    assert call(exact_chapter_count, "chapters") in mock_determine_count.call_args_list
    assert mock_add_pdf_chapter_content.call_count == exact_chapter_count
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()

def test_generate_single_column_unified_chapters_range(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'chapters_config' (range object) for 'single_column_text' variant,
    ensuring BaseGenerator._determine_count uses the patched random.randint."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_chapter_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    chapters_range_config = {"min": 2, "max": 5}
    expected_chapters_from_range = 3 
    mock_base_randint.return_value = expected_chapters_from_range

    specific_pdf_config = {
        "title": "Test PDF Range Chapters", "author": "Test Author Range Chapters", "variant": "single_column_text",
        "chapters_config": chapters_range_config, "sections_config": {"min": 0, "max": 0},
        "paragraphs_config": {"min": 1, "max": 1}, "sentences_config": {"min": 1, "max": 1},
        "words_config": {"min": 1, "max": 1}, "images_config": {"min": 0, "max": 0},
        "tables_config": {"min": 0, "max": 0}, "lists_config": {"min": 0, "max": 0},
        "code_blocks_config": {"min": 0, "max": 0}, "blockquotes_config": {"min": 0, "max": 0},
        "text_boxes_config": {"min": 0, "max": 0}, "diagrams_config": {"min": 0, "max": 0},
        "charts_config": {"min": 0, "max": 0}, "math_formulas_config": {"min": 0, "max": 0},
        "footnotes_config": {"min": 0, "max": 0}, "endnotes_config": {"min": 0, "max": 0},
        "index_terms_config": {"min": 0, "max": 0}, "glossary_terms_config": {"min": 0, "max": 0},
        "bibliography_entries_config": {"min": 0, "max": 0}, "appendices_config": {"min": 0, "max": 0},
        "cover_config": {"include_cover": False}, "toc_config": {"include_toc": False},
        "header_config": {"include_header": False}, "footer_config": {"include_footer": False},
        "page_numbering_config": {"include_page_numbers": False},
        "font_config": {"font_name": "Helvetica", "font_size_pt": 12, "line_spacing_pt": 14},
        "page_layout": {"page_width_mm": 210, "page_height_mm": 297, "left_margin_mm": 20, "right_margin_mm": 20, "top_margin_mm": 25, "bottom_margin_mm": 25},
    }
    global_generator_config = {
        "output_directory_base": "test_output_pdf_range_chapters_global",
        "output_filename_base": "test_doc_range_global",
        "document_template_class": "synth_data_gen.document_templates.SimpleDocTemplate",
        "random_seed": 42, "debug_mode": False,
        "file_types": {"pdf": specific_pdf_config}
    }
    output_dir = os.path.join(global_generator_config["output_directory_base"], pdf_generator_instance.GENERATOR_ID)
    output_filename = global_generator_config["output_filename_base"] + ".pdf"
    final_output_path = os.path.join(output_dir, output_filename)

    mock_ensure_output_dirs.return_value = None
    mock_base_randint.reset_mock()
    mock_add_pdf_chapter_content.reset_mock()

    pdf_generator_instance.generate(
        specific_config=specific_pdf_config,
        global_config=global_generator_config,
        output_path=final_output_path
    )

    mock_base_randint.assert_called_once_with(chapters_range_config["min"], chapters_range_config["max"])
    assert mock_add_pdf_chapter_content.call_count == expected_chapters_from_range
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()

def test_generate_single_column_unified_chapters_probabilistic(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'chapters_config' (probabilistic) for 'single_column_text'."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_chapter_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
    # mock_base_random will be patched using 'with patch'
    # mock_base_randint will be patched using 'with patch'
    
    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance

    chapters_prob_config = {"chance": 0.7, "if_true": {"min": 1, "max": 3}, "if_false": 0}
    
    specific_pdf_config = {
        "title": "Test PDF Probabilistic Chapters", "author": "Test Author Probabilistic",
        "pdf_variant": "single_column_text", "chapters_config": chapters_prob_config,
        "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14},
        "mixed_page_sizes_orientations_chance": 0.0 # Ensure no interference
    }
    global_generator_config = {"default_language": "en"}
    mocker.patch('synth_data_gen.generators.pdf.random.random', return_value=0.99) # Patch pdf.random

    # Scenario 1
    expected_chapters_scenario1 = 2
    output_path_s1 = "test_output/pdf_prob_chapters_s1.pdf"
    with patch('synth_data_gen.core.base.random.random', return_value=0.5) as mock_random_s1, \
         patch('synth_data_gen.core.base.random.randint', return_value=expected_chapters_scenario1) as mock_randint_s1:
        mock_simple_doc_template_class.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        mock_doc_instance.reset_mock()
        mock_add_pdf_chapter_content.reset_mock() # Reset for this scenario

        pdf_generator_instance.generate(specific_pdf_config, global_generator_config, output_path_s1)
        
        assert mock_random_s1.call_count >= 1 # Called for chapters_config, and potentially page_count_config if not mocked out
        # More precise: check it was called for chapters_config.
        # The current structure of _create_pdf_text_single_column calls _determine_count for page_count first.
        # Let's assume page_count_config is the default int (10), so it won't call random.
        # So, random.random should be called once for chapters_config.
        # If page_count_config was also probabilistic and not controlled, this assertion would be tricky.
        # Given specific_config doesn't set page_count_config, it defaults to 10 (int).
        assert mock_random_s1.call_count == 1 # Expect once for chapters_config
        mock_randint_s1.assert_called_once_with(chapters_prob_config["if_true"]["min"], chapters_prob_config["if_true"]["max"])
        assert mock_add_pdf_chapter_content.call_count == expected_chapters_scenario1

    # Scenario 2
    expected_chapters_scenario2 = 0 
    output_path_s2 = "test_output/pdf_prob_chapters_s2.pdf"
    with patch('synth_data_gen.core.base.random.random', return_value=0.8) as mock_random_s2, \
         patch('synth_data_gen.core.base.random.randint') as mock_randint_s2:
        mock_simple_doc_template_class.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        mock_doc_instance.reset_mock()
        mock_add_pdf_chapter_content.reset_mock() # Reset for this scenario

        pdf_generator_instance.generate(specific_pdf_config, global_generator_config, output_path_s2)
        
        assert mock_random_s2.call_count == 1 # Expect once for chapters_config
        mock_randint_s2.assert_not_called() 
        assert mock_add_pdf_chapter_content.call_count == expected_chapters_scenario2

def test_generate_single_column_page_count_exact(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'page_count_config' (exact int) for 'single_column_text' variant."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_determine_count = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') 
    
    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    exact_page_count = 5
    # Side effect: page_count, chapters, sections, notes, images, tables, figures
    mock_determine_count.side_effect = [exact_page_count, 1, 0,0,0, 0,0] # Adjusted for tables/figures

    specific_pdf_config = {
        "title": "PDF Exact Page Count Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": exact_page_count, "chapters_config": 1, 
        "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "table_generation": {"pdf_tables_occurrence_config": 0}, # Ensure these are 0 for the mock side_effect
        "figure_generation": {"pdf_figures_occurrence_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_exact_page_count.pdf"

    pdf_generator_instance.generate(specific_pdf_config, global_config, output_path)

    assert call(exact_page_count, "page_count") in mock_determine_count.call_args_list
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()

def test_generate_single_column_page_count_range(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'page_count_config' (range) for 'single_column_text' variant."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    
    original_determine_count = BaseGenerator._determine_count
    def side_effect_for_determine_count(config_val, context_key):
        # Allow page_count to use original logic (which will use mocked randint)
        if context_key == "page_count":
            return original_determine_count(pdf_generator_instance, config_val, context_key)
        # For other calls, return fixed values to isolate the test
        elif context_key == "chapters": return 1
        elif context_key.startswith("sections_chap_"): return 0
        elif context_key.startswith("notes_chap_"): return 0
        elif context_key.startswith("images_chap_"): return 0
        elif context_key == "pdf_tables_occurrence": return 0
        elif context_key == "pdf_figures": return 0
        return original_determine_count(pdf_generator_instance, config_val, context_key) # Fallback
    mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    page_count_range_config = {"min": 3, "max": 7}
    expected_page_count_from_range = 4 
    mock_base_randint.return_value = expected_page_count_from_range
        
    specific_pdf_config = {
        "title": "PDF Range Page Count Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": page_count_range_config, "chapters_config": 1, 
        "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "table_generation": {"pdf_tables_occurrence_config": 0}, 
        "figure_generation": {"pdf_figures_occurrence_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_range_page_count.pdf"

    pdf_generator_instance.generate(specific_pdf_config, global_config, output_path)

    mock_determine_count_on_pdf.assert_any_call(page_count_range_config, "page_count")
    mock_base_randint.assert_called_once_with(page_count_range_config["min"], page_count_range_config["max"])
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()

def test_generate_single_column_page_count_probabilistic(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'page_count_config' (probabilistic) for 'single_column_text'."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') # Mock to simplify content
    
    # Patch random used directly in pdf.py for mixed_page_sizes_orientations_chance
    mocker.patch('synth_data_gen.generators.pdf.random.random', return_value=0.99) # High value to avoid path

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance

    page_count_prob_config = {"chance": 0.6, "if_true": {"min": 2, "max": 4}, "if_false": 1}

    specific_pdf_config_base = {
        "title": "PDF Probabilistic Page Count Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": page_count_prob_config, 
        "chapters_config": 1, # Keep other counts simple and deterministic
        "sections_per_chapter_config": 0, 
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "table_generation": {"pdf_tables_occurrence_config": 0},
        "figure_generation": {"pdf_figures_occurrence_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14},
        "mixed_page_sizes_orientations_chance": 0.0 # Crucial: ensure this is 0.0
    }
    global_config = {"default_language": "en"}

    # Scenario 1: Chance met for page_count
    output_path_s1 = "test_output/pdf_prob_page_count_s1.pdf"
    with patch('synth_data_gen.core.base.random.random', return_value=0.4) as mock_core_random_s1, \
         patch('synth_data_gen.core.base.random.randint', return_value=3) as mock_core_randint_s1:
        
        mock_simple_doc_template_class.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        mock_doc_instance.reset_mock()

        pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s1)
    
        # _determine_count for page_count_config should call core.base.random.random once.
        # Other _determine_count calls (chapters, tables etc.) use integer configs, so no random calls from them.
        assert mock_core_random_s1.call_count == 1 
        mock_core_randint_s1.assert_called_once_with(2, 4) # Check it was called for the if_true range

    # Scenario 2: Chance not met for page_count
    output_path_s2 = "test_output/pdf_prob_page_count_s2.pdf"
    with patch('synth_data_gen.core.base.random.random', return_value=0.8) as mock_core_random_s2, \
         patch('synth_data_gen.core.base.random.randint') as mock_core_randint_s2:
        
        mock_simple_doc_template_class.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        mock_doc_instance.reset_mock()

        pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s2)
    
        assert mock_core_random_s2.call_count == 1
        mock_core_randint_s2.assert_not_called()

def test_single_column_with_exact_table_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_tables_occurrence_config' (exact int) within 'single_column_text'."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
    mock_determine_count = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') 
    
    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    exact_table_count = 1
    def determine_count_side_effect(config_value, context_key):
        if context_key == "page_count": return 10
        elif context_key == "chapters": return 1
        elif context_key.startswith("sections_chap_"): return 0
        elif context_key.startswith("notes_chap_"): return 0
        elif context_key.startswith("images_chap_"): return 0
        elif context_key == "pdf_tables_occurrence": return exact_table_count
        elif context_key == "pdf_figures": return 0
        return 0 
    mock_determine_count.side_effect = determine_count_side_effect

    specific_config = {
        "title": "PDF Single Column with Table", "pdf_variant": "single_column_text", "page_count_config": 10,
        "chapters_config": 1, "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "table_generation": {"pdf_tables_occurrence_config": exact_table_count},
        "figure_generation": {"pdf_figures_occurrence_config": 0}, 
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right": 25}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_single_column_with_table.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    mock_determine_count.assert_any_call(exact_table_count, "pdf_tables_occurrence")
    assert mock_add_pdf_table_content.call_count == exact_table_count

def test_single_column_with_range_table_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_tables_occurrence_config' (range dict) within 'single_column_text'."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance

    table_range_config = {"min": 1, "max": 3}
    expected_tables = 2
    mock_base_randint.return_value = expected_tables

    def custom_determine_count_side_effect(config_val, context_key):
        if context_key == "pdf_tables_occurrence":
            return BaseGenerator._determine_count(pdf_generator_instance, config_val, context_key)
        elif context_key == "page_count": return 1 
        elif context_key == "chapters": return 1
        elif context_key.startswith("sections_chap_"): return 0
        elif context_key.startswith("notes_chap_"): return 0
        elif context_key.startswith("images_chap_"): return 0
        elif context_key == "pdf_figures": return 0
        return BaseGenerator._determine_count(pdf_generator_instance, config_val, context_key) 
    mock_determine_count_on_pdf.side_effect = custom_determine_count_side_effect
    
    specific_config = {
        "title": "Test PDF Range Tables", "pdf_variant": "single_column_text",
        "table_generation": {"pdf_tables_occurrence_config": table_range_config},
        "page_count_config": 1, "chapters_config": 1, "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0}, "multimedia": {"include_images": False, "images_config": 0},
        "figure_generation": {"pdf_figures_occurrence_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14},
        "mixed_page_sizes_orientations_chance": 0.0
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_range_tables.pdf"
    pdf_generator_instance.generate(specific_config, global_config, output_path)
    
    mock_determine_count_on_pdf.assert_any_call(table_range_config, "pdf_tables_occurrence")
    assert mock_add_pdf_table_content.call_count == expected_tables


def test_single_column_with_probabilistic_table_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_tables_occurrence_config' (probabilistic) within 'single_column_text'."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    # Patch random used in pdf.py for mixed_page_sizes_orientations_chance
    mocker.patch('synth_data_gen.generators.pdf.random.random', return_value=0.9) 

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance

    table_prob_config = {"chance": 0.7, "if_true": {"min": 1, "max": 2}, "if_false": 0}
    
    specific_pdf_config_base = {
        "title": "Test PDF Probabilistic Tables", "author": "Test Author Probabilistic",
        "pdf_variant": "single_column_text", 
        "table_generation": {"pdf_tables_occurrence_config": table_prob_config}, 
        "page_count_config": 1, "chapters_config": 1,
        "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "figure_generation": {"pdf_figures_occurrence_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14},
        "mixed_page_sizes_orientations_chance": 0.0 
    }
    global_config = {"default_language": "en"}

    def custom_determine_count_side_effect(config_value, context_key):
        if context_key == "pdf_tables_occurrence":
            return BaseGenerator._determine_count(pdf_generator_instance, config_value, context_key)
        elif context_key == "page_count":
            return BaseGenerator._determine_count(pdf_generator_instance, specific_pdf_config_base["page_count_config"], context_key)
        elif context_key == "chapters":
            return BaseGenerator._determine_count(pdf_generator_instance, specific_pdf_config_base["chapters_config"], context_key)
        elif context_key.startswith("sections_chap_"):
            return BaseGenerator._determine_count(pdf_generator_instance, specific_pdf_config_base["sections_per_chapter_config"], context_key)
        elif context_key.startswith("notes_chap_"):
            return BaseGenerator._determine_count(pdf_generator_instance, specific_pdf_config_base["notes_system"]["notes_config"], context_key)
        elif context_key.startswith("images_chap_"):
            return BaseGenerator._determine_count(pdf_generator_instance, 0, context_key) 
        elif context_key == "pdf_figures":
            return BaseGenerator._determine_count(pdf_generator_instance, specific_pdf_config_base["figure_generation"]["pdf_figures_occurrence_config"], context_key)
        # print(f"Warning: Unhandled context_key '{context_key}' in custom_determine_count_side_effect for probabilistic table test")
        return BaseGenerator._determine_count(pdf_generator_instance, config_value, context_key) 

    mock_determine_count_on_pdf.side_effect = custom_determine_count_side_effect

    # Scenario 1: Chance met (random value < chance)
    expected_tables_scenario1 = 1
    output_path_s1 = "test_output/pdf_prob_tables_s1.pdf"
    with patch('synth_data_gen.core.base.random.random', return_value=0.5) as mock_core_random_s1, \
         patch('synth_data_gen.core.base.random.randint', return_value=expected_tables_scenario1) as mock_core_randint_s1:
        
        mock_simple_doc_template_class.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        mock_doc_instance.reset_mock()
        mock_add_pdf_table_content.reset_mock()

        pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s1)
    
        mock_determine_count_on_pdf.assert_any_call(table_prob_config, "pdf_tables_occurrence")
        assert mock_add_pdf_table_content.call_count == expected_tables_scenario1
        mock_core_random_s1.assert_called_once() 
        mock_core_randint_s1.assert_called_once_with(table_prob_config["if_true"]["min"], table_prob_config["if_true"]["max"])


    # Scenario 2: Chance not met (random value >= chance)
    expected_tables_scenario2 = 0 
    output_path_s2 = "test_output/pdf_prob_tables_s2.pdf"
    
    mock_determine_count_on_pdf.side_effect = custom_determine_count_side_effect # Re-assign side effect as it might have been cleared by mock_determine_count_on_pdf.reset_mock() if that was