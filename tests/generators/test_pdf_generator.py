import os
import shutil  # Added for tearDown equivalent
import sys
from unittest.mock import MagicMock, call  # Keep call and MagicMock, ensure patch is imported

import pytest
from pytest_mock import MockerFixture
from reportlab.lib.pagesizes import letter  # Add import

from synth_data_gen.core.base import BaseGenerator
from synth_data_gen.generators.pdf import PdfGenerator


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

def test_generate_unknown_variant_falls_back_to_single_column(mocker: MockerFixture, pdf_generator_instance: PdfGenerator, caplog):
    """Test that an unknown pdf_variant falls back to single_column_text."""
    import logging
    mock_ensure_output_dirs = mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_create_single_column = mocker.patch.object(pdf_generator_instance, '_create_pdf_text_single_column')

    specific_config = {"title": "Unknown Variant Test", "pdf_variant": "this_variant_does_not_exist"}
    global_config = {}
    output_path = "test_output/unknown_variant.pdf"

    with caplog.at_level(logging.WARNING):
        pdf_generator_instance.generate(specific_config, global_config, output_path)

    assert "Unknown PDF variant 'this_variant_does_not_exist'" in caplog.text
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
    assert mock_base_random.call_count == 1  # Fixed: guard check prevents unnecessary random() call
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
    assert mock_base_random.call_count == 1  # Fixed: guard check prevents unnecessary random() call
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
    mock_add_pdf_chapter_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
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

    # Scenario 1: chance met (0.4 < 0.6)
    mock_base_random.return_value = 0.4
    expected_page_count_s1 = 3
    mock_base_randint.return_value = expected_page_count_s1
    output_path_s1 = "test_output/pdf_prob_page_count_s1.pdf"
    pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s1)
    assert mock_base_random.call_count == 1 # For the page_count probabilistic check
    mock_base_randint.assert_called_once_with(page_count_prob_config["if_true"]["min"], page_count_prob_config["if_true"]["max"])

    # Reset for Scenario 2
    mock_base_random.reset_mock(); mock_base_randint.reset_mock(); mock_determine_count_on_pdf.reset_mock()
    mock_simple_doc_template_class.reset_mock(); mock_doc_instance.reset_mock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

    # Scenario 2: chance not met (0.8 > 0.6)
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
        elif context_key.startswith("sections_chap_") or context_key.startswith("notes_chap_") or context_key.startswith("images_chap_"): return 0
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
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')

    original_determine_count = BaseGenerator._determine_count
    def side_effect_for_determine_count(config_val, context_key):
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

    # Check that _determine_count was called for tables (actual key is "pdf_tables")
    mock_determine_count_on_pdf.assert_any_call(tables_range_config, "pdf_tables")
    # Verify expected table content was added
    assert mock_add_pdf_table_content.call_count == expected_tables_from_range
    mock_simple_doc_template_class.assert_called_once()
    mock_doc_instance.build.assert_called_once()
