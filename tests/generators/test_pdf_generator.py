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
def test_generate_running_header_content_variations(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test that 'running_header.content' variations are correctly passed through."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    # Mock the method that would consume the header content, not the generate method itself
    # Assuming _create_pdf_running_headers_footers is the one that uses this.
    # If not, this mock target needs to be adjusted.
    mock_create_headers_footers = mocker.patch.object(pdf_generator_instance, '_create_pdf_running_headers_footers')
    
    base_specific_config = {
        "title": "Header Content Test", 
        "pdf_variant": "running_headers_footers", # Target this variant
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_footer": {"enable": False}, 
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14},
        "page_count_config": 1, 
        "chapters_config": 1 # Minimal content
    }
    global_config = {}
    output_path = "test_output/header_content_test.pdf"

    # Scenario 1: Custom header text
    custom_header_text = "My Custom Header"
    specific_config_custom = {
        **base_specific_config, 
        "running_header": {"enable": True, "content": custom_header_text, "right_content": ""} 
    }
    pdf_generator_instance.generate(specific_config_custom, global_config, output_path)
    
    # Check that the _create_pdf_running_headers_footers was called with the correct config
    args_custom, _ = mock_create_headers_footers.call_args
    assert args_custom[1]["running_header"]["content"] == custom_header_text
    mock_create_headers_footers.reset_mock()

    # Scenario 2: Different custom header text
    another_header_text = "Another Section Title"
    specific_config_another = {
        **base_specific_config, 
        "running_header": {"enable": True, "content": another_header_text, "right_content": "Page {page_number}"}
    }
    pdf_generator_instance.generate(specific_config_another, global_config, output_path)
    args_another, _ = mock_create_headers_footers.call_args
    assert args_another[1]["running_header"]["content"] == another_header_text
    assert args_another[1]["running_header"]["right_content"] == "Page {page_number}"
    mock_create_headers_footers.reset_mock()

    # Scenario 3: Empty header text (should still be enabled)
    specific_config_empty = {
        **base_specific_config, 
        "running_header": {"enable": True, "content": "", "right_content": "Only Page Num"}
    }
    pdf_generator_instance.generate(specific_config_empty, global_config, output_path)
    args_empty, _ = mock_create_headers_footers.call_args
    assert args_empty[1]["running_header"]["content"] == ""
    assert args_empty[1]["running_header"]["enable"] # Ensure it's still enabled
    assert args_empty[1]["running_header"]["right_content"] == "Only Page Num"
def test_generate_visual_toc_max_depth(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test that 'visual_toc.max_depth' is correctly passed through."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_visual_toc = mocker.patch.object(pdf_generator_instance, '_create_pdf_visual_toc_hyperlinked')
    
    base_specific_config = {
        "title": "Visual ToC Depth Test", 
        "pdf_variant": "visual_toc_hyperlinked", # Target this variant
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, 
        "running_footer": {"enable": False}, 
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14},
        "page_count_config": 1, 
        "chapters_config": 1 # Minimal content
    }
    global_config = {}
    output_path = "test_output/visual_toc_depth_test.pdf"

    # Scenario 1: Specific max_depth
    specific_depth = 2
    specific_config_depth_2 = {
        **base_specific_config, 
        "visual_toc": {"enable": True, "max_depth": specific_depth, "title": "Table of Contents"}
    }
    pdf_generator_instance.generate(specific_config_depth_2, global_config, output_path)
    args_depth_2, _ = mock_create_visual_toc.call_args
    assert args_depth_2[1]["visual_toc"]["max_depth"] == specific_depth
    mock_create_visual_toc.reset_mock()

    # Scenario 2: Different max_depth
    another_depth = 4
    specific_config_depth_4 = {
        **base_specific_config, 
        "visual_toc": {"enable": True, "max_depth": another_depth, "title": "Detailed ToC"}
    }
    pdf_generator_instance.generate(specific_config_depth_4, global_config, output_path)
    args_depth_4, _ = mock_create_visual_toc.call_args
    assert args_depth_4[1]["visual_toc"]["max_depth"] == another_depth
    mock_create_visual_toc.reset_mock()

    # Scenario 3: Default max_depth (if not provided, PdfGenerator should use its default)
    # This requires knowing the default. Assuming it's 3 based on common practices.
    # If the default is handled inside _create_pdf_visual_toc_hyperlinked, this test might need adjustment
    # or we trust the unit tests of _create_pdf_visual_toc_hyperlinked for default handling.
    # For now, let's assume the config is passed as is, and the component handles defaulting.
    specific_config_no_depth = {
        **base_specific_config, 
        "visual_toc": {"enable": True, "title": "Simple ToC"} # No max_depth specified
    }
    pdf_generator_instance.generate(specific_config_no_depth, global_config, output_path)
    args_no_depth, _ = mock_create_visual_toc.call_args
    assert "max_depth" not in args_no_depth[1]["visual_toc"] # Or assert it's a default if generate adds it
                                                       # Based on current pattern, it's likely not added if missing.
