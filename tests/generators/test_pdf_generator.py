import unittest
import os
from unittest.mock import patch, MagicMock, call
from synth_data_gen.generators.pdf import PdfGenerator

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
        # _determine_count will be called for chapters, then for sub-elements within each chapter.
        # For this test, we focus on the chapter count. Assume 0 for sub-elements.
        # The first call to _determine_count is for "chapters".
        mock_determine_count.side_effect = [
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
        mock_simple_doc_template_class, mock_ensure_output_dirs
    ):
        """Test 'chapters_config' (range object) for 'single_column_text' variant,
        ensuring BaseGenerator._determine_count uses random.randint."""
        mock_doc_instance = MagicMock()
        mock_simple_doc_template_class.return_value = mock_doc_instance
        
        chapters_range_config = {"min": 2, "max": 5}
        # The actual number of chapters determined by random.randint is not the primary focus
        # for this specific test, as long as random.randint is called correctly.
        # We must set a return_value for mock_base_randint because the subsequent logic
        # (e.g. looping num_chapters_to_generate times) depends on it being an integer.
        mock_base_randint.return_value = 3 # Value within the range {"min": 2, "max": 5}

        self.generator.config = {
            "output_directory_base": "test_output",
            "output_filename_base": "single_col_unified_range",
            "document_template_class": "synth_data_gen.document_templates.SimpleDocTemplate",
            "file_types": {
                "pdf": {
                    "variant": "single_column_text",
                    "chapters_config": chapters_range_config, # Use the range object
                    "sections_config": {"min": 0, "max": 0}, # No sections for this test
                    "paragraphs_config": {"min": 1, "max": 1},
                    "sentences_per_paragraph_config": {"min": 1, "max": 1},
                    "words_per_sentence_config": {"min": 1, "max": 1},
                    "page_layout": {
                        "page_width_mm": 210,
                        "page_height_mm": 297,
                        "left_margin_mm": 20,
                        "right_margin_mm": 20,
                        "top_margin_mm": 25,
                        "bottom_margin_mm": 25
                    },
                    "font_config": {
                        "font_name": "Helvetica",
                        "font_size_pt": 12,
                        "line_spacing_pt": 14
                    }
                }
            }
        }
        specific_config = self.generator.config["file_types"]["pdf"]
        global_config_for_gen = self.generator.config
        
        output_filename = self.generator.config.get("output_filename_base", "single_col_unified_range_test") + ".pdf"
        output_dir_base = self.generator.config.get("output_directory_base", "test_output_pdfs")
        final_output_path = os.path.join(output_dir_base, self.generator.GENERATOR_ID, output_filename)

        mock_base_randint.reset_mock() # Reset before the action we are testing
        self.generator.generate(specific_config, global_config_for_gen, final_output_path)

        # self.generator.generate(specific_config, global_config_for_gen, final_output_path) # Redundant call removed

        mock_base_randint.assert_called_once_with(chapters_range_config["min"], chapters_range_config["max"])
        # We expect _add_pdf_chapter_content to be called based on the outcome of random.randint
        # If mock_base_randint.return_value was set, we could assert call_count here.
        # For now, we just ensure it's called at least once if chapters are generated.
        # If min_chapters is > 0, it should be called.
        if chapters_range_config["min"] > 0:
            mock_add_pdf_chapter_content.assert_called()
        
        # Assert that _add_pdf_chapter_content was called the expected number of times
        # This relies on mock_base_randint.return_value which dictates num_chapters_to_generate
        expected_chapters_from_range = mock_base_randint.return_value
        self.assertEqual(mock_add_pdf_chapter_content.call_count, expected_chapters_from_range)

        # Further assertions could check the content passed to _add_pdf_chapter_content
        # or the number of times it was called if mock_base_randint.return_value was fixed.
                # The mock on `random.randint` will then be hit.
                # For subsequent calls to `_determine_count` (for sections, etc.), we can then
                # make it return 0.

                # Let's adjust the side_effect for mock_determine_count.
                # The first call (chapters) should use the actual method.
                # The subsequent calls (sections, notes, images for each chapter) should return 0.
                # This means the side_effect list needs to be constructed carefully.
                # The first element of the side_effect list will be used for the first call.
                # If we want the original method to run, we can't just put a value there.

                # The issue is that the test is trying to mock _determine_count AND random.randint
                # and verify calls to both, but the mock of _determine_count is preventing random.randint from being called.

                # Simplest fix for THIS test's failure:
                # The `BaseGenerator._determine_count` *does* call `random.randint`.
                # The test is failing because the `side_effect` for `mock_determine_count`
                # is PREVENTING the original `_determine_count` from running for the "chapters" call.
                # So, `random.randint` is never reached.
                # The `side_effect` should only control the calls for sub-elements.
                # For the main "chapters" call, we want the actual `_determine_count` to run,
                # which will then hit our `mock_randint`.

                # We need to allow the first call to `_determine_count` to go through to the original method.
                # The other calls (for sections, notes, images) should return 0.
                # This is hard to do with a simple list side_effect if the number of chapters is dynamic.

                # Let's assume the `_determine_count` method in `BaseGenerator` is correct.
                # The test should verify that `PdfGenerator` uses it correctly for `chapters_config`.
                # The `mock_randint.assert_called_with` is the crucial check here.
        # For sub-elements, their configs are 0, so original _determine_count will return 0.
        # This seems like the correct way.
        # mock_determine_count was not defined in this test method's scope.
        # The test already mocks random.randint called by the original _determine_count.
        # Removing this line as it causes a NameError.

        # The following block (lines 306-321 originally) was a duplicate test setup
        # and a second call to self.generator.generate(), causing mock_base_randint
        # to be called twice. This block is now removed to ensure the test
        # correctly verifies a single call to randint for the primary test setup.

        # Check if random.randint (from BaseGenerator's perspective) was called
        # This assertion now correctly applies to the single generate() call at line 234.
        mock_base_randint.assert_called_once_with(chapters_range_config["min"], chapters_range_config["max"])
        
        self.assertEqual(mock_add_pdf_chapter_content.call_count, expected_chapters_from_range)
        mock_simple_doc_template_class.assert_called_once()
        mock_doc_instance.build.assert_called_once()


if __name__ == '__main__':
    unittest.main()