def test_single_column_with_probabilistic_table_occurrence(mocker: MockerFixture, pdf_generator_instance: PdfGenerator):
    """Test 'pdf_tables_occurrence_config' (probabilistic) within 'single_column_text'."""
    mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
    mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    mock_add_pdf_table_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_table_content')
    mock_add_pdf_chapter_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
    mock_determine_count_on_pdf = mocker.patch.object(pdf_generator_instance, '_determine_count')
    mock_base_random = mocker.patch('synth_data_gen.core.base.random.random')
    mock_base_randint = mocker.patch('synth_data_gen.core.base.random.randint')

    mock_doc_instance = mocker.MagicMock()
    mock_simple_doc_template_class.return_value = mock_doc_instance

    # Define side effect that returns proper int values
    table_prob_config = {"chance": 0.7, "if_true": {"min": 1, "max": 2}, "if_false": 0}
    def side_effect_for_determine_count(config_val, context_key):
        if context_key == "page_count" or context_key == "chapters":
            return 1
        elif context_key.startswith("sections_chap_") or context_key.startswith("notes_chap_") or context_key.startswith("images_chap_"):
            return 0
        elif context_key == "pdf_tables":
            # Return value based on mock_base_random for probabilistic
            original_determine_count = BaseGenerator._determine_count
            return original_determine_count(pdf_generator_instance, config_val, context_key)
        elif context_key == "pdf_figures":
            return 0
        return 0
    mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

    specific_pdf_config_base = {
        "title": "Test PDF Probabilistic Tables", "author": "Test Author Probabilistic",
        "pdf_variant": "single_column_text",
        "table_generation": {"pdf_tables_occurrence_config": table_prob_config},
        "page_count_config": 1, "chapters_config": 1,
        "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
        "multimedia": {"include_images": False, "images_config": 0},
        "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
        "running_header": {"enable": False}, "running_footer": {"enable": False},
        "page_numbering": {"enable": False},
        "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
    }
    global_config = {"default_language": "en"}

    # Scenario 1: chance met (0.5 < 0.7)
    mock_base_random.return_value = 0.5
    expected_tables_scenario1 = 1
    mock_base_randint.return_value = expected_tables_scenario1
    output_path_s1 = "test_output/pdf_prob_tables_s1.pdf"
    pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s1)
    # Check _determine_count was called for tables
    mock_determine_count_on_pdf.assert_any_call(table_prob_config, "pdf_tables")
    assert mock_add_pdf_table_content.call_count == expected_tables_scenario1

    # Reset for Scenario 2
    mock_base_random.reset_mock(); mock_base_randint.reset_mock(); mock_determine_count_on_pdf.reset_mock()
    mock_add_pdf_table_content.reset_mock()
    mock_simple_doc_template_class.reset_mock(); mock_doc_instance.reset_mock()
    mock_simple_doc_template_class.return_value = mock_doc_instance
    mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

    # Scenario 2: chance not met (0.8 > 0.7)
    mock_base_random.return_value = 0.8
    expected_tables_scenario2 = 0
    output_path_s2 = "test_output/pdf_prob_tables_s2.pdf"
    pdf_generator_instance.generate(specific_pdf_config_base, global_config, output_path_s2)
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

        from reportlab.lib.pagesizes import landscape  # For expected values

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
# =============================================================================
# Ligature Processing Tests (Unit Tests)
# =============================================================================

def test_process_text_for_ligatures_enabled(pdf_generator_instance: PdfGenerator):
    """Test _process_text_for_ligatures replaces fi and fl when enabled."""
    ligature_config = {"enable": True}
    input_text = "figure flow field"
    expected = "ﬁgure ﬂow ﬁeld"

    result = pdf_generator_instance._process_text_for_ligatures(input_text, ligature_config)
    assert result == expected


def test_process_text_for_ligatures_disabled(pdf_generator_instance: PdfGenerator):
    """Test _process_text_for_ligatures does not modify text when disabled."""
    ligature_config = {"enable": False}
    input_text = "figure flow field"

    result = pdf_generator_instance._process_text_for_ligatures(input_text, ligature_config)
    assert result == input_text  # No change


def test_process_text_for_ligatures_empty_config(pdf_generator_instance: PdfGenerator):
    """Test _process_text_for_ligatures with empty config defaults to disabled."""
    ligature_config = {}
    input_text = "figure flow field"

    result = pdf_generator_instance._process_text_for_ligatures(input_text, ligature_config)
    assert result == input_text  # No change (enable defaults to False)


# =============================================================================
# Text Degradation Tests (for OCR simulation)
# =============================================================================

def test_degrade_text_high_accuracy(pdf_generator_instance: PdfGenerator):
    """Test _degrade_text with high accuracy preserves most of text."""
    input_text = "The quick brown fox"
    # With 1.0 accuracy, text should be unchanged
    result = pdf_generator_instance._degrade_text(input_text, 1.0)
    assert result == input_text


