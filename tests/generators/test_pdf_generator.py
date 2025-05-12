import unittest
import os
from unittest.mock import patch, MagicMock, call
from synth_data_gen.generators.pdf import PdfGenerator
from synth_data_gen.core.base import BaseGenerator # Import BaseGenerator

class TestPdfGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = PdfGenerator()

    def test_get_default_specific_config(self):
        """Test that get_default_specific_config for PDF returns the expected structure."""
        defaults = self.generator.get_default_specific_config()
        
        self.assertIsInstance(defaults, dict)
        
        # Check for some key top-level default settings
        self.assertIn("generation_method", defaults)
        self.assertEqual(defaults["generation_method"], "from_html")
        self.assertIn("page_count_config", defaults)
        self.assertEqual(defaults["page_count_config"], 10)
        self.assertIn("author", defaults)
        self.assertEqual(defaults["author"], "Default PDF Author")
        self.assertIn("title", defaults)
        self.assertEqual(defaults["title"], "Synthetic PDF Document")
        self.assertIn("pdf_variant", defaults) # Important for routing in generate method
        self.assertEqual(defaults["pdf_variant"], "single_column_text")

        # Check for nested structures
        self.assertIn("layout", defaults)
        self.assertIsInstance(defaults["layout"], dict)
        self.assertIn("columns", defaults["layout"])
        self.assertEqual(defaults["layout"]["columns"], 1)
        self.assertIn("margins_mm", defaults["layout"])
        self.assertIsInstance(defaults["layout"]["margins_mm"], dict)
        self.assertEqual(defaults["layout"]["margins_mm"]["top"], 20)

        self.assertIn("running_header", defaults)
        self.assertIsInstance(defaults["running_header"], dict)
        self.assertTrue(defaults["running_header"]["enable"])
        self.assertEqual(defaults["running_header"]["right_content"], "Page {page_number}")

    def test_validate_config_valid(self):
        """Test validate_config with valid specific and global configs for PDF."""
        specific_config = self.generator.get_default_specific_config()
        global_config = {"default_language": "en"}
        self.assertTrue(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_missing_pdf_variant(self):
        """Test validate_config when pdf_variant is missing (should still pass due to current implementation)."""
        # Current PdfGenerator.validate_config only prints a warning for missing pdf_variant
        specific_config = self.generator.get_default_specific_config()
        del specific_config["pdf_variant"]
        global_config = {"default_language": "en"}
        self.assertTrue(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_invalid_base_specific_config(self):
        """Test validate_config when the specific_config is not a dict (handled by super)."""
        specific_config = "not_a_dict"
        global_config = {"default_language": "en"}
        self.assertFalse(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_invalid_base_global_config(self):
        """Test validate_config when the global_config is not a dict (handled by super)."""
        specific_config = self.generator.get_default_specific_config()
        global_config = "not_a_dict"
        self.assertFalse(self.generator.validate_config(specific_config, global_config))

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch.object(PdfGenerator, '_create_pdf_text_single_column') # Patching the instance method
    def test_generate_minimal_pdf_single_column(self, mock_create_single_column, mock_ensure_output_dirs):
        """Test the basic flow of the generate method for a minimal single-column PDF."""
        specific_config = {
            "title": "Test PDF",
            "author": "Test PDF Author",
            "pdf_variant": "single_column_text" # Explicitly select variant
            # Other settings will use defaults
        }
        global_config = {"default_author": "Global PDF Author"}
        output_path = "test_output/minimal.pdf"
        expected_dir_to_ensure = "test_output"

        returned_path = self.generator.generate(specific_config, global_config, output_path)

        mock_ensure_output_dirs.assert_called_once_with(expected_dir_to_ensure)
        mock_create_single_column.assert_called_once_with(output_path, specific_config, global_config)
        self.assertEqual(returned_path, output_path)

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch.object(PdfGenerator, '_create_pdf_text_multi_column') # Patching a different variant
    def test_generate_minimal_pdf_multi_column(self, mock_create_multi_column, mock_ensure_output_dirs):
        """Test routing to a different PDF variant."""
        specific_config = {
            "title": "Multi Column Test",
            "pdf_variant": "multi_column_text"
        }
        global_config = {}
        output_path = "test_output/multi.pdf"
        
        self.generator.generate(specific_config, global_config, output_path)
        
        mock_create_multi_column.assert_called_once_with(output_path, specific_config, global_config)

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch.object(PdfGenerator, '_create_pdf_text_single_column') # Default fallback
    def test_generate_unknown_variant_falls_back_to_single_column(self, mock_create_single_column, mock_ensure_output_dirs):
        """Test that an unknown pdf_variant falls back to single_column_text."""
        specific_config = {
            "title": "Unknown Variant Test",
            "pdf_variant": "this_variant_does_not_exist"
        }
        global_config = {}
        output_path = "test_output/unknown_variant.pdf"
        
        # We expect a print warning about the unknown variant, but it should still call the fallback.
        with patch('builtins.print') as mock_print:
            self.generator.generate(specific_config, global_config, output_path)
            mock_print.assert_any_call("Warning: Unknown PDF variant 'this_variant_does_not_exist'. Generating single_column_text instead.")

        mock_create_single_column.assert_called_once_with(output_path, specific_config, global_config)

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch('synth_data_gen.generators.pdf.SimpleDocTemplate') # Mock the class
    @patch.object(PdfGenerator, '_determine_count')
    @patch.object(PdfGenerator, '_add_pdf_chapter_content') # Assumed method for adding chapter to story
    def test_generate_single_column_unified_chapters_exact(
        self, mock_add_pdf_chapter_content, mock_determine_count,
        mock_simple_doc_template_class, mock_ensure_output_dirs
    ):
        """Test 'chapters_config' (exact int) for 'single_column_text' variant."""
        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        exact_chapter_count = 2
        # specific_config is defined *after* this block, so we can't use specific_config.get here.
        # The page_count_config call will happen first in _create_pdf_text_single_column.
        # For this test, the focus is chapters. Assume a default or fixed page_count for the mock's first return.
        # The actual specific_config for this test doesn't set page_count_config, so the SUT would use its default (10).
        mock_determine_count.side_effect = [
            10, # Mocked return for the page_count_config call
            exact_chapter_count, # For chapters_config
            0, # sections_per_chapter_config for chap 1
            0, # notes_config for chap 1
            0, # images_config for chap 1
            0, # sections_per_chapter_config for chap 2
            0, # notes_config for chap 2
            0  # images_config for chap 2
        ]

        specific_config = {
            "title": "PDF Exact Chapters Test",
            "author": "Test Author",
            "pdf_variant": "single_column_text",
            "chapters_config": exact_chapter_count, # Unified quantity
            "sections_per_chapter_config": 0, # Keep sub-elements simple
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            # Add other minimal required fields for single_column_text if any
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
            "running_header": {"enable": False},
            "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/pdf_exact_chapters.pdf"

        # This will call _create_pdf_text_single_column internally
        self.generator.generate(specific_config, global_config, output_path)

        # Check that _determine_count was called for "chapters" with the exact integer value
        self.assertIn(
            call(exact_chapter_count, "chapters"), # Corrected: use imported 'call'
            mock_determine_count.call_args_list
        )
        # Check that our assumed chapter adding method was called correctly
        self.assertEqual(mock_add_pdf_chapter_content.call_count, exact_chapter_count)
        mock_simple_doc_template_class.assert_called_once()
        mock_doc_instance.build.assert_called_once()

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    @patch.object(PdfGenerator, '_add_pdf_chapter_content')
    @patch('synth_data_gen.core.base.random.randint') # Patch randint where BaseGenerator calls it
    def test_generate_single_column_unified_chapters_range(
        self, mock_base_randint, mock_add_pdf_chapter_content,
        mock_simple_doc_template_class, mock_ensure_output_dirs # ensure_output_dirs is from class-level patch
    ):
        """Test 'chapters_config' (range object) for 'single_column_text' variant,
        ensuring BaseGenerator._determine_count uses the patched random.randint."""
        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        chapters_range_config = {"min": 2, "max": 5}
        expected_chapters_from_range = 3 # This is what random.randint will return
        mock_base_randint.return_value = expected_chapters_from_range

        # This is the specific configuration for the PDF document itself
        specific_pdf_config = {
            "title": "Test PDF Range Chapters",
            "author": "Test Author Range Chapters",
            "variant": "single_column_text",
            "chapters_config": chapters_range_config,
            "sections_config": {"min": 0, "max": 0},
            "paragraphs_config": {"min": 1, "max": 1},
            "sentences_config": {"min": 1, "max": 1},
            "words_config": {"min": 1, "max": 1},
            "images_config": {"min": 0, "max": 0},
            "tables_config": {"min": 0, "max": 0},
            "lists_config": {"min": 0, "max": 0},
            "code_blocks_config": {"min": 0, "max": 0},
            "blockquotes_config": {"min": 0, "max": 0},
            "text_boxes_config": {"min": 0, "max": 0},
            "diagrams_config": {"min": 0, "max": 0},
            "charts_config": {"min": 0, "max": 0},
            "math_formulas_config": {"min": 0, "max": 0},
            "footnotes_config": {"min": 0, "max": 0},
            "endnotes_config": {"min": 0, "max": 0},
            "index_terms_config": {"min": 0, "max": 0},
            "glossary_terms_config": {"min": 0, "max": 0},
            "bibliography_entries_config": {"min": 0, "max": 0},
            "appendices_config": {"min": 0, "max": 0},
            "cover_config": {"include_cover": False},
            "toc_config": {"include_toc": False},
            "header_config": {"include_header": False},
            "footer_config": {"include_footer": False},
            "page_numbering_config": {"include_page_numbers": False},
            "font_config": {"font_name": "Helvetica", "font_size_pt": 12, "line_spacing_pt": 14},
            "page_layout": {"page_width_mm": 210, "page_height_mm": 297, "left_margin_mm": 20, "right_margin_mm": 20, "top_margin_mm": 25, "bottom_margin_mm": 25},
        }

        # This is the global configuration that includes the specific PDF config
        # and other top-level settings.
        global_generator_config = {
            "output_directory_base": "test_output_pdf_range_chapters_global",
            "output_filename_base": "test_doc_range_global",
            "document_template_class": "synth_data_gen.document_templates.SimpleDocTemplate",
            "random_seed": 42,
            "debug_mode": False,
            "file_types": {
                "pdf": specific_pdf_config # Embed the specific config here
            }
        }
        
        # Construct the output path
        output_dir = os.path.join(
            global_generator_config["output_directory_base"],
            self.generator.GENERATOR_ID
        )
        output_filename = global_generator_config["output_filename_base"] + ".pdf"
        final_output_path = os.path.join(output_dir, output_filename)

        mock_ensure_output_dirs.return_value = None # This mock comes from class-level patch
        mock_base_randint.reset_mock()
        mock_add_pdf_chapter_content.reset_mock()

        original_instance_determine_count_mock = None
        # Check if _determine_count is already a mock on the instance (from setUp)
        had_instance_mock = hasattr(self.generator, '_determine_count') and \
                            isinstance(self.generator._determine_count, MagicMock)

        if had_instance_mock:
            original_instance_determine_count_mock = self.generator._determine_count
            del self.generator._determine_count # Temporarily remove to call BaseGenerator's version

        try:
            # Call generate with the correct arguments
            self.generator.generate(
                specific_config=specific_pdf_config,
                global_config=global_generator_config,
                output_path=final_output_path
            )

            mock_base_randint.assert_called_once_with(
                chapters_range_config["min"], chapters_range_config["max"]
            )
            self.assertEqual(mock_add_pdf_chapter_content.call_count, expected_chapters_from_range)
        finally:
            # Restore the instance mock if it was present and we had temporarily removed it.
            if had_instance_mock and original_instance_determine_count_mock:
                self.generator._determine_count = original_instance_determine_count_mock

        mock_base_randint.assert_called_once_with(chapters_range_config["min"], chapters_range_config["max"])
        
        self.assertEqual(mock_add_pdf_chapter_content.call_count, expected_chapters_from_range)
        mock_simple_doc_template_class.assert_called_once()
        mock_doc_instance.build.assert_called_once()

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    @patch.object(PdfGenerator, '_add_pdf_chapter_content')
    @patch('synth_data_gen.core.base.random.random')  # For probability check
    @patch('synth_data_gen.core.base.random.randint') # For count if probability met
    def test_generate_single_column_unified_chapters_probabilistic(
        self, mock_base_randint, mock_base_random, mock_add_pdf_chapter_content,
        mock_simple_doc_template_class, mock_ensure_output_dirs
    ):
        """Test 'chapters_config' (probabilistic) for 'single_column_text'."""
        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance

        chapters_prob_config = {"chance": 0.7, "if_true": {"min": 1, "max": 3}, "if_false": 0}
        
        # Scenario 1: Probability met (random() < chance)
        mock_base_random.return_value = 0.5 # Less than 0.7
        expected_chapters_scenario1 = 2
        mock_base_randint.return_value = expected_chapters_scenario1

        specific_pdf_config = {
            "title": "Test PDF Probabilistic Chapters",
            "author": "Test Author Probabilistic",
            "pdf_variant": "single_column_text",
            "chapters_config": chapters_prob_config,
            "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
            "running_header": {"enable": False},
            "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_generator_config = {"default_language": "en"}
        output_path = "test_output/pdf_prob_chapters_s1.pdf"

        # Reset mocks for the first scenario
        mock_base_random.reset_mock()
        mock_base_randint.reset_mock()
        mock_add_pdf_chapter_content.reset_mock()
        mock_base_random.return_value = 0.5
        mock_base_randint.return_value = expected_chapters_scenario1
        
        original_instance_determine_count_mock = None
        had_instance_mock = hasattr(self.generator, '_determine_count') and \
                            isinstance(self.generator._determine_count, MagicMock)
        if had_instance_mock:
            original_instance_determine_count_mock = self.generator._determine_count
            del self.generator._determine_count

        try:
            self.generator.generate(specific_pdf_config, global_generator_config, output_path)
            mock_base_random.assert_called_once()
            mock_base_randint.assert_called_once_with(chapters_prob_config["if_true"]["min"], chapters_prob_config["if_true"]["max"])
            self.assertEqual(mock_add_pdf_chapter_content.call_count, expected_chapters_scenario1)
        finally:
            if had_instance_mock and original_instance_determine_count_mock:
                self.generator._determine_count = original_instance_determine_count_mock

        # Scenario 2: Probability not met (random() >= chance)
        mock_base_random.reset_mock()
        mock_base_randint.reset_mock()
        mock_add_pdf_chapter_content.reset_mock()
        mock_simple_doc_template_class.reset_mock() # Reset for new generate call
        mock_doc_instance.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance


        mock_base_random.return_value = 0.8 # Greater than 0.7
        expected_chapters_scenario2 = 0 # Based on "if_false": 0

        output_path_s2 = "test_output/pdf_prob_chapters_s2.pdf"
        
        if had_instance_mock: # Ensure it's removed again for the second call
            if hasattr(self.generator, '_determine_count') and isinstance(self.generator._determine_count, MagicMock):
                 original_instance_determine_count_mock = self.generator._determine_count # Re-capture if it was restored
            else: # It was restored as a real method
                 original_instance_determine_count_mock = None # Signal it's not a mock now
            
            if isinstance(self.generator._determine_count, MagicMock): # only delete if it's a mock
                del self.generator._determine_count


        try:
            self.generator.generate(specific_pdf_config, global_generator_config, output_path_s2)
            mock_base_random.assert_called_once()
            mock_base_randint.assert_not_called() # Should not be called if probability fails and if_false is 0
            self.assertEqual(mock_add_pdf_chapter_content.call_count, expected_chapters_scenario2)
        finally:
            if had_instance_mock and original_instance_determine_count_mock:
                 self.generator._determine_count = original_instance_determine_count_mock
            elif had_instance_mock and not original_instance_determine_count_mock and hasattr(self.generator, '_determine_count_backup_real'):
                 pass

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    @patch.object(PdfGenerator, '_add_pdf_chapter_content') # Keep this for consistency, though not directly used for page count
    @patch.object(PdfGenerator, '_determine_count') # Mock _determine_count
    def test_generate_single_column_page_count_exact(
        self, mock_determine_count, mock_add_pdf_chapter_content,
        mock_simple_doc_template_class, mock_ensure_output_dirs
    ):
        """Test 'page_count_config' (exact int) for 'single_column_text' variant."""
        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        exact_page_count = 5
        # _determine_count will be called for page_count_config first.
        # Then for chapters, assume 1 chapter with 0 sub-elements for simplicity.
        mock_determine_count.side_effect = [
            exact_page_count, # For page_count_config
            1, # For chapters_config
            0, # sections_per_chapter_config for chap 1
            0, # notes_config for chap 1
            0  # images_config for chap 1
        ]

        specific_pdf_config = {
            "title": "PDF Exact Page Count Test",
            "author": "Test Author",
            "pdf_variant": "single_column_text",
            "page_count_config": exact_page_count, # Unified quantity
            "chapters_config": 1, 
            "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
            "running_header": {"enable": False},
            "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/pdf_exact_page_count.pdf"

        self.generator.generate(specific_pdf_config, global_config, output_path)

        # Check that _determine_count was called for "page_count" with the exact integer value
        self.assertIn(
            call(exact_page_count, "page_count"),
            mock_determine_count.call_args_list
        )
        # This test focuses on page_count_config being passed to _determine_count.
        # The actual mechanism of enforcing page count in ReportLab is complex and
        # likely involves controlling the amount of content added to the story,
        # or specific ReportLab flowables/settings, which is beyond this specific unit test's scope
        # for _determine_count. We assume _create_pdf_text_single_column would use this.
        mock_simple_doc_template_class.assert_called_once()
        mock_doc_instance.build.assert_called_once()

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    @patch.object(PdfGenerator, '_add_pdf_chapter_content')
    @patch('synth_data_gen.core.base.random.randint') # Patch for BaseGenerator's _determine_count
    @patch.object(PdfGenerator, '_determine_count') # No wraps, will use side_effect
    def test_generate_single_column_page_count_range(
        self, mock_determine_count_on_pdf, mock_base_randint, mock_add_pdf_chapter_content,
        mock_simple_doc_template_class, mock_ensure_output_dirs
    ):
        """Test 'page_count_config' (range) for 'single_column_text' variant."""
        
        # Manually replicate 'wraps' behavior using side_effect to call the original method
        # This is to work around the TypeError encountered with 'wraps'.
        original_determine_count = BaseGenerator._determine_count
        def side_effect_for_determine_count(config_val, context_key):
            # self.generator is the instance of PdfGenerator from the test's setUp
            return original_determine_count(self.generator, config_val, context_key)
        
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        page_count_range_config = {"min": 3, "max": 7}
        expected_page_count_from_range = 4 # This is what random.randint will return
        mock_base_randint.return_value = expected_page_count_from_range

        # For this test, we are primarily interested in the page_count_config.
        # We'll simplify chapters and their sub-elements.
        # The first call to _determine_count in _create_pdf_text_single_column is for page_count.
        # The second is for chapters.
        # Subsequent calls are for sub-elements within chapters.
        
        # We expect the SUT's _determine_count to be called for page_count_config.
        # This call, in turn, should call random.randint (which is mock_base_randint).
        # Then, it will be called for chapters_config.
        
        specific_pdf_config = {
            "title": "PDF Range Page Count Test",
            "author": "Test Author",
            "pdf_variant": "single_column_text",
            "page_count_config": page_count_range_config, # Unified quantity
            "chapters_config": 1, # Keep chapters simple for this test
            "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
            "running_header": {"enable": False},
            "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/pdf_range_page_count.pdf"

        self.generator.generate(specific_pdf_config, global_config, output_path)

        # Check that PdfGenerator._determine_count was called for "page_count"
        # The first argument to call() is the config value, the second is the context string.
        mock_determine_count_on_pdf.assert_any_call(page_count_range_config, "page_count")
        
        # Check that base random.randint was called by _determine_count for the page_count_range_config
        mock_base_randint.assert_any_call(page_count_range_config["min"], page_count_range_config["max"])
        
        mock_simple_doc_template_class.assert_called_once()
        mock_doc_instance.build.assert_called_once()

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    @patch.object(PdfGenerator, '_add_pdf_chapter_content') # For chapter generation consistency
    @patch('synth_data_gen.core.base.random.random')  # For probability check in _determine_count
    @patch('synth_data_gen.core.base.random.randint') # For count if probability met in _determine_count
    @patch.object(PdfGenerator, '_determine_count')   # To spy on its calls
    def test_generate_single_column_page_count_probabilistic(
        self, mock_determine_count_on_pdf, mock_base_randint, mock_base_random,
        mock_add_pdf_chapter_content, mock_simple_doc_template_class, mock_ensure_output_dirs
    ):
        """Test 'page_count_config' (probabilistic) for 'single_column_text'."""
        
        # Setup side_effect for PdfGenerator._determine_count to call BaseGenerator._determine_count
        original_determine_count = BaseGenerator._determine_count
        def side_effect_for_determine_count(config_val, context_key):
            return original_determine_count(self.generator, config_val, context_key)
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count

        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        page_count_prob_config = {"chance": 0.6, "if_true": {"min": 2, "max": 4}, "if_false": 1}
        
        specific_pdf_config_base = {
            "title": "PDF Probabilistic Page Count Test",
            "author": "Test Author",
            "pdf_variant": "single_column_text",
            "page_count_config": page_count_prob_config,
            "chapters_config": 1, # Keep chapters simple
            "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":20, "right":20}},
            "running_header": {"enable": False},
            "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}

        # Scenario 1: Probability met (random() < chance)
        mock_base_random.return_value = 0.4 # Less than 0.6
        expected_page_count_scenario1 = 3
        mock_base_randint.return_value = expected_page_count_scenario1
        
        # Reset relevant mocks for scenario 1
        mock_determine_count_on_pdf.reset_mock() # Reset call history for the spy
        mock_base_random.reset_mock()
        mock_base_randint.reset_mock()
        mock_simple_doc_template_class.reset_mock()
        mock_doc_instance.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        # Re-apply side_effect as reset_mock clears it
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count
        mock_base_random.return_value = 0.4
        mock_base_randint.return_value = expected_page_count_scenario1

        output_path_s1 = "test_output/pdf_prob_page_count_s1.pdf"
        self.generator.generate(specific_pdf_config_base, global_config, output_path_s1)

        # Check that PdfGenerator._determine_count was called for "page_count"
        mock_determine_count_on_pdf.assert_any_call(page_count_prob_config, "page_count")
        # Check that base random.random was called by _determine_count
        mock_base_random.assert_called_once()
        # Check that base random.randint was called by _determine_count
        mock_base_randint.assert_called_once_with(page_count_prob_config["if_true"]["min"], page_count_prob_config["if_true"]["max"])
        
        mock_simple_doc_template_class.assert_called_once()
        mock_doc_instance.build.assert_called_once()

        # Scenario 2: Probability not met (random() >= chance)
        mock_base_random.reset_mock()
        mock_base_randint.reset_mock()
        mock_determine_count_on_pdf.reset_mock() # Reset call history for the spy
        mock_simple_doc_template_class.reset_mock()
        mock_doc_instance.reset_mock()
        mock_simple_doc_template_class.return_value = mock_doc_instance

        # Re-apply side_effect
        mock_determine_count_on_pdf.side_effect = side_effect_for_determine_count
        mock_base_random.return_value = 0.8 # Greater than 0.6
        # expected_page_count_scenario2 is page_count_prob_config["if_false"] which is 1
        # In this case, randint should not be called by _determine_count

        output_path_s2 = "test_output/pdf_prob_page_count_s2.pdf"
        self.generator.generate(specific_pdf_config_base, global_config, output_path_s2)

        mock_determine_count_on_pdf.assert_any_call(page_count_prob_config, "page_count")
        mock_base_random.assert_called_once()
        mock_base_randint.assert_not_called() # Should not be called if probability fails and if_false is an int
        
        mock_simple_doc_template_class.assert_called_once()
        mock_doc_instance.build.assert_called_once()

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch.object(PdfGenerator, '_create_pdf_text_single_column')
    @patch.object(PdfGenerator, '_create_pdf_text_multi_column')
    def test_generate_routes_to_multi_column_based_on_layout_config(
        self, mock_create_multi_column, mock_create_single_column, mock_ensure_output_dirs
    ):
        """Test that generate routes to multi-column if layout.columns is 2,
           even if pdf_variant is 'single_column_text'."""
        specific_config = {
            "title": "Test PDF Layout Columns",
            "author": "Test Author",
            "pdf_variant": "single_column_text", # Default text variant
            "layout": {
                "columns": 2, # Specify multi-column layout
                "margins_mm": {"top": 20, "bottom": 20, "left": 25, "right": 25}
            },
            # Add other minimal required fields for any text variant
            "page_count_config": 1,
            "chapters_config": 1,
            "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "running_header": {"enable": False},
            "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/pdf_layout_columns.pdf"

        self.generator.generate(specific_config, global_config, output_path)

        mock_ensure_output_dirs.assert_called_once_with(os.path.dirname(output_path))
        mock_create_multi_column.assert_called_once_with(output_path, specific_config, global_config)
        mock_create_single_column.assert_not_called()

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    # We are testing the routing and config passing to _create_pdf_running_headers_footers,
    # so we can mock the actual drawing part within that method if needed, or check its calls.
    # For now, let's assume _create_pdf_running_headers_footers correctly uses SimpleDocTemplate's build args.
    @patch.object(PdfGenerator, '_create_pdf_running_headers_footers')
    def test_generate_running_header_enable_disable(
        self, mock_create_headers_footers, mock_simple_doc_template_class, mock_ensure_output_dirs
    ):
        """Test that 'running_header.enable' correctly controls header generation."""
        
        # Scenario 1: Running header enabled
        specific_config_header_enabled = {
            "title": "Test PDF Running Header Enabled",
            "pdf_variant": "running_headers_footers", # Target this variant
            "running_header": {"enable": True, "left_content": "Header On"},
            "running_footer": {"enable": False}, # Keep footer simple
            "page_count_config": 1, "chapters_config": 1, # Minimal content
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right":25}},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path_enabled = "test_output/pdf_header_enabled.pdf"

        # We expect _create_pdf_running_headers_footers to be called.
        # The internal logic of _create_pdf_running_headers_footers should then use
        # SimpleDocTemplate with onFirstPage/onLaterPages if header is enabled.
        self.generator.generate(specific_config_header_enabled, global_config, output_path_enabled)
        mock_create_headers_footers.assert_called_once_with(output_path_enabled, specific_config_header_enabled, global_config)
        
        # To verify header drawing, we'd ideally check calls to canvas.drawString within the
        # draw_header_footer function passed to SimpleDocTemplate.build.
        # This requires a more complex mock setup if we don't mock _create_pdf_running_headers_footers.
        # For this TDD step, ensuring the correct variant method is called is sufficient.
        # A deeper test for _create_pdf_running_headers_footers itself would verify drawString.

        # Scenario 2: Running header disabled
        mock_create_headers_footers.reset_mock() # Reset for the second scenario

        specific_config_header_disabled = {
            "title": "Test PDF Running Header Disabled",
            "pdf_variant": "running_headers_footers",
            "running_header": {"enable": False, "left_content": "Header Off"}, # Explicitly disable
            "running_footer": {"enable": False},
            "page_count_config": 1, "chapters_config": 1,
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right":25}},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        output_path_disabled = "test_output/pdf_header_disabled.pdf"

        self.generator.generate(specific_config_header_disabled, global_config, output_path_disabled)
        mock_create_headers_footers.assert_called_once_with(output_path_disabled, specific_config_header_disabled, global_config)
        # Again, asserting the variant method is called. The internal logic of that method
        # should respect running_header.enable = False and not draw the header.

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch.object(PdfGenerator, '_create_pdf_visual_toc_hyperlinked')
    @patch.object(PdfGenerator, '_create_pdf_text_single_column') # Fallback if ToC is disabled
    def test_generate_visual_toc_enable_disable(
        self, mock_create_single_column, mock_create_visual_toc, mock_ensure_output_dirs
    ):
        """Test that 'visual_toc.enable' correctly controls ToC generation."""
        
        # Scenario 1: Visual ToC enabled
        specific_config_toc_enabled = {
            "title": "Test PDF Visual ToC Enabled",
            "pdf_variant": "visual_toc_hyperlinked", # Target this variant
            "visual_toc": {"enable": True, "max_depth": 3},
            "page_count_config": 1, "chapters_config": 1, # Minimal content
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right":25}},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path_enabled = "test_output/pdf_visual_toc_enabled.pdf"

        self.generator.generate(specific_config_toc_enabled, global_config, output_path_enabled)
        mock_create_visual_toc.assert_called_once_with(output_path_enabled, specific_config_toc_enabled, global_config)
        mock_create_single_column.assert_not_called()
        
        # Scenario 2: Visual ToC disabled
        mock_create_visual_toc.reset_mock()
        mock_create_single_column.reset_mock()

        specific_config_toc_disabled = {
            "title": "Test PDF Visual ToC Disabled",
            "pdf_variant": "visual_toc_hyperlinked", # Still target variant, but disable via config
            "visual_toc": {"enable": False, "max_depth": 3},
            "page_count_config": 1, "chapters_config": 1,
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right":25}},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        output_path_disabled = "test_output/pdf_visual_toc_disabled.pdf"

        # If visual_toc.enable is false, it should perhaps fall back to a default like single_column_text
        # or simply not call the _create_pdf_visual_toc_hyperlinked.
        # For this test, we'll assume it falls back to single_column if visual_toc is disabled.
        # This behavior will drive the implementation.
        self.generator.generate(specific_config_toc_disabled, global_config, output_path_disabled)
        mock_create_visual_toc.assert_not_called()
        mock_create_single_column.assert_called_once_with(output_path_disabled, specific_config_toc_disabled, global_config)

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch.object(PdfGenerator, '_create_pdf_simple_table')
    def test_generate_routes_to_simple_table_variant(
        self, mock_create_simple_table, mock_ensure_output_dirs
    ):
        """Test that generate routes to _create_pdf_simple_table for the 'simple_table' variant."""
        specific_config = {
            "title": "Test PDF Simple Table Variant",
            "pdf_variant": "simple_table",
            "table_generation": { # Add a basic table_generation config
                "pdf_tables_occurrence_config": 1
            },
            "page_count_config": 1, "chapters_config": 0, # Minimal content
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right":25}},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/pdf_simple_table_variant.pdf"

        self.generator.generate(specific_config, global_config, output_path)
        mock_ensure_output_dirs.assert_called_once_with(os.path.dirname(output_path))
        mock_create_simple_table.assert_called_once_with(output_path, specific_config, global_config)

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    @patch.object(PdfGenerator, '_add_pdf_chapter_content')
    @patch.object(PdfGenerator, '_determine_count')
    @patch.object(PdfGenerator, '_add_pdf_table_content') # Assume a new method for adding tables
    def test_single_column_with_exact_table_occurrence(
        self, mock_add_pdf_table_content, mock_determine_count,
        mock_add_pdf_chapter_content, mock_simple_doc_template_class, mock_ensure_output_dirs
    ):
        """Test 'pdf_tables_occurrence_config' (exact int) within 'single_column_text'."""
        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        exact_table_count = 1
        # Expected calls to _determine_count:
        # 1. page_count_config
        # 2. chapters_config
        # 3. table_generation.pdf_tables_occurrence_config (within chapter loop, or document level)
        # For simplicity, assume tables are document-level for now, or tested per chapter.
        # Let's assume for this test, tables are added after chapters.
        def determine_count_side_effect(config_value, context_key):
            if context_key == "page_count":
                return 10
            elif context_key == "chapters":
                return 1
            elif context_key.startswith("sections_chap_"):
                return 0
            elif context_key.startswith("notes_chap_"):
                return 0
            elif context_key.startswith("images_chap_"):
                return 0
            elif context_key == "tables":
                return exact_table_count
            return 0 # Default for any other unexpected calls
        mock_determine_count.side_effect = determine_count_side_effect

        specific_config = {
            "title": "PDF Single Column with Table",
            "pdf_variant": "single_column_text",
            "page_count_config": 10,
            "chapters_config": 1,
            "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "table_generation": {
                "pdf_tables_occurrence_config": exact_table_count,
                # other table settings...
            },
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right":25}},
            "running_header": {"enable": False},
            "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/pdf_single_column_with_table.pdf"

        self.generator.generate(specific_config, global_config, output_path)

        # Check that _determine_count was called for tables
        table_occurrence_config = specific_config["table_generation"]["pdf_tables_occurrence_config"]
        self.assertIn(
            call(table_occurrence_config, "tables"), # Assuming "tables" as context_key
            mock_determine_count.call_args_list
        )
        # Check that our assumed table adding method was called correctly
        self.assertEqual(mock_add_pdf_table_content.call_count, exact_table_count)
        mock_simple_doc_template_class.assert_called_once()
        mock_doc_instance.build.assert_called_once()

    @patch('synth_data_gen.generators.pdf.ensure_output_directories')
    @patch('synth_data_gen.generators.pdf.SimpleDocTemplate')
    @patch.object(PdfGenerator, '_add_pdf_chapter_content')
    @patch.object(PdfGenerator, '_add_pdf_table_content') # Keep this if tables can also be present
    @patch.object(PdfGenerator, '_determine_count')
    @patch.object(PdfGenerator, '_add_pdf_figure_content') # Assume a new method for adding figures
    def test_single_column_with_exact_figure_occurrence(
        self, mock_add_pdf_figure_content, mock_determine_count,
        mock_add_pdf_table_content, mock_add_pdf_chapter_content,
        mock_simple_doc_template_class, mock_ensure_output_dirs
    ):
        """Test 'pdf_figures_occurrence_config' (exact int) within 'single_column_text'."""
        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        exact_figure_count = 1
        
        def determine_count_side_effect(config_value, context_key):
            if context_key == "page_count": return 10
            elif context_key == "chapters": return 1
            elif context_key.startswith("sections_chap_"): return 0
            elif context_key.startswith("notes_chap_"): return 0
            elif context_key.startswith("images_chap_"): return 0 # This is for general images, not figures from figure_generation
            elif context_key == "tables": return 0 # Assume no tables for this specific test
            elif context_key == "figures": return exact_figure_count
            return 0
        mock_determine_count.side_effect = determine_count_side_effect

        specific_config = {
            "title": "PDF Single Column with Figure",
            "pdf_variant": "single_column_text",
            "page_count_config": 10,
            "chapters_config": 1,
            "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0}, # General images
            "table_generation": {"pdf_tables_occurrence_config": 0}, # No tables
            "figure_generation": { # New section for figures
                "pdf_figures_occurrence_config": exact_figure_count,
                # other figure settings...
            },
            "layout": {"columns": 1, "margins_mm": {"top":20, "bottom":20, "left":25, "right":25}},
            "running_header": {"enable": False},
            "running_footer": {"enable": False},
            "page_numbering": {"enable": False},
            "paragraph_styling": {"font_name": "Helvetica", "font_size": 12, "leading": 14}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/pdf_single_column_with_figure.pdf"

        self.generator.generate(specific_config, global_config, output_path)

        figure_occurrence_config = specific_config["figure_generation"]["pdf_figures_occurrence_config"]
        self.assertIn(
            call(figure_occurrence_config, "figures"), # Assuming "figures" as context_key
            mock_determine_count.call_args_list
        )
        self.assertEqual(mock_add_pdf_figure_content.call_count, exact_figure_count)
        mock_simple_doc_template_class.assert_called_once()
        mock_doc_instance.build.assert_called_once()

if __name__ == '__main__':
    unittest.main()