def test_single_column_with_range_table_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_tables_occurrence_config' (range) within 'single_column_text'."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') # Mock to simplify

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    table_occurrence_range_config = {"min": 1, "max": 3}
    expected_tables_from_range = 2
    mock_base_randint.return_value = expected_tables_from_range

    # Define a side_effect function for _determine_count
    # This ensures that when _determine_count is called for tables, it uses the mocked randint
    # and for other elements, it returns a default value (e.g., 1 or 0)
    def determine_count_side_effect(config_value, context_key):
        if context_key == "pdf_tables":
            # Call the original BaseGenerator._determine_count for the actual logic
            # but it will use the patched random.randint
            return BaseGenerator._determine_count(pdf_generator_instance, config_value, context_key)
        elif context_key == "page_count":
            return 10 # Default page count
        elif context_key == "chapters":
            return 1 # Default chapter count
        # Add other default return values for other context_keys if necessary
        return 0
    mock_determine_count_on_pdf.side_effect = determine_count_side_effect
    
    specific_config = {
        "title": "PDF Range Tables Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": 10, "chapters_config": 1, "sections_per_chapter_config": 0,
        "table_generation": {"pdf_tables_occurrence_config": table_occurrence_range_config},
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
    mock_determine_count_on_pdf.assert_any_call(table_occurrence_range_config, "pdf_tables")
    # Check that random.randint was called by _determine_count for the table config
    mock_base_randint.assert_called_once_with(table_occurrence_range_config["min"], table_occurrence_range_config["max"])
    assert mock_add_pdf_table_content.call_count == expected_tables_from_range
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()
def test_single_column_with_probabilistic_table_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_tables_occurrence_config' (probabilistic) within 'single_column_text'."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mock_base_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') # Mock to simplify

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    table_occurrence_prob_config = {"chance": 0.6, "if_true": {"min": 1, "max": 2}, "if_false": 0}
    
    # Define a side_effect function for _determine_count
    def determine_count_side_effect(config_value, context_key):
        if context_key == "pdf_tables":
            return BaseGenerator._determine_count(pdf_generator_instance, config_value, context_key)
        elif context_key == "page_count": return 10
        elif context_key == "chapters": return 1
        return 0
    mock_determine_count_on_pdf.side_effect = determine_count_side_effect
    
    base_specific_config = {
        "title": "PDF Prob Tables Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": 10, "chapters_config": 1, "sections_per_chapter_config": 0,
        "table_generation": {"pdf_tables_occurrence_config": table_occurrence_prob_config},
        "figure_generation": {"pdf_figures_occurrence_config": 0},
        "notes_system": {"notes_config": 0}, 
        "multimedia": {"include_images": False, "images_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}

    # Scenario 1: Chance hits, tables are generated
    mock_base_random.return_value = 0.4 # Lower than chance (0.6)
    expected_tables_s1 = 1 # Example, could be 1 or 2 based on if_true range
    mock_base_randint.return_value = expected_tables_s1
    output_path_s1 = "test_output/pdf_prob_tables_s1.pdf"
    
    pdf_generator_instance.generate(base_specific_config, global_config, output_path_s1)
    mock_determine_count_on_pdf.assert_any_call(table_occurrence_prob_config, "pdf_tables")
    mock_base_random.assert_called_once()
    mock_base_randint.assert_called_once_with(table_occurrence_prob_config["if_true"]["min"], table_occurrence_prob_config["if_true"]["max"])
    assert mock_add_pdf_table_content.call_count == expected_tables_s1
    
    # Reset mocks for Scenario 2
    mock_add_pdf_table_content.reset_mock()
    mock_determine_count_on_pdf.reset_mock()
    mock_determine_count_on_pdf.side_effect = determine_count_side_effect # Re-assign side_effect
    mock_base_random.reset_mock()
    mock_base_randint.reset_mock()
    mock_simple_doc_template_class.reset_mock() # Reset this as well
    mock_simple_doc_template_class.return_value = mock_doc_instance # Re-assign return_value


    # Scenario 2: Chance misses, no tables are generated
    mock_base_random.return_value = 0.8 # Higher than chance (0.6)
    expected_tables_s2 = 0
    output_path_s2 = "test_output/pdf_prob_tables_s2.pdf"

    pdf_generator_instance.generate(base_specific_config, global_config, output_path_s2)
    mock_determine_count_on_pdf.assert_any_call(table_occurrence_prob_config, "pdf_tables")
    mock_base_random.assert_called_once()
    mock_base_randint.assert_not_called() # Should not be called if chance misses and if_false is 0
    assert mock_add_pdf_table_content.call_count == expected_tables_s2
def test_single_column_table_content_row_col_counts(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'row_count_config' and 'col_count_config' for tables within 'single_column_text'."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    # _add_pdf_table_content should NOT be mocked here, as we need its internal calls to _determine_count
    # We need to mock _determine_count to control row/col counts specifically for the table
    mock_determine_count = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    exact_rows = 3
    exact_cols = 4
    
    # Side effect for _determine_count:
    # 1. pdf_tables occurrence
    # 2. page_count
    # 3. chapters
    # 4. table_rows (inside _add_pdf_table_content, which we are testing)
    # 5. table_cols (inside _add_pdf_table_content)
    # Other calls for figures etc.
    mock_determine_count.side_effect = [1, 10, 1, exact_rows, exact_cols, 0, 0, 0] 

    specific_config = {
        "title": "PDF Table Row/Col Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": 10, "chapters_config": 1,
        "table_generation": {
            "pdf_tables_occurrence_config": 1, # Generate one table
            "row_count_config": exact_rows,
            "col_count_config": exact_cols,
            # Other table params can be added here if needed for the test
        },
        "figure_generation": {"pdf_figures_occurrence_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_table_rows_cols.pdf"

    # We need to spy on the actual _add_pdf_table_content to see what it does with row/col counts
    # For now, let's assume _add_pdf_table_content will internally call _determine_count
    # for row_count_config and col_count_config.
    # The test will verify these calls to _determine_count.

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    # Check that _determine_count was called for table rows and columns
    # with the correct config values and context keys.
    # The context keys "table_rows" and "table_cols" are assumed for now.
    calls = [
        call(1, "pdf_tables"), # For the table occurrence itself
        call(10, "page_count"),
        call(1, "chapters"),
        call(exact_rows, "table_rows"), 
        call(exact_cols, "table_cols"),
        call(0, "figures") # Assuming figures is checked after tables
    ]
    # Allow for other calls like sections_per_chapter, notes, images within _add_pdf_chapter_content
    # For this test, we are primarily interested in the table_rows and table_cols calls.
    
    # A more precise way if the order is strictly known:
    # mock_determine_count.assert_has_calls(calls, any_order=False) 
    # However, internal structure of _create_pdf_text_single_column might call _determine_count for other things.
    # So, we check for specific calls being present.
    
    found_row_call = any(c == call(exact_rows, "table_rows") for c in mock_determine_count.call_args_list)
    found_col_call = any(c == call(exact_cols, "table_cols") for c in mock_determine_count.call_args_list)
    
    assert found_row_call, "Expected _determine_count to be called for 'table_rows'"
    assert found_col_call, "Expected _determine_count to be called for 'table_cols'"

    # This assertion implicitly tests that _add_pdf_table_content was called once
    # because the row/col count determination happens inside it (or is triggered by it).
    # mock_add_pdf_table_content.assert_called_once() # Removed as it's not defined when testing internals
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()
def test_single_column_with_range_figure_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_figures_occurrence_config' (range) within 'single_column_text'."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_figure_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_figure_content')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') # Mock to simplify

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    figure_occurrence_range_config = {"min": 2, "max": 4}
    expected_figures_from_range = 3
    mock_base_randint.return_value = expected_figures_from_range

    def determine_count_side_effect(config_value, context_key):
        if context_key == "pdf_figures":
            return BaseGenerator._determine_count(pdf_generator_instance, config_value, context_key)
        elif context_key == "page_count": return 10
        elif context_key == "chapters": return 1
        elif context_key == "pdf_tables": return 0 # No tables for this test
        return 0
    mock_determine_count_on_pdf.side_effect = determine_count_side_effect
    
    specific_config = {
        "title": "PDF Range Figures Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": 10, "chapters_config": 1, "sections_per_chapter_config": 0,
        "table_generation": {"pdf_tables_occurrence_config": 0},
        "figure_generation": {"pdf_figures_occurrence_config": figure_occurrence_range_config},
        "notes_system": {"notes_config": 0}, 
        "multimedia": {"include_images": False, "images_config": 0}, # Assuming figures are distinct from general images
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_range_figures.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    mock_determine_count_on_pdf.assert_any_call(figure_occurrence_range_config, "pdf_figures")
    mock_base_randint.assert_called_once_with(figure_occurrence_range_config["min"], figure_occurrence_range_config["max"])
    assert mock_add_pdf_figure_content.call_count == expected_figures_from_range
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()
def test_single_column_with_probabilistic_figure_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_figures_occurrence_config' (probabilistic) within 'single_column_text'."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_figure_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_figure_content')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mock_base_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    figure_occurrence_prob_config = {"chance": 0.7, "if_true": {"min": 1, "max": 2}, "if_false": 0}

    def determine_count_side_effect(config_value, context_key):
        if context_key == "pdf_figures":
            return BaseGenerator._determine_count(pdf_generator_instance, config_value, context_key)
        elif context_key == "page_count": return 10
        elif context_key == "chapters": return 1
        elif context_key == "pdf_tables": return 0
        return 0 
    mock_determine_count_on_pdf.side_effect = determine_count_side_effect
    
    base_specific_config = {
        "title": "PDF Prob Figures Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": 10, "chapters_config": 1,
        "table_generation": {"pdf_tables_occurrence_config": 0},
        "figure_generation": {"pdf_figures_occurrence_config": figure_occurrence_prob_config},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
    }
    global_config = {"default_language": "en"}

    # Scenario 1: Chance hits
    mock_base_random.return_value = 0.5 
    expected_figures_s1 = 1
    mock_base_randint.return_value = expected_figures_s1
    output_path_s1 = "test_output/pdf_prob_figures_s1.pdf"
    
    pdf_generator_instance.generate(base_specific_config, global_config, output_path_s1)
    mock_determine_count_on_pdf.assert_any_call(figure_occurrence_prob_config, "pdf_figures")
    mock_base_random.assert_called_once()
    mock_base_randint.assert_called_once_with(figure_occurrence_prob_config["if_true"]["min"], figure_occurrence_prob_config["if_true"]["max"])
    assert mock_add_pdf_figure_content.call_count == expected_figures_s1
    
    # Reset mocks for Scenario 2
    mock_add_pdf_figure_content.reset_mock()
    mock_determine_count_on_pdf.reset_mock()
    mock_determine_count_on_pdf.side_effect = determine_count_side_effect
    mock_base_random.reset_mock()
    mock_base_randint.reset_mock()
    mock_simple_doc_template_class.reset_mock()
    mock_simple_doc_template_class.return_value = mock_doc_instance

    # Scenario 2: Chance misses
    mock_base_random.return_value = 0.9 
    expected_figures_s2 = 0
    output_path_s2 = "test_output/pdf_prob_figures_s2.pdf"

    pdf_generator_instance.generate(base_specific_config, global_config, output_path_s2)
    mock_determine_count_on_pdf.assert_any_call(figure_occurrence_prob_config, "pdf_figures")
    mock_base_random.assert_called_once()
    mock_base_randint.assert_not_called()
    assert mock_add_pdf_figure_content.call_count == expected_figures_s2
def test_single_column_figure_caption_content(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'caption_config.enable' and 'caption_config.text_options' for figures."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_determine_count = mocker.patch.object(pdf_generator_instance, '_determine_count')
    # Spy on _add_pdf_figure_content to check its internal calls if needed,
    # but primarily we'll check if _determine_count is called with caption text options.
    spy_add_pdf_figure_content = mocker.spy(pdf_generator_instance, '_add_pdf_figure_content')
    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content') # Mock to simplify

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    custom_caption = "This is a specific figure caption."
    
    # Corrected side_effect order:
    # 1. page_count
    # 2. chapters
    # 3. pdf_tables_occurrence_config
    #    (If >0, _add_pdf_table_content calls _determine_count for table_rows, table_cols)
    # 4. pdf_figures_occurrence_config
    # 5. figure_caption_text (from within _add_pdf_figure_content)
    # Additional placeholders for other potential calls (e.g., sections within chapters)
    mock_determine_count.side_effect = [
        10,             # page_count_config
        1,              # chapters_config
        0,              # pdf_tables_occurrence_config (set to 0 in this test's specific_config)
        1,              # pdf_figures_occurrence_config (set to 1 in this test's specific_config)
        custom_caption, # Expected return for figure_caption_text
        0, 0, 0         # Placeholders for other potential calls
    ]

    specific_config = {
        "title": "PDF Figure Caption Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": 10, "chapters_config": 1, "sections_per_chapter_config": 0,
        "table_generation": {"pdf_tables_occurrence_config": 0}, # Ensure no table calls to _determine_count
        "figure_generation": {
            "pdf_figures_occurrence_config": 1, 
            "caption_config": {
                "enable": True,
                "text_options": [custom_caption, "Another caption option"],
                "font_family": "Helvetica-Oblique",
                "font_size_pt": 9,
                "alignment": "CENTER"
            }
        },
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_figure_caption.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)
    
    spy_add_pdf_figure_content.assert_called_once()

    # Verify that _determine_count was called from within _add_pdf_figure_content
    # with the caption text options and the correct context key.
    found_caption_text_call = any(
        c_args == call(specific_config["figure_generation"]["caption_config"]["text_options"], "figure_caption_text")
        for c_args in mock_determine_count.call_args_list
    )
    assert found_caption_text_call, \
        f"Expected _determine_count to be called with caption_config.text_options and context_key 'figure_caption_text'.\nActual calls: {mock_determine_count.call_args_list}"

    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()
def test_single_column_figure_caption_content(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'caption_config.enable' and 'caption_config.text_options' for figures."""
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    # We will not mock _add_pdf_figure_content, but rather spy on what it passes to Paragraph or similar
    # For now, let's assume _add_pdf_figure_content will use _determine_count for caption text selection
    # and we can check the arguments passed to it.
    # This is a simplification; a more robust test would check the actual PDF content or ReportLab flowables.
    mock_determine_count = mocker.patch.object(pdf_generator_instance, '_determine_count')
    # Spy on the _add_pdf_figure_content method to check its arguments if needed, but for now, focus on _determine_count
    spy_add_pdf_figure_content = mocker.spy(pdf_generator_instance, '_add_pdf_figure_content')

    mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    
    custom_caption = "This is a custom figure caption."
    
    # Side effect for _determine_count:
    # 1. pdf_figures occurrence (set to 1)
    # 2. page_count
    # 3. chapters
    # 4. pdf_tables
    # 5. caption_text (this is what we want to verify is called with text_options)
    mock_determine_count.side_effect = [
        10,             # page_count_config
        1,              # chapters_config
        0,              # pdf_tables_occurrence_config
        1,              # pdf_figures_occurrence_config
        custom_caption  # figure_caption_text
    ]

    specific_config = {
        "title": "PDF Figure Caption Test", "author": "Test Author", "pdf_variant": "single_column_text",
        "page_count_config": 10, "chapters_config": 1,
        "table_generation": {"pdf_tables_occurrence_config": 0},
        "figure_generation": {
            "pdf_figures_occurrence_config": 1, # Generate one figure
            "caption_config": {
                "enable": True,
                "text_options": [custom_caption, "Another caption"], # Provide options
                "font_family": "Helvetica-Oblique",
                "font_size_pt": 9,
                "alignment": "CENTER"
            }
        },
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
    }
    global_config = {"default_language": "en"}
    output_path = "test_output/pdf_figure_caption.pdf"

    pdf_generator_instance.generate(specific_config, global_config, output_path)

    # Verify that _determine_count was called for selecting the caption text
    # The context key "figure_caption_text" is an assumption for now.
    # The actual implementation in _add_pdf_figure_content will determine this.
    
    # Check that _add_pdf_figure_content was called
    spy_add_pdf_figure_content.assert_called_once()
    
    # We expect _determine_count to be called with the text_options from caption_config
    # This is an indirect way to test if caption_config is being used.
    # A more direct test would involve inspecting the arguments to Paragraph if _add_pdf_figure_content creates one.
    
    # Based on the current _add_pdf_figure_content placeholder, it doesn't use _determine_count for captions.
    # This test will fail, driving the implementation.
    
    # Expected calls to _determine_count:
    # - pdf_figures_occurrence_config
    # - page_count_config
    # - chapters_config
    # - pdf_tables_occurrence_config (will return 0 based on side_effect)
    # - caption_text (from within _add_pdf_figure_content)
    
    # Let's refine the assertion to check for the specific call related to caption text.
    # This requires _add_pdf_figure_content to actually use _determine_count for captions.
    # The current placeholder _add_pdf_figure_content does not do this.
    # This test is designed to FAIL and drive that implementation.
    
    found_caption_text_call = False
    for call_args in mock_determine_count.call_args_list:
        args, _ = call_args
        if len(args) == 2 and args[0] == specific_config["figure_generation"]["caption_config"]["text_options"] and args[1] == "figure_caption_text":
            found_caption_text_call = True
            break
    assert found_caption_text_call, "Expected _determine_count to be called with caption_config.text_options and context_key 'figure_caption_text'"

    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()