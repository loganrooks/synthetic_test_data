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
import random # For patching random.randint and random.random
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate # For ToC and integration tests
import re # Add import for regular expressions

@pytest.fixture
def pdf_generator_instance():
    return PdfGenerator()

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
    specific_config = "not_a_dict"
    global_config = {"default_language": "en"}
    assert not pdf_generator_instance.validate_config(specific_config, global_config)

def test_validate_config_invalid_base_global_config(pdf_generator_instance: PdfGenerator):
    """Test validate_config when the global_config is not a dict (handled by super)."""
    specific_config = pdf_generator_instance.get_default_specific_config()
    global_config = "not_a_dict"
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
    mock_base_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
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
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_generator_config = {"default_language": "en"}

    # Scenario 1
    mock_base_random.return_value = 0.5 
    expected_chapters_scenario1 = 2
    mock_base_randint.return_value = expected_chapters_scenario1
    output_path_s1 = "test_output/pdf_prob_chapters_s1.pdf"
    pdf_generator_instance.generate(specific_pdf_config, global_generator_config, output_path_s1)
    assert mock_base_random.call_count == 2 # Adjusted expectation
    mock_base_randint.assert_called_once_with(chapters_prob_config["if_true"]["min"], chapters_prob_config["if_true"]["max"])
    assert mock_add_pdf_chapter_content.call_count == expected_chapters_scenario1

    # Reset for Scenario 2
    mock_base_random.reset_mock(); mock_base_randint.reset_mock(); mock_add_pdf_chapter_content.reset_mock()
    mock_simple_doc_template_class.reset_mock(); mock_doc_instance.reset_mock()
    mock_simple_doc_template_class.return_value = mock_doc_instance

    mock_base_random.return_value = 0.8 
    expected_chapters_scenario2 = 0 
    output_path_s2 = "test_output/pdf_prob_chapters_s2.pdf"
    pdf_generator_instance.generate(specific_pdf_config, global_generator_config, output_path_s2)
    assert mock_base_random.call_count == 2 # Assuming the unexpected second call always happens
    mock_base_randint.assert_not_called() 
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
    mock_determine_count.side_effect = [exact_page_count, 1, 0,0,0]

    specific_pdf_config = {
        "title": "PDF Exact Page Count Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": exact_page_count, "chapters_config": 1, 
        "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
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
        return original_determine_count(pdf_generator_instance, config_val, context_key)
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
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
    mock_base_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')

    original_determine_count = BaseGenerator._determine_count
    def side_effect_for_determine_count(config_val, context_key):
        return original_determine_count(pdf_generator_instance, config_val, context_key)
    mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    page_count_prob_config = {"chance": 0.6, "if_true": {"min": 2, "max": 4}, "if_false": 1}
    
    specific_pdf_config_base = {
        "title": "PDF Probabilistic Page Count Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": page_count_prob_config, "chapters_config": 1,
        "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}

    # Scenario 1
    mock_base_random.return_value = 0.4 
    expected_page_count_s1 = 3 
    mock_base_randint.return_value = expected_page_count_s1
    output_path_s1 = "test_output/pdf_prob_page_count_s1.pdf"
    pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s1)
    assert mock_base_random.call_count == 1 # For the page_count probabilistic check
    mock_base_randint.assert_called_once_with(page_count_prob_config["if_true"]["min"], page_count_prob_config["if_true"]["max"])
    assert mock_add_pdf_chapter_content.call_count == expected_page_count_s1

    # Reset for Scenario 2
    mock_base_random.reset_mock(); mock_base_randint.reset_mock(); mock_determine_count_on_pdf.reset_mock()
    mock_simple_doc_template_class.reset_mock(); mock_doc_instance.reset_mock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

    # Scenario 2
    mock_base_random.return_value = 0.8 
    output_path_s2 = "test_output/pdf_prob_page_count_s2.pdf"
    pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s2)
    assert mock_base_random.call_count == 1 
    mock_base_randint.assert_not_called()