def test_degrade_text_zero_accuracy(pdf_generator_instance: PdfGenerator):
    """Test _degrade_text with 0.0 accuracy replaces all characters."""
    input_text = "test"
    result = pdf_generator_instance._degrade_text(input_text, 0.0)
    # All characters should be replaced (none match original)
    assert len(result) == len(input_text)
    # With 0.0 accuracy, all characters are replaced
    assert result != input_text

class TestPdfGenerator:
    """
    Test class for PdfGenerator with setup/teardown for temporary directories.

    Note: Many test cases have standalone equivalents above. This class focuses on
    tests that benefit from the shared temp_dir setup and cleanup.
    """

    def setup_method(self, method):
        """Setup for each test method."""
        self.generator = PdfGenerator()
        self.temp_dir = "test_temp_pdf_output"
        os.makedirs(self.temp_dir, exist_ok=True)

    def teardown_method(self, method):
        """Teardown after each test method."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_visual_toc_flowables_generation(self):
        """Test get_visual_toc_flowables returns proper Table-based ToC entries."""
        from reportlab.platypus import Table

        specific_config = {
            "chapters_config": {
                "chapter_details": [
                    {"title": "Introduction", "level": 1, "toc_key": "intro"},
                    {"title": "Chapter 1", "level": 1, "toc_key": "ch1"},
                    {"title": "Section 1.1", "level": 2, "toc_key": "sec1_1"},
                ]
            },
            "visual_toc": {"max_depth": 2, "page_number_style": "dot_leader"},
            "page_setup": {"margins_mm": {"left_mm": 25, "right_mm": 25}}
        }
        global_config = {}
        page_numbers = {"intro": 1, "ch1": 3, "sec1_1": 5}

        flowables = self.generator.get_visual_toc_flowables(specific_config, global_config, page_numbers)

        # Should have 3 entries
        assert len(flowables) == 3
        # All should be Table instances (Table-based ToC entries)
        for f in flowables:
            assert isinstance(f, Table)

    def test_visual_toc_respects_max_depth(self):
        """Test that ToC entries beyond max_depth are excluded."""
        specific_config = {
            "chapters_config": {
                "chapter_details": [
                    {"title": "Chapter 1", "level": 1},
                    {"title": "Section 1.1", "level": 2},
                    {"title": "Subsection 1.1.1", "level": 3},  # Should be excluded at max_depth=2
                ]
            },
            "visual_toc": {"max_depth": 2, "page_number_style": "plain"}
        }
        global_config = {}

        flowables = self.generator.get_visual_toc_flowables(specific_config, global_config)

        # Only level 1 and 2 should be included
        assert len(flowables) == 2

    @pytest.mark.skipif(
        sys.version_info < (3, 9),
        reason="reportlab has hashlib compatibility issues with Python 3.8"
    )
    def test_ocr_simulation_creates_pdf(self, mocker: MockerFixture):
        """Test that OCR simulation variant creates a PDF file."""
        mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')

        specific_config = {
            "title": "OCR Simulation Test",
            "pdf_variant": "simulated_ocr_high_quality",
            "ocr_simulation_settings": {
                "ocr_accuracy_level": 0.95,
                "skew_chance": 0.0,
                "noise_chance": 0.0
            }
        }
        global_config = {"default_author": "Test Author"}
        output_path = os.path.join(self.temp_dir, "ocr_test.pdf")

        self.generator.generate(specific_config, global_config, output_path)

        # Verify PDF was created
        assert os.path.exists(output_path)

    def test_degrade_text_applies_degradation(self):
        """Test _degrade_text degrades text based on accuracy level."""
        # High accuracy - no changes
        result_high = self.generator._degrade_text("Hello", 1.0)
        assert result_high == "Hello"

        # Low accuracy - some degradation
        result_low = self.generator._degrade_text("Hello World", 0.5)
        assert len(result_low) == len("Hello World")
        # At 0.5 accuracy, roughly half the non-space chars should be changed

    def test_figure_generation_with_exact_count(self, mocker: MockerFixture):
        """Test figure generation with exact count configuration."""
        pdf_generator_instance = self.generator

        mocker.patch('synth_data_gen.generators.pdf.ensure_output_directories')
        mock_simple_doc_template_class = mocker.patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
        mock_add_pdf_figure_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_figure_content')
        mock_add_pdf_chapter_content = mocker.patch.object(pdf_generator_instance, '_add_pdf_chapter_content')
        mock_determine_count = mocker.patch.object(pdf_generator_instance, '_determine_count')

        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance

        # Define side effect that returns proper int values
        exact_figure_count = 2
        def side_effect_for_determine_count(config_val, context_key):
            if context_key == "page_count" or context_key == "chapters":
                return 1
            elif context_key.startswith("sections_chap_") or context_key.startswith("notes_chap_") or context_key.startswith("images_chap_") or context_key == "pdf_tables":
                return 0
            elif context_key == "pdf_figures":
                return exact_figure_count
            return 0
        mock_determine_count.side_effect = side_effect_for_determine_count

        specific_config = {
            "title": "Test PDF with Figures",
            "pdf_variant": "single_column_text",
            "figure_generation": {"pdf_figures_occurrence_config": exact_figure_count},
            "page_count_config": 1, "chapters_config": 1,
            "sections_per_chapter_config": 0, "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
            "running_header": {"enable": False}, "running_footer": {"enable": False},
        }
        global_config = {"default_language": "en"}
        output_path = os.path.join(self.temp_dir, "pdf_figures_test.pdf")

        pdf_generator_instance.generate(specific_config, global_config, output_path)

        # Check _determine_count was called for figures
        mock_determine_count.assert_any_call(exact_figure_count, "pdf_figures")
        assert mock_add_pdf_figure_content.call_count == exact_figure_count

    # Note: test_visual_toc_is_integrated_into_pdf_story was replaced by
    # test_visual_toc_flowables_generation and test_visual_toc_respects_max_depth above.

    # Note: test_ligature_simulation_setting_is_respected was replaced by the standalone
    # test_process_text_for_ligatures_* tests above which test the actual method directly.

    def test_ligature_processing_integration(self):
        """Test that ligature processing is applied when generating content with ligatures enabled."""
        ligature_config = {"enable": True}
        test_text = "figure flow field"
        expected = "ﬁgure ﬂow ﬁeld"

        result = self.generator._process_text_for_ligatures(test_text, ligature_config)
        assert result == expected

# End of TestPdfGenerator class - remaining tests below are duplicates
# of standalone tests at the top of the file and have been removed to
# avoid duplication. See standalone tests for:
# - test_get_default_specific_config
# - test_validate_config_*
# - test_generate_minimal_pdf_*
# - test_generate_single_column_*


# =============================================================================
# Additional standalone tests for ToC functionality
# =============================================================================

def test_create_toc_entry_table_dot_leader(pdf_generator_instance: PdfGenerator):
    """Test _create_toc_entry_table with dot_leader style."""
    from reportlab.platypus import Table

    table = pdf_generator_instance._create_toc_entry_table(
        title="Chapter 1: Introduction",
        page_ref="5",
        level=1,
        page_number_style="dot_leader",
        available_width=400
    )

    assert isinstance(table, Table)


def test_create_toc_entry_table_no_page_numbers(pdf_generator_instance: PdfGenerator):
    """Test _create_toc_entry_table with no_page_numbers style."""
    from reportlab.platypus import Table

    table = pdf_generator_instance._create_toc_entry_table(
        title="Chapter 2: Methods",
        page_ref="10",
        level=1,
        page_number_style="no_page_numbers",
        available_width=400
    )

    assert isinstance(table, Table)
