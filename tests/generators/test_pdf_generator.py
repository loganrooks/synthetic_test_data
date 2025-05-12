import pytest
import os
import shutil # Added for tearDown equivalent
from pytest_mock import MockerFixture
from unittest.mock import call, MagicMock # Keep call and MagicMock
from synth_data_gen.generators.pdf import PdfGenerator
from synth_data_gen.core.base import BaseGenerator 
import random # For patching random.randint and random.random

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
    mock_base_random.assert_called_once()
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
    mock_base_random.assert_called_once()
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
    mock_determine_count_on_pdf.assert_any_call(page_count_prob_config, "page_count")
    mock_base_random.assert_called_once()
    mock_base_randint.assert_called_once_with(page_count_prob_config["if_true"]["min"], page_count_prob_config["if_true"]["max"])
    
    # Reset for Scenario 2
    mock_base_random.reset_mock(); mock_base_randint.reset_mock(); mock_determine_count_on_pdf.reset_mock()
    mock_simple_doc_template_class.reset_mock(); mock_doc_instance.reset_mock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

    # Scenario 2
    mock_base_random.return_value = 0.8 
    output_path_s2 = "test_output/pdf_prob_page_count_s2.pdf"
    pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s2)
    mock_determine_count_on_pdf.assert_any_call(page_count_prob_config, "page_count")
    mock_base_random.assert_called_once()
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
        elif context_key == "tables": return exact_table_count # Corrected context key
        elif context_key == "pdf_figures": return 0
        return 0
    mock_determine_count.side_effect = determine_count_side_effect

    specific_config = {
        "title": "PDF Single Column with Table", "pdf_variant": "single_column_text", "page_count_config": 10,
        "chapters_config": 1, "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "table_generation": {"pdf_tables_occurrence_config": exact_table_count}, 
        "pdf_figures_occurrence_config": {"count": 0}, 
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right":25}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_single_column_with_table.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    assert call(specific_config["table_generation"]["pdf_tables_occurrence_config"], "tables") in mock_determine_count.call_args_list
    assert mock_add_pdf_table_content.call_count == exact_table_count
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()

def test_single_column_with_exact_figure_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_figures_occurrence_config' (exact int) within 'single_column_text'."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_figure_to_story = mocker.patch.object(pdf_generator_instance, '_add_pdf_figure_content')
    mock_determine_count = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') # Mock to simplify
    mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content') # Mock to simplify

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    exact_figure_count = 1
    
    def determine_count_side_effect(config_value, context_key):
        if context_key == "page_count": return 10
        elif context_key == "chapters": return 1
        elif context_key.startswith("sections_chap_"): return 0
        elif context_key.startswith("notes_chap_"): return 0
        elif context_key.startswith("images_chap_"): return 0
        elif context_key == "pdf_tables": return 0
        elif context_key == "figures": return exact_figure_count # Corrected context key
        return 0
    mock_determine_count.side_effect = determine_count_side_effect

    specific_config = {
        "title": "PDF Exact Figures Test", "pdf_variant": "single_column_text", "page_count_config": 10,
        "chapters_config": 1, "sections_per_chapter_config": 0,
        "notes_system": {"notes_config": 0}, "multimedia": {"include_images": False, "images_config": 0},
        "pdf_tables_occurrence_config": {"count": 0},
        "figure_generation": {
            "pdf_figures_occurrence_config": {"count": exact_figure_count}
        },
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":25}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_exact_figures.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    assert call(specific_config["figure_generation"]["pdf_figures_occurrence_config"], "figures") in mock_determine_count.call_args_list
    assert mock_add_figure_to_story.call_count == exact_figure_count
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()