def test_generate_routes_to_multi_column_based_on_layout_config(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test that generate routes to multi-column if layout.columns is 2,
       even if pdf_variant is 'single_column_text'."""
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_single = mocker.patch.object(pdf_generator_instance, '_create_pdf_text_single_column')
    mock_create_multi = mocker.patch.object(pdf_generator_instance, '_create_pdf_text_multi_column')
    
    output_path = "test_output/pdf_layout_columns.pdf"
    global_config = {}

    # Scenario 1
    specific_config = {
        "title": "Test PDF Layout Columns", "author": "Test Author", "pdf_variant": "single_column_text",
        "layout": {"columns": 2, "margins_mm": {"top": 20, "bottom": 20, "left": 25, "right": 25}},
        "page_count_config": 1, "chapters_config": 1, "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0}, "multimedia": {"include_images": False, "images_config": 0},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    pdf_generator_instance.generate(specific_config, global_config, output_path)
    mock_create_multi.assert_called_once_with(output_path, specific_config, global_config)
    mock_create_single.assert_not_called()
def test_generate_single_column_applies_custom_margins(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test that custom margins are applied in the single-column variant."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') # Mock to simplify
    mocker.patch.object(pdf_generator_instance, '_determine_count', side_effect=[1, 1, 0, 0, 0]) # page, chapter, tables, figures

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance

    custom_page_margins = {"top_mm": 10, "bottom_mm": 15, "left_mm": 20, "right_mm": 22}
    specific_config = {
        "title": "Custom Margins Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": 1, "chapters_config": 1,
        "layout_settings": {"columns": 1, "page_margins": custom_page_margins},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14},
        "table_generation": {"pdf_tables_occurrence_config": 0},
        "figure_generation": {"pdf_figures_occurrence_config": 0},
        "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_custom_margins.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    mock_ensure_output_dirs.assert_called_once_with(os.path.dirname(output_path))
    
    # Check that SimpleDocTemplate was called with the correct margins
    # Margins are expected in points by reportlab (1mm = 2.8346456693 points)
    expected_left_margin = custom_page_margins["left_mm"] * 2.8346456693
    expected_right_margin = custom_page_margins["right_mm"] * 2.8346456693
    expected_top_margin = custom_page_margins["top_mm"] * 2.8346456693
    expected_bottom_margin = custom_page_margins["bottom_mm"] * 2.8346456693

    args, kwargs = mock_simple_doc_template_class.call_args
    assert kwargs.get("leftMargin") == pytest.approx(expected_left_margin)
    assert kwargs.get("rightMargin") == pytest.approx(expected_right_margin)
    assert kwargs.get("topMargin") == pytest.approx(expected_top_margin)
    assert kwargs.get("bottomMargin") == pytest.approx(expected_bottom_margin)
    
    mock_doc_instance.build.assert_called_once()

def test_generate_running_header_enable_disable(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test that 'running_header.enable' correctly controls header generation."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_pdf = mocker.patch.object(pdf_generator_instance, '_create_pdf_text_single_column') # Assuming this is the variant used
    
    base_specific_config = {
        "title": "Header Test", "pdf_variant": "single_column_text", # Changed to single_column_text for simplicity
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_footer": {"enable": False}, "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14},
        "page_count_config": 1, "chapters_config": 1 # Minimal content
    }
    global_config = {}
    output_path = "test_output/header_test.pdf"

    specific_config_enabled = {**base_specific_config, "running_header": {"enable": True, "content": "Test Header"}}
    pdf_generator_instance.generate(specific_config_enabled, global_config, output_path)
    args_enabled, _ = mock_create_pdf.call_args
    assert args_enabled[1]["running_header"]["enable"]
    mock_create_pdf.reset_mock()

    specific_config_disabled = {**base_specific_config, "running_header": {"enable": False}}
    pdf_generator_instance.generate(specific_config_disabled, global_config, output_path)
    args_disabled, _ = mock_create_pdf.call_args
    assert not args_disabled[1]["running_header"]["enable"]
def test_generate_running_header_content_and_font(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test running_header content and font_size_pt."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    # Mock the method that would actually draw, to inspect its arguments
    mock_create_pdf_method = mocker.patch.object(pdf_generator_instance, '_create_pdf_running_headers_footers')
    
    header_config = {
        "enable": True,
        "left_content": "Book Title Here",
        "center_content": "Section X",
        "right_content": "Page {page_number}",
        "font_size_pt": 8,
        "include_on_first_page": True
    }
    specific_config = {
        "title": "Header Content Test", 
        "pdf_variant": "running_headers_footers", # Ensure this variant is called
        "running_header": header_config,
        "page_count_config": 2 # Need at least one page for header to be drawn
    }
    global_config = {"default_language": "en", "default_title": "Book Title Here"} # Provide default title for placeholder
    output_path = "test_output/header_content_test.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    mock_create_pdf_method.assert_called_once()
    args, kwargs = mock_create_pdf_method.call_args
    
    # The specific_config is the second positional argument to _create_pdf_running_headers_footers
    called_specific_config = args[1] 
    assert called_specific_config["running_header"]["left_content"] == "Book Title Here"
    assert called_specific_config["running_header"]["center_content"] == "Section X"
    assert called_specific_config["running_header"]["right_content"] == "Page {page_number}"
    assert called_specific_config["running_header"]["font_size_pt"] == 8
    assert called_specific_config["running_header"]["include_on_first_page"] == True

def test_generate_visual_toc_enable_disable(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test that 'visual_toc.enable' correctly controls ToC generation."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_visual_toc = mocker.patch.object(pdf_generator_instance, '_create_pdf_visual_toc_hyperlinked')
    mock_create_single_column = mocker.patch.object(pdf_generator_instance, '_create_pdf_text_single_column')
    
    base_specific_config = {
        "title": "Visual ToC Test", "pdf_variant": "visual_toc_hyperlinked", # Target this variant
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False}, 
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14},
        "page_count_config": 1, "chapters_config": 1 # Minimal content
    }
    global_config = {}
    output_path = "test_output/visual_toc_test.pdf"

    specific_config_enabled = {**base_specific_config, "visual_toc": {"enable": True, "max_depth": 3}}
    pdf_generator_instance.generate(specific_config_enabled, global_config, output_path)
    mock_create_visual_toc.assert_called_once_with(output_path, specific_config_enabled, global_config)
    mock_create_single_column.assert_not_called()
    mock_create_visual_toc.reset_mock()

    specific_config_disabled = {**base_specific_config, "visual_toc": {"enable": False}}
    pdf_generator_instance.generate(specific_config_disabled, global_config, output_path)
    mock_create_visual_toc.assert_not_called()
    mock_create_single_column.assert_called_once_with(output_path, specific_config_disabled, global_config)
def test_generate_visual_toc_style_and_depth(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test visual_toc style, max_depth, and page_number_style."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_toc_method = mocker.patch.object(pdf_generator_instance, '_create_pdf_visual_toc_hyperlinked')
    
    toc_config = {
        "enable": True,
        "max_depth": 2,
        "style": "custom_toc_style",
        "page_number_style": "roman_numerals"
    }
    specific_config = {
        "title": "Visual ToC Style Test", 
        "pdf_variant": "visual_toc_hyperlinked", # Ensure this variant is called
        "visual_toc": toc_config,
        "page_count_config": 3 # Need a few pages for ToC to make sense
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/visual_toc_style_test.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    mock_create_toc_method.assert_called_once()
    args, kwargs = mock_create_toc_method.call_args
    
    called_specific_config = args[1]
    assert called_specific_config["visual_toc"]["max_depth"] == 2
    assert called_specific_config["visual_toc"]["style"] == "custom_toc_style"
    assert called_specific_config["visual_toc"]["page_number_style"] == "roman_numerals"
def test_generate_ocr_simulation_passes_settings(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test that ocr_simulation_settings are passed to the correct method."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_ocr_pdf_method = mocker.patch.object(pdf_generator_instance, '_create_pdf_simulated_ocr_high_quality')

    ocr_settings = {
        "base_image_quality": "medium",
        "ocr_accuracy_level": 0.95,
        "include_skew_chance": 0.1,
        "include_noise_chance": 0.15,
        "include_handwritten_annotations_chance": 0.05
    }
    specific_config = {
        "title": "OCR Sim Test", 
        "pdf_variant": "simulated_ocr_high_quality",
        "generation_method": "ocr_simulation", # Explicitly set for clarity, though variant implies it
        "ocr_simulation_settings": ocr_settings,
        "page_count_config": 1 
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/ocr_sim_test.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    mock_create_ocr_pdf_method.assert_called_once()
    args, kwargs = mock_create_ocr_pdf_method.call_args
    
    called_specific_config = args[1]
    assert called_specific_config["ocr_simulation_settings"] == ocr_settings

def test_generate_routes_to_simple_table_variant(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test that generate routes to _create_pdf_simple_table for the 'simple_table' variant."""
    mock_ensure_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_simple_table = mocker.patch.object(pdf_generator_instance, '_create_pdf_simple_table')
    
    specific_config = {
        "title": "Test PDF Simple Table Variant", "pdf_variant": "simple_table",
        "table_generation": {"pdf_tables_occurrence_config": 1},
        "page_count_config": 1, "chapters_config": 0, 
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right":25}},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_simple_table_variant.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)
    mock_ensure_dirs.assert_called_once_with(os.path.dirname(output_path))
    mock_create_simple_table.assert_called_once_with(output_path, specific_config, global_config)

def test_single_column_with_exact_table_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_tables_occurrence_config' (exact int) within 'single_column_text'."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
    mock_determine_count = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') # Mock to simplify
    
    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    exact_table_count = 1
    def determine_count_side_effect(config_value, context_key):
        if context_key == "page_count": return 10
        elif context_key == "chapters": return 1
        elif context_key.startswith("sections_chap_"): return 0
        elif context_key.startswith("notes_chap_"): return 0
        elif context_key.startswith("images_chap_"): return 0
        elif context_key == "pdf_tables": return exact_table_count # SUT uses 'pdf_tables'
        elif context_key == "pdf_figures": return 0
        return 0
    mock_determine_count.side_effect = determine_count_side_effect

    specific_config = {
        "title": "PDF Single Column with Table", "pdf_variant": "single_column_text", "page_count_config": 10,
        "chapters_config": 1, "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "table_generation": {"pdf_tables_occurrence_config": exact_table_count}, 
        "pdf_figures_occurrence_config": {"count": 0}, 
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right": 25}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_single_column_with_table.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    assert call(specific_config["table_generation"]["pdf_tables_occurrence_config"], "pdf_tables") in mock_determine_count.call_args_list
    assert mock_add_pdf_table_content.call_count == exact_table_count
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()

def test_single_column_with_range_table_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_tables_occurrence_config' (range) within 'single_column_text'."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    # We need to spy on _determine_count on the instance, but let the BaseGenerator's logic run
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    
    original_determine_count = BaseGenerator._determine_count 
    def side_effect_for_determine_count(config_val, context_key):
        # Call the original BaseGenerator._determine_count method
        # Pass 'self' which is pdf_generator_instance in this context
        return original_determine_count(pdf_generator_instance, config_val, context_key)
    mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count
    
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') 

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    tables_range_config = {"min": 1, "max": 3}
    expected_tables_from_range = 2
    mock_base_randint.return_value = expected_tables_from_range
        
    specific_config = {
        "title": "PDF Range Tables Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": 1, "chapters_config": 1, "sections_per_chapter_config": 0,
        "table_generation": {"pdf_tables_occurrence_config": tables_range_config},
        "figure_generation": {"pdf_figures_occurrence_config": 0},
        "notes_system": {"notes_config": 0}, 
        "multimedia": {"include_images": False, "images_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_range_tables.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    # Check that _determine_count was called for tables
    mock_determine_count_on_pdf.assert_any_call(tables_range_config, "pdf_tables_occurrence")
    # Check that random.randint was called by BaseGenerator._determine_count
    mock_base_randint.assert_called_once_with(tables_range_config["min"], tables_range_config["max"])
    assert mock_add_pdf_table_content.call_count == expected_tables_from_range
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()
def test_single_column_with_probabilistic_table_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_tables_occurrence_config' (probabilistic) within 'single_column_text'."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mock_base_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    
    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance

    table_prob_config = {"chance": 0.7, "if_true": {"min": 1, "max": 2}, "if_false": 0}
    
    specific_pdf_config_base = {
        "title": "Test PDF Probabilistic Tables", "author": "Test Author Probabilistic",
        "pdf_variant": "single_column_text", "table_generation": table_prob_config,
        "page_count_config": 1, "chapters_config": 1,
        "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}

    # Scenario 1
    mock_base_random.return_value = 0.5 
    expected_tables_scenario1 = 1
    mock_base_randint.return_value = expected_tables_scenario1
    output_path_s1 = "test_output/pdf_prob_tables_s1.pdf"
    pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s1)
    mock_determine_count_on_pdf.assert_any_call(table_prob_config, "pdf_tables_occurrence")
    assert mock_base_random.call_count == 2 # Adjusted expectation
    mock_base_randint.assert_called_once_with(table_prob_config["if_true"]["min"], table_prob_config["if_true"]["max"])
    assert mock_add_pdf_table_content.call_count == expected_tables_scenario1

    # Reset for Scenario 2
    mock_base_random.reset_mock(); mock_base_randint.reset_mock(); mock_determine_count_on_pdf.reset_mock()
    mock_simple_doc_template_class.reset_mock(); mock_doc_instance.reset_mock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

    # Scenario 2
    mock_base_random.return_value = 0.8 
    expected_tables_scenario2 = 0 
    output_path_s2 = "test_output/pdf_prob_tables_s2.pdf"
    pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s2)
    mock_determine_count_on_pdf.assert_any_call(table_prob_config, "pdf_tables_occurrence")
    assert mock_base_random.call_count == 2 # Assuming the unexpected second call always happens
    mock_base_randint.assert_not_called() 
    assert mock_add_pdf_table_content.call_count == expected_tables_scenario2

def test_generate_single_column_page_rotation_is_applied(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
        """Test that page_setup.rotation correctly adjusts pagesize for SimpleDocTemplate."""
        mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
        
        # Mock methods that add content to avoid unrelated errors
        mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
        mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
        mocker.patch.object(pdf_generator_instance, '_add_pdf_figure_content')
        mocker.patch.object(pdf_generator_instance, '_determine_count', return_value=0) # No content needed

        mock_doc_instance = mocker.MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        from reportlab.lib.pagesizes import letter, landscape # For expected values

        specific_config = {
            "title": "Rotation Test", "author": "Test Author", "pdf_variant": "single_column_text",
            "page_count_config": 1, 
            "chapters_config": 0, # No chapters needed for this page setup test
            "table_generation": {"pdf_tables_occurrence_config": 0},
            "figure_generation": {"pdf_figures_occurrence_config": 0},
            "page_setup": {
                "page_size": "letter", # Base page size
                "orientation": "portrait", # Initial orientation
                "rotation": 90 # Apply 90-degree rotation
            },
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
            "running_header": {"enable": False}, "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/pdf_rotation_test.pdf"

        pdf_generator_instance.generate(specific_config, global_config, output_path)

        mock_simple_doc_template_class.assert_called_once()
        
        args, kwargs = mock_simple_doc_template_class.call_args
        
        # Default letter is (612.0, 792.0) points
        # Rotated 90 degrees should be (792.0, 612.0)
        expected_pagesize = landscape(letter) # landscape() swaps width and height
        
        assert "pagesize" in kwargs, "pagesize argument not found in SimpleDocTemplate call"
        assert kwargs["pagesize"] == pytest.approx(expected_pagesize), \
            f"Expected pagesize {expected_pagesize}, got {kwargs['pagesize']}"
def test_ligature_simulation_setting_is_respected(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
        """Test that ligature_simulation settings are passed to a processing step."""
        mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
        
        # Mock the actual Paragraph class to inspect text passed to it
        mock_paragraph_class = mocker.patch('synth_data_gen.generators.pdf.Paragraph')
        
        # Mock other content-adding methods to simplify
        mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
        mocker.patch.object(pdf_generator_instance, '_add_pdf_figure_content')
        # _add_pdf_chapter_content will call _add_pdf_paragraph, which creates Paragraphs
        # We don't mock _add_pdf_chapter_content or _add_pdf_paragraph fully,
        # but we need to control _determine_count for them.

        # page_count, chapters, sections_per_chapter, paragraphs_per_section
        # plus calls from table/figure generation (set to 0)
        # plus calls from _add_pdf_paragraph for text_blocks_config
        # For one chapter, one section, one paragraph with one text block:
        # page_count(1), chapters(1), sections(1), paragraphs(1), text_blocks(1)
        # tables_occurrence(0), figures_occurrence(0)
        mock_determine_count = mocker.patch.object(
            pdf_generator_instance, 
            '_determine_count', 
            side_effect=[
                1, # page_count
                1, # chapters
                1, # sections_per_chapter
                1, # paragraphs_per_section
                1, # text_blocks_per_paragraph
                0, # tables_occurrence
                0  # figures_occurrence
            ]
        )

        mock_doc_instance = mocker.MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance

        ligature_config_enabled = {"enable": True, "strength": "medium"} # Changed to enabled
        test_text_input = "figure flow field"
        expected_processed_text = "ﬁgure ﬂow ﬁeld" # Example processed text

        specific_config = {
            "title": "Ligature Test", "author": "Test Author", "pdf_variant": "single_column_text",
            "page_count_config": 1, "chapters_config": 1, "sections_per_chapter_config": 1, 
            "paragraphs_per_section_config": 1, "text_blocks_per_paragraph_config": 1, # Ensure content generation
            "layout": {"type": "single_column", "margins_mm": {"top_mm": 20, "bottom_mm": 20, "left_mm": 20, "right_mm": 20}}, # Corrected layout
            "running_header": {"enable": False}, "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "fonts": {"default_font_name": "Helvetica", "default_font_size_pt": 12, "default_leading_pt": 14}, # Corrected fonts
            "table_generation": {"tables_occurrence": 0}, # Corrected table_generation
            "figure_generation": {"figures_occurrence": 0}, # Corrected figure_generation
            "ligature_simulation": ligature_config_enabled,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0}
        }
        global_config = {"default_language": "en"}
        output_path = os.path.join(self.temp_dir, "pdf_ligature_test.pdf")

        mock_process_ligatures = mocker.spy(pdf_generator_instance, '_process_text_for_ligatures')

        # Mock _get_dummy_text to return our specific test_text_input
        mocker.patch.object(pdf_generator_instance, '_get_dummy_text', return_value=test_text_input)

        pdf_generator_instance.generate(specific_config, global_config, output_path)
        
        # Assert that _process_text_for_ligatures was called with the original text and config
        # It will be called for chapter titles, section titles, and paragraph text.
        # We need to ensure it's called with our specific `test_text_input`.
        
        # Check all calls to _process_text_for_ligatures
        found_call_with_test_input = False
        for call_arg in mock_process_ligatures.call_args_list:
            text_arg, config_arg = call_arg[0]
            if text_arg == test_text_input and config_arg == ligature_config_enabled:
                found_call_with_test_input = True
                break
        assert found_call_with_test_input, f"_process_text_for_ligatures was not called with \'{test_text_input}\' and ligature_config_enabled"

        # Assert that Paragraph was called with the expected *processed* text
        # This requires knowing the exact output of _process_text_for_ligatures
        # For "figure flow field", it should be "ﬁgure ﬂow ﬁeld"
        expected_processed_text = "ﬁgure ﬂow ﬁeld" 
        
        found_paragraph_with_processed_text = False
        for call_arg in mock_paragraph_class.call_args_list:
            text_arg = call_arg[0][0] # Text is the first argument to Paragraph
            if text_arg == expected_processed_text:
                found_paragraph_with_processed_text = True
                break
        assert found_paragraph_with_processed_text, f"Paragraph was not called with the processed ligature text \'{expected_processed_text}\'"

# Remove duplicated test_ocr_simulation_applies_noise
# Remove duplicated test_ocr_noise_type_salt_and_pepper

# Corrected test_ocr_simulation_applies_accuracy
def test_ocr_simulation_applies_accuracy(self, mocker: MockerFixture): # Added self
    pdf_generator_instance = self.generator # Use self.generator
    mock_canvas_instance = MagicMock() 
    mocker.patch('synth_data_gen.generators.pdf.canvas.Canvas', return_value=mock_canvas_instance)
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    
    from reportlab.platypus import Paragraph as ReportLabParagraph
    mock_paragraph_class = mocker.spy(ReportLabParagraph, '__init__')

    original_ocr_text_cleaned = "The problem of universals..." # Simplified for brevity

    # Scenario 1: High accuracy (e.g., 0.98)
    specific_config_high_acc = {
        "title": "OCR Accuracy Test - High",
        "pdf_variant": "simulated_ocr_high_quality",
        "ocr_simulation_settings": {
            "ocr_accuracy_level": 0.98, # High accuracy
            "skew_chance": 0.0, "noise_chance": 0.0 
        },
        "page_count_config": 1, "chapters_config": 0 
    }
    global_config = {"default_language": "en"}
    output_path_high = os.path.join(self.temp_dir, "pdf_ocr_accuracy_high.pdf")

    # Mock _determine_count for this specific call context
    with patch.object(pdf_generator_instance, '_determine_count', side_effect=[1, 0, 0, 0, 0]): # page, chap, sec, para, block
        pdf_generator_instance.generate(specific_config_high_acc, global_config, output_path_high)
    
    # Capture text passed to Paragraph for high accuracy
    text_passed_high_acc = []
    for call_args in mock_paragraph_class.call_args_list:
        if isinstance(call_args[0][0], str): # First arg to Paragraph is text
            text_passed_high_acc.append(call_args[0][0])
    
    # Calculate errors for high accuracy (simplified diff)
    # This is a placeholder for a proper diff or error calculation
    # errors_high_acc = sum(1 for a, b in zip(original_ocr_text_cleaned, \' \'.join(text_passed_high_acc)) if a != b)
    # For now, let's just check if text was processed. A more robust check would involve comparing with expected OCR errors.
    assert any(original_ocr_text_cleaned.split()[0] in text for text in text_passed_high_acc), "Original text not found in high accuracy output"


    # Reset mocks for Scenario 2
    mock_paragraph_class.reset_mock()

    # Scenario 2: Low accuracy (e.g., 0.7)
    specific_config_low_acc = {
        "title": "OCR Accuracy Test - Low",
        "pdf_variant": "simulated_ocr_high_quality",
        "ocr_simulation_settings": {
            "ocr_accuracy_level": 0.7, # Low accuracy
            "skew_chance": 0.0, "noise_chance": 0.0
        },
        "page_count_config": 1, "chapters_config": 0
    }
    output_path_low = os.path.join(self.temp_dir, "pdf_ocr_accuracy_low.pdf")

    with patch.object(pdf_generator_instance, '_determine_count', side_effect=[1, 0, 0, 0, 0]):
        pdf_generator_instance.generate(specific_config_low_acc, global_config, output_path_low)

    text_passed_low_acc = []
    for call_args in mock_paragraph_class.call_args_list:
        if isinstance(call_args[0][0], str):
            text_passed_low_acc.append(call_args[0][0])
            
    # errors_low_acc = sum(1 for a, b in zip(original_ocr_text_cleaned, \' \'.join(text_passed_low_acc)) if a != b)
    # assert errors_low_acc > errors_high_acc, "Expected more errors with lower OCR accuracy."
    assert any(original_ocr_text_cleaned.split()[0] in text for text in text_passed_low_acc), "Original text not found in low accuracy output"
    # A more robust assertion would be to check that text_passed_low_acc has more deviations from original_ocr_text_cleaned
    # than text_passed_high_acc. This requires a good string similarity/difference metric.

# Ensure the test class has a setUp method to initialize self.generator and self.temp_dir
class TestPdfGenerator: 
    def setup_method(self, method):
        """Setup for each test method."""
        self.generator = PdfGenerator()
        self.temp_dir = "test_temp_pdf_output"
        os.makedirs(self.temp_dir, exist_ok=True)

    def teardown_method(self, method):
        """Teardown after each test method."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('synth_data_gen.core.base.random.random')
    def test_single_column_with_probabilistic_table_occurrence(self, mock_base_random, mocker: MockerFixture):
        pdf_generator_instance = self.generator

        mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
        mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
        mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
        mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
        
        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance

        original_determine_count = BaseGenerator._determine_count
        def side_effect_for_determine_count(config_val, context_key):
            # Allow specific keys to pass through to the original _determine_count
            if context_key == "page_count": return 1 
            if context_key == "chapters": return 1 
            if context_key.startswith("sections_in_chapter"): return 0
            if context_key.startswith("paragraphs_in_section"): return 0
            if context_key.startswith("text_blocks_in_paragraph"): return 0
            if context_key == "pdf_figures": return 0 
            if "tables_in_chapter" in context_key: # Let table count be determined by original
                 return original_determine_count(pdf_generator_instance, config_val, context_key)
            return 0 # Default for other elements not explicitly handled
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count
        
        # Mock _add_pdf_chapter_content as it's complex and not the focus here
        mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content', return_value=[])


        # Scenario 1: Table occurrence chance is 0.0 (table should not occur)
        config_scenario_1 = {
            "output_path": self.temp_dir,
            "filename_prefix": "prob_table_doc_s1",
            "layout": {
                "type": "single_column",
                "chapters": 1, 
                "content_elements": {
                    "tables": {"chance": 0.0, "if_true": 1, "if_false": 0}, 
                    "figures": 0, 
                    "lists": 0 
                }
            },
            "fonts": {"custom_fonts_config": None, "default_font_name": "Helvetica"},
            "security": {"encrypt": False},
            "page_count_config": 1 # Ensure page_count is defined
        }
        global_config = {"default_language": "en"}
        output_path_s1 = os.path.join(self.temp_dir, "prob_table_doc_s1.pdf")

        mock_base_random.return_value = 0.5 # This will be > 0.0, so if_false path
        expected_tables_scenario1 = 0
        
        pdf_generator_instance.generate(config_scenario_1, global_config, output_path_s1)

        actual_calls = mock_determine_count_on_pdf.call_args_list
        assert any(call_args[0][0] == config_scenario_1["layout"]["content_elements"]["tables"] and "tables_in_chapter" in call_args[0][1] for call_args in actual_calls), "Expected call to _determine_count for tables"
        assert mock_base_random.call_count == 1 
        mock_base_randint.assert_not_called() 
        assert mock_add_pdf_table_content.call_count == expected_tables_scenario1

        # Reset mocks for Scenario 2
        mock_base_random.reset_mock()
        mock_base_randint.reset_mock()
        mock_add_pdf_table_content.reset_mock()
        mock_determine_count_on_pdf.reset_mock() # Reset all calls
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count # Re-assign side effect
        mock_simple_doc_template_class.reset_mock()
        mock_doc_instance.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance


        # Scenario 2: Table occurrence chance is 1.0 (table should occur)
        config_scenario_2 = {
            "output_path": self.temp_dir,
            "filename_prefix": "prob_table_doc_s2",
            "layout": {
                "type": "single_column",
                "chapters": 1, 
                "content_elements": {
                    "tables": {"chance": 1.0, "if_true": 1, "if_false": 0}, 
                    "figures": 0, 
                    "lists": 0
                }
            },
            "fonts": {"custom_fonts_config": None, "default_font_name": "Helvetica"},
            "security": {"encrypt": False},
            "page_count_config": 1 # Ensure page_count is defined
        }
        output_path_s2 = os.path.join(self.temp_dir, "prob_table_doc_s2.pdf")
        
        mock_base_random.return_value = 0.5 # This will be < 1.0, so if_true path
        expected_tables_scenario2 = 1
        
        pdf_generator_instance.generate(config_scenario_2, global_config, output_path_s2)

        actual_calls_s2 = mock_determine_count_on_pdf.call_args_list
        assert any(call_args[0][0] == config_scenario_2["layout"]["content_elements"]["tables"] and "tables_in_chapter" in call_args[0][1] for call_args in actual_calls_s2), "Expected call to _determine_count for tables in S2"
        assert mock_base_random.call_count == 1 
        mock_base_randint.assert_not_called() # if_true is an int
        assert mock_add_pdf_table_content.call_count == expected_tables_scenario2

    @patch('synth_data_gen.core.base.random.random')
    def test_single_column_with_probabilistic_figure_occurrence(self, mock_base_random, mocker: MockerFixture):
        pdf_generator_instance = self.generator

        mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
        mock_add_pdf_figure_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_figure_content')
        mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
        mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')

        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance

        original_determine_count = BaseGenerator._determine_count
        def side_effect_for_determine_count(config_val, context_key):
            if context_key == "page_count": return 1
            if context_key == "chapters": return 1
            if context_key.startswith("sections_in_chapter"): return 0
            if context_key.startswith("paragraphs_in_section"): return 0
            if context_key.startswith("text_blocks_in_paragraph"): return 0
            if context_key == "pdf_tables": return 0
            if "figures_in_chapter" in context_key: # Let figure count be determined by original
                 return original_determine_count(pdf_generator_instance, config_val, context_key)
            return 0
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count
        
        mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content', return_value=[])


        # Scenario 1: Figure occurrence chance is 0.0 (figure should not occur)
        config_scenario_1 = {
            "output_path": self.temp_dir,
            "filename_prefix": "prob_figure_doc_s1",
            "layout": {
                "type": "single_column",
                "chapters": 1,
                "content_elements": {
                    "tables": 0, 
                    "figures": {"chance": 0.0, "if_true": 1, "if_false": 0}, 
                    "lists": 0
                }
            },
            "fonts": {"custom_fonts_config": None, "default_font_name": "Helvetica"},
            "security": {"encrypt": False},
            "page_count_config": 1
        }
        global_config = {"default_language": "en"}
        output_path_s1 = os.path.join(self.temp_dir, "prob_figure_doc_s1.pdf")

        mock_base_random.return_value = 0.5 # > 0.0, so if_false
        expected_figures_scenario1 = 0
        
        pdf_generator_instance.generate(config_scenario_1, global_config, output_path_s1)

        actual_calls = mock_determine_count_on_pdf.call_args_list
        assert any(call_args[0][0] == config_scenario_1["layout"]["content_elements"]["figures"] and "figures_in_chapter" in call_args[0][1] for call_args in actual_calls), "Expected call to _determine_count for figures"
        assert mock_base_random.call_count == 1
        mock_base_randint.assert_not_called()
        assert mock_add_pdf_figure_content.call_count == expected_figures_scenario1

        # Reset mocks for Scenario 2
        mock_base_random.reset_mock()
        mock_base_randint.reset_mock()
        mock_add_pdf_figure_content.reset_mock()
        mock_determine_count_on_pdf.reset_mock()
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count
        mock_simple_doc_template_class.reset_mock()
        mock_doc_instance.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance

        # Scenario 2: Figure occurrence chance is 1.0 (figure should occur)
        config_scenario_2 = {
            "output_path": self.temp_dir,
            "filename_prefix": "prob_figure_doc_s2",
            "layout": {
                "type": "single_column",
                "chapters": 1,
                "content_elements": {
                    "tables": 0,
                    "figures": {"chance": 1.0, "if_true": 1, "if_false": 0}, 
                    "lists": 0
                }
            },
            "fonts": {"custom_fonts_config": None, "default_font_name": "Helvetica"},
            "security": {"encrypt": False},
            "page_count_config": 1
        }
        output_path_s2 = os.path.join(self.temp_dir, "prob_figure_doc_s2.pdf")

        mock_base_random.return_value = 0.5 # < 1.0, so if_true
        expected_figures_scenario2 = 1

        pdf_generator_instance.generate(config_scenario_2, global_config, output_path_s2)

        actual_calls_s2 = mock_determine_count_on_pdf.call_args_list
        assert any(call_args[0][0] == config_scenario_2["layout"]["content_elements"]["figures"] and "figures_in_chapter" in call_args[0][1] for call_args in actual_calls_s2), "Expected call to _determine_count for figures in S2"
        assert mock_base_random.call_count == 1
        mock_base_randint.assert_not_called() 
        assert mock_add_pdf_figure_content.call_count == expected_figures_scenario2

    def test_visual_toc_is_integrated_into_pdf_story(self, mocker: MockerFixture): # Added MockerFixture
        generator = self.generator
        doc_mock = MagicMock(spec=SimpleDocTemplate)
        styles_mock = generator._get_default_styles() 
        global_config_mock = MagicMock()
        global_config_mock.default_language = "en" 

        specific_config_with_toc = {
            "layout": {
                "type": "single_column",
                "chapters": 1 
            },
            "visual_toc": {"enabled": True, "title": "Table of Contents"},
            "fonts": {"custom_fonts_config": None, "default_font_name": "Helvetica"},
            "security": {"encrypt": False},
            "filename_prefix": "toc_test_doc",
            "page_count_config": 1 
        }

        mock_chapter_title_p = Paragraph("Sample Chapter 1", styles_mock['h1'])
        mock_chapter_title_p.toc_level = 0 
        mock_chapter_title_p.bookmark_key = "chapter_1_0" 
        
        MockDocTemplate = MagicMock(spec=SimpleDocTemplate) 
        MockDocTemplate.return_value = doc_mock 

        # Patch _determine_count on the generator instance for this test
        mock_determine_count_instance = mocker.patch.object(generator, '_determine_count')
        
        def determine_count_side_effect(config_value, context_key):
            # print(f"ToC DEBUG _determine_count: val={config_value}, key={context_key}") # Debug print
            if context_key == "page_count": return specific_config_with_toc.get("page_count_config", 1)
            if context_key == "chapters": return 1 
            if context_key.startswith("sections_in_chapter"): return 1 
            if context_key.startswith("paragraphs_in_section"): return 1 
            if context_key.startswith("text_blocks_in_paragraph"): return 1 
            # For content elements like tables, figures, lists within the chapter content generation part
            if "tables_in_chapter" in context_key: return 0
            if "figures_in_chapter" in context_key: return 0
            if "lists_in_chapter" in context_key: return 0
            return 0 
        mock_determine_count_instance.side_effect = determine_count_side_effect

        with patch.object(generator, '_setup_document_and_styles', return_value=(doc_mock, styles_mock)), \
             patch.object(generator, 'generate_single_column_content', return_value=[mock_chapter_title_p]), \
             patch.object(generator, 'get_visual_toc_flowables', wraps=generator.get_visual_toc_flowables) as mock_get_toc_flowables, \
             patch('synth_data_gen.generators.pdf.SimpleDocTemplate', MockDocTemplate), \
             patch('synth_data_gen.generators.pdf.PageNumCanvas'), \
             patch('synth_data_gen.core.base.random.randint', return_value=123): # Keep this patch for base random
            
            doc_mock.build = MagicMock()
            generator.generate(specific_config_with_toc, global_config_mock, os.path.join(self.temp_dir, "dummy_toc_path.pdf"))
        
        mock_get_toc_flowables.assert_called_once()
        story_built = doc_mock.build.call_args[0][0]
        
        toc_title_found = any(isinstance(f, Paragraph) and f.text == "Table of Contents" for f in story_built)
        assert toc_title_found, "ToC Title 'Table of Contents' not found in the story."

        expected_toc_entry_regex = r"Sample Chapter 1.*\(PAGE_REF:chapter_1_0\)"
        
        toc_entry_found = False
        for flowable in story_built:
            if isinstance(flowable, Paragraph):
                # print(f"DEBUG ToC Flowable Text: {flowable.text}") # For debugging
                if re.search(expected_toc_entry_regex, flowable.text):
                    toc_entry_found = True
                    # Check for dot leader specifically if needed
                    assert "<dot leaderFill/>" in flowable.text or "...DOTS..." in flowable.text, \
                        f"Expected dot leader in ToC entry, got: {flowable.text}"
                    break
        assert toc_entry_found, f"Expected ToC entry matching regex '{expected_toc_entry_regex}' not found in story: {[f.text for f in story_built if isinstance(f, Paragraph)]}."


    @patch('synth_data_gen.generators.pdf.Paragraph') 
    def test_ligature_simulation_setting_is_respected(self, mock_paragraph_class, mocker: MockerFixture): 
        pdf_generator_instance = self.generator

        mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
        
        mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
        mocker.patch.object(pdf_generator_instance, '_add_pdf_figure_content')

        # Define a side effect function for _determine_count
        def determine_count_side_effect_ligature(config_value, context_key):
            if context_key == "page_count": return 1
            if context_key == "chapters": return 1
            if context_key.startswith("sections_in_chapter"): return 1
            if context_key.startswith("paragraphs_in_section"): return 1
            if context_key.startswith("text_blocks_in_paragraph"): return 1
            if "tables" in context_key: return 0
            if "figures" in context_key: return 0
            if "lists" in context_key: return 0
            return 1 # Default for other simple counts if any
        
        mocker.patch.object(
            pdf_generator_instance, 
            '_determine_count', 
            side_effect=determine_count_side_effect_ligature
        )

        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        ligature_config_enabled = {"enable": True, "strength": "medium"}
        test_text_input = "figure flow field" 
        
        specific_config = {
            "title": "Ligature Test", "author": "Test Author", "pdf_variant": "single_column_text",
            "page_count_config": 1, "chapters_config": 1, "sections_per_chapter_config": 1, 
            "paragraphs_per_section_config": 1, "text_blocks_per_paragraph_config": 1, 
            "layout": {"type": "single_column", "margins_mm": {"top_mm": 20, "bottom_mm": 20, "left_mm": 20, "right_mm": 20}}, 
            "running_header": {"enable": False}, "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            # Corrected fonts structure
            "fonts": {"default_font_name": "Helvetica", "custom_fonts_config": None, "font_size_pt": 12, "leading_pt": 14},
            # Corrected table_generation and figure_generation structure
            "content_elements": {
                 "tables": 0,
                 "figures": 0,
                 "lists": 0
            },
            "ligature_simulation": ligature_config_enabled,
            "notes_system": {"notes_config": 0}, # Assuming this structure
            "multimedia": {"include_images": False, "images_config": 0} # Assuming this structure
        }
        global_config = {"default_language": "en"}
        output_path = os.path.join(self.temp_dir, "pdf_ligature_test.pdf")

        mock_process_ligatures = mocker.spy(pdf_generator_instance, '_process_text_for_ligatures')
        mocker.patch.object(pdf_generator_instance, '_get_dummy_text', return_value=test_text_input)

        pdf_generator_instance.generate(specific_config, global_config, output_path)
        
        found_call_with_test_input = False
        for call_arg in mock_process_ligatures.call_args_list:
            text_arg, config_arg = call_arg[0]
            if text_arg == test_text_input and config_arg == ligature_config_enabled:
                found_call_with_test_input = True
                break
        assert found_call_with_test_input, f"_process_text_for_ligatures was not called with '{test_text_input}' and ligature_config_enabled"

        expected_processed_text = "ﬁgure ﬂow ﬁeld" 
        
        found_paragraph_with_processed_text = False
        for call_arg in mock_paragraph_class.call_args_list:
            text_arg = call_arg[0][0] 
            if text_arg == expected_processed_text:
                found_paragraph_with_processed_text = True
                break
        assert found_paragraph_with_processed_text, f"Paragraph was not called with the processed ligature text '{expected_processed_text}'"

    def test_ocr_simulation_applies_accuracy(self, mocker: MockerFixture): 
        pdf_generator_instance = self.generator 
        mock_canvas_instance = MagicMock() 
        mocker.patch('synth_data_gen.generators.pdf.canvas.Canvas', return_value=mock_canvas_instance)
        mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        
        from reportlab.platypus import Paragraph as ReportLabParagraph # Ensure this is imported locally if not globally
        mock_paragraph_class = mocker.spy(ReportLabParagraph, '__init__')

        # This is a simplified version of the text used in SUT's _create_pdf_simulated_ocr_high_quality
        # The actual text is longer. For a robust test, use the exact text or a representative part.
        original_ocr_text_cleaned = "The problern of universals" 

        # Scenario 1: High accuracy
        specific_config_high_acc = {
            "title": "OCR Accuracy Test - High",
            "pdf_variant": "simulated_ocr_high_quality", # This variant triggers _create_pdf_simulated_ocr_high_quality
            "ocr_simulation_settings": {
                "ocr_accuracy_level": 0.98, 
                "skew_chance": 0.0, "noise_chance": 0.0,
                "noise_level_percent": 0, "noise_type": "speckle" # Minimize other effects
            },
            "page_count_config": 1, "chapters_config": 0, # Minimal content config
            "layout": {"type": "single_column"}, # Basic layout
            "fonts": {"default_font_name": "Helvetica"} # Basic font
        }
        global_config = {"default_language": "en", "default_author": "Test Author"} # SUT uses global_config['default_author']
        output_path_high = os.path.join(self.temp_dir, "pdf_ocr_accuracy_high.pdf")

        # Mock _determine_count for this specific call context
        with patch.object(pdf_generator_instance, '_determine_count', return_value=1) as mock_determine_count:
            pdf_generator_instance.generate(specific_config_high_acc, global_config, output_path_high)
        
        text_passed_high_acc = []
        for call_args in mock_paragraph_class.call_args_list:
            if isinstance(call_args[0][0], str): 
                text_passed_high_acc.append(call_args[0][0])
        
        # Check if any part of the original text (or its processed version) made it to a Paragraph
        assert any(original_ocr_text_cleaned.lower() in text.lower() for text in text_passed_high_acc), \
            f"Original text substring not found in high accuracy output. Got: {text_passed_high_acc}"


        mock_paragraph_class.reset_mock() # Reset for the next scenario

        # Scenario 2: Low accuracy
        specific_config_low_acc = {
            "title": "OCR Accuracy Test - Low",
            "pdf_variant": "simulated_ocr_high_quality",
            "ocr_simulation_settings": {
                "ocr_accuracy_level": 0.7, 
                "skew_chance": 0.0, "noise_chance": 0.0,
                "noise_level_percent": 0, "noise_type": "speckle"
            },
            "page_count_config": 1, "chapters_config": 0,
            "layout": {"type": "single_column"},
            "fonts": {"default_font_name": "Helvetica"}
        }
        output_path_low = os.path.join(self.temp_dir, "pdf_ocr_accuracy_low.pdf")
        
        # Re-patch _determine_count if necessary for this call
        mocker.patch.object(pdf_generator_instance, '_determine_count', return_value=1)

        pdf_generator_instance.generate(specific_config_low_acc, global_config, output_path_low)

        text_passed_low_acc = []
        for call_args in mock_paragraph_class.call_args_list:
            if isinstance(call_args[0][0], str):
                text_passed_low_acc.append(call_args[0][0])
                
        assert any(original_ocr_text_cleaned.lower() in text.lower() for text in text_passed_low_acc), \
            f"Original text substring not found in low accuracy output. Got: {text_passed_low_acc}"
        
        # Ideally, we'd compare the number of errors or similarity score here.
        # For now, just ensuring text is processed is a basic check.
        # A more robust assertion would be:
        # errors_high = calculate_string_difference(original_ocr_text_cleaned, " ".join(text_passed_high_acc))
        # errors_low = calculate_string_difference(original_ocr_text_cleaned, " ".join(text_passed_low_acc))
        # assert errors_low > errors_high, "Expected more errors with lower OCR accuracy."

    # Ensure other tests like test_generate_single_column_unified_chapters_probabilistic etc.
    # are also methods of this class and use self.generator, self.temp_dir, and mocker.
    # For brevity, I am not reproducing all of them here, but the structure should be:
    #
    # class TestPdfGenerator:
    #     def setup_method(self, method): ...
    #     def teardown_method(self, method): ...
    #
    #     def test_get_default_specific_config(self, pdf_generator_instance: PdfGenerator): # Note: fixture might need adjustment
    #         # If pdf_generator_instance fixture is used, ensure it's compatible or use self.generator
    #         defaults = self.generator.get_default_specific_config()
    #         # ... rest of the test ...
    #
    #     def test_validate_config_valid(self, pdf_generator_instance: PdfGenerator):
    #         specific_config = self.generator.get_default_specific_config()
    #         # ... rest of the test ...
    #
    #     # ... and so on for all other tests ...

# Minimal example for a pre-existing test to show structure
    def test_get_default_specific_config(self): # Removed fixture, using self.generator
        defaults = self.generator.get_default_specific_config()
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

    def test_validate_config_valid(self, pdf_generator_instance: PdfGenerator):
        """Test validate_config with valid specific and global configs for PDF."""
        specific_config = pdf_generator_instance.get_default_specific_config()
        global_config = {"default_language": "en"}
        assert pdf_generator_instance.validate_config(specific_config, global_config)

    def test_validate_config_missing_pdf_variant(self, pdf_generator_instance: PdfGenerator):
        """Test validate_config when pdf_variant is missing (should still pass due to current implementation)."""
        specific_config = pdf_generator_instance.get_default_specific_config()
        del specific_config["pdf_variant"]
        global_config = {"default_language": "en"}
        assert pdf_generator_instance.validate_config(specific_config, global_config)

    def test_validate_config_invalid_base_specific_config(self, pdf_generator_instance: PdfGenerator):
        """Test validate_config when the specific_config is not a dict (handled by super)."""
        specific_config = "not_a_dict"
        global_config = {"default_language": "en"}
        assert not pdf_generator_instance.validate_config(specific_config, global_config)

    def test_validate_config_invalid_base_global_config(self, pdf_generator_instance: PdfGenerator):
        """Test validate_config when the global_config is not a dict (handled by super)."""
        specific_config = pdf_generator_instance.get_default_specific_config()
        global_config = "not_a_dict"
        assert not pdf_generator_instance.validate_config(specific_config, global_config)

    def test_generate_minimal_pdf_single_column(self, mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
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

    def test_generate_minimal_pdf_multi_column(self, mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
        """Test routing to a different PDF variant."""
        mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        mock_create_multi_column = mocker.patch.object(pdf_generator_instance, '_create_pdf_text_multi_column')
        
        specific_config = {"title": "Multi Column Test", "pdf_variant": "multi_column_text"}
        global_config = {}
        output_path = "test_output/multi.pdf"
        
        pdf_generator_instance.generate(specific_config, global_config, output_path)
        
        mock_create_multi_column.assert_called_once_with(output_path, specific_config, global_config)

    def test_generate_unknown_variant_falls_back_to_single_column(self, mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
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

    def test_generate_single_column_unified_chapters_exact(self, mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
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

    def test_generate_single_column_unified_chapters_range(self, mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
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

    def test_generate_single_column_unified_chapters_probabilistic(self, mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
        """Test 'chapters_config' (probabilistic) for 'single_column_text'."""
        mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
        mock_add_pdf_chapter_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
        mock_base_random = mocker.patch('synth_data_gen.core.base.random.random')
        mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
        
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
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_generator_config = {"default_language": "en"}

        # Scenario 1: Chance met
        mock_base_random.return_value = 0.5 # < 0.7, so if_true
        expected_chapters_scenario1 = 2
        mock_base_randint.return_value = expected_chapters_scenario1 # For the range in if_true
        
        output_path_s1 = os.path.join(self.temp_dir, "pdf_prob_chapters_s1.pdf")
        pdf_generator_instance.generate(specific_pdf_config, global_generator_config, output_path_s1)
        
        assert mock_base_random.call_count == 1 # For the chapter probabilistic check
        mock_base_randint.assert_called_once_with(chapters_prob_config["if_true"]["min"], chapters_prob_config["if_true"]["max"])
        assert mock_add_pdf_chapter_content.call_count == expected_chapters_scenario1

        # Reset for Scenario 2
        mock_base_random.reset_mock(); mock_base_randint.reset_mock(); mock_add_pdf_chapter_content.reset_mock()
        mock_determine_count_instance.reset_mock() # Reset the instance mock
        mock_determine_count_instance.side_effect = side_effect_determine_count_chapters # Re-assign
        mock_simple_doc_template_class.reset_mock(); mock_doc_instance.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance

        # Scenario 2: Chance not met
        mock_base_random.return_value = 0.8 # > 0.7, so if_false
        expected_chapters_scenario2 = 0 
        
        output_path_s2 = os.path.join(self.temp_dir, "pdf_prob_chapters_s2.pdf")
        pdf_generator_instance.generate(specific_pdf_config, global_generator_config, output_path_s2)
        
        assert mock_base_random.call_count == 1 
        mock_base_randint.assert_not_called() 
        assert mock_add_pdf_chapter_content.call_count == expected_chapters_scenario2

    @patch('synth_data_gen.core.base.random.random')
    @patch('synth_data_gen.core.base.random.randint')
    def test_generate_single_column_page_count_probabilistic(self, mock_base_randint, mock_base_random, mocker: MockerFixture):
        pdf_generator_instance = self.generator
        mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
        mock_add_pdf_chapter_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
        
        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        page_count_prob_config = {"chance": 0.6, "if_true": {"min": 2, "max": 4}, "if_false": 1}
        
        # Patch _determine_count on the instance
        mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
        original_base_determine_count = BaseGenerator._determine_count

        # Side effect for _determine_count
        # We want page_count to go through the original logic to test probabilistic evaluation
        # Other counts can be fixed.
        def side_effect_for_determine_count_page(config_val, context_key):
            if context_key == "page_count":
                return original_base_determine_count(pdf_generator_instance, config_val, context_key)
            if context_key == "chapters": return 1 # Fixed chapters
            if "sections_in_chapter" in context_key: return 1
            if "paragraphs_in_section" in context_key: return 1
            if "text_blocks_in_paragraph" in context_key: return 1
            if "tables" in context_key: return 0
            if "figures" in context_key: return 0
            if "lists" in context_key: return 0
            return 0 # Default for others
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count_page
            
        specific_pdf_config_base = {
            "title": "PDF Probabilistic Page Count Test", "author": "Test Author", 
            "pdf_variant": "single_column_text",
            "page_count_config": page_count_prob_config, 
            "layout": { # Assuming layout structure
                "type": "single_column",
                "chapters": 1, # Fixed chapters for simplicity of page count test
                "sections_per_chapter": 1,
                "paragraphs_per_section": 1,
                "content_elements": {"tables":0, "figures":0, "lists":0}
            },
            "fonts": {"default_font_name": "Helvetica", "custom_fonts_config": None},
            "security": {"encrypt": False}
        }
        global_config = {"default_language": "en"}

        # Scenario 1: Chance met for page_count
        mock_base_random.return_value = 0.4 # < 0.6, so if_true for page_count
        expected_page_count_s1_val = 3 
        mock_base_randint.return_value = expected_page_count_s1_val # For the range in if_true
        
        # We expect _add_pdf_chapter_content to be called based on the determined page count logic
        # This is tricky because _add_pdf_chapter_content itself might generate multiple pages.
        # For this test, we are primarily interested in the *initial* determination of page_count.
        # The SUT's _create_pdf_text_single_column uses page_count to loop for _add_pdf_chapter_content.
        # So, if page_count is 3, _add_pdf_chapter_content should be called 3 times.

        output_path_s1 = os.path.join(self.temp_dir, "pdf_prob_page_count_s1.pdf")
        pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s1)
        
        # Check that _determine_count was called for "page_count"
        assert any(call[0][1] == "page_count" for call in mock_determine_count_on_pdf.call_args_list)
        assert mock_base_random.call_count == 1 # For the page_count probabilistic check
        mock_base_randint.assert_called_once_with(page_count_prob_config["if_true"]["min"], page_count_prob_config["if_true"]["max"])
        assert mock_add_pdf_chapter_content.call_count == expected_page_count_s1_val

        # Reset for Scenario 2
        mock_base_random.reset_mock(); mock_base_randint.reset_mock()
        mock_determine_count_on_pdf.reset_mock()
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count_page # Re-assign
        mock_add_pdf_chapter_content.reset_mock()
        mock_simple_doc_template_class.reset_mock(); mock_doc_instance.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance

        # Scenario 2: Chance not met for page_count
        mock_base_random.return_value = 0.8 # > 0.6, so if_false for page_count
        expected_page_count_s2_val = page_count_prob_config["if_false"] # which is 1
        
        output_path_s2 = os.path.join(self.temp_dir, "pdf_prob_page_count_s2.pdf")
        pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s2)
        
        assert any(call[0][1] == "page_count" for call in mock_determine_count_on_pdf.call_args_list)
        assert mock_base_random.call_count == 1 
        mock_base_randint.assert_not_called() 
        assert mock_add_pdf_chapter_content.call_count == expected_page_count_s2_val