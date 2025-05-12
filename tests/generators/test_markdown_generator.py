import unittest
from synth_data_gen.generators.markdown import MarkdownGenerator

class TestMarkdownGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = MarkdownGenerator()

    def test_get_default_specific_config(self):
        """Test that get_default_specific_config for Markdown returns the expected structure."""
        defaults = self.generator.get_default_specific_config()
        
        self.assertIsInstance(defaults, dict)
        
        # Check for some key top-level default settings
        self.assertIn("headings_config", defaults)
        self.assertEqual(defaults["headings_config"], 5)
        self.assertIn("include_lists", defaults)
        self.assertTrue(defaults["include_lists"])
        self.assertIn("md_variant", defaults)
        self.assertEqual(defaults["md_variant"], "basic_elements")

        # Check for nested structures
        self.assertIn("gfm_features", defaults)
        self.assertIsInstance(defaults["gfm_features"], dict)
        self.assertIn("include_code_blocks", defaults["gfm_features"])
        self.assertTrue(defaults["gfm_features"]["include_code_blocks"])

        self.assertIn("frontmatter", defaults)
        self.assertIsInstance(defaults["frontmatter"], dict)
        self.assertIn("style", defaults["frontmatter"])
        self.assertEqual(defaults["frontmatter"]["style"], "yaml")
        self.assertIn("fields", defaults["frontmatter"])
        self.assertIsInstance(defaults["frontmatter"]["fields"], dict)
        self.assertTrue(defaults["frontmatter"]["fields"]["title"])

    def test_validate_config_valid(self):
        """Test validate_config with valid specific and global configs for Markdown."""
        specific_config = self.generator.get_default_specific_config()
        global_config = {"default_author": "Global Author"}
        self.assertTrue(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_missing_md_variant(self):
        """Test validate_config when md_variant is missing (should still pass due to current implementation)."""
        # Current MarkdownGenerator.validate_config only prints a warning
        specific_config = self.generator.get_default_specific_config()
        del specific_config["md_variant"]
        global_config = {"default_author": "Global Author"}
        self.assertTrue(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_invalid_base_specific_config(self):
        """Test validate_config when the specific_config is not a dict (handled by super)."""
        specific_config = "not_a_dict"
        global_config = {"default_author": "Global Author"}
        self.assertFalse(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_invalid_base_global_config(self):
        """Test validate_config when the global_config is not a dict (handled by super)."""
        specific_config = self.generator.get_default_specific_config()
        global_config = "not_a_dict"
        self.assertFalse(self.generator.validate_config(specific_config, global_config))

    @unittest.mock.patch('synth_data_gen.generators.markdown.ensure_output_directories')
    @unittest.mock.patch.object(MarkdownGenerator, '_generate_frontmatter')
    @unittest.mock.patch.object(MarkdownGenerator, '_create_md_basic_elements_content')
    @unittest.mock.patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_generate_minimal_markdown_basic_elements(
        self, mock_open_file, mock_create_basic_content,
        mock_generate_frontmatter, mock_ensure_output_dirs
    ):
        """Test the basic flow of the generate method for a minimal Markdown file."""
        
        mock_generate_frontmatter.return_value = "---\ntitle: Test MD\n---\n\n"
        mock_create_basic_content.return_value = "# Hello World"

        specific_config = {
            "title": "Test MD", # Used by frontmatter
            "md_variant": "basic_elements"
        }
        global_config = {"default_author": "Global MD Author"}
        output_path = "test_output/minimal.md"
        expected_dir_to_ensure = "test_output"

        returned_path = self.generator.generate(specific_config, global_config, output_path)

        mock_ensure_output_dirs.assert_called_once_with(expected_dir_to_ensure)
        mock_generate_frontmatter.assert_called_once_with(specific_config, global_config)
        mock_create_basic_content.assert_called_once_with(specific_config, global_config)
        
        mock_open_file.assert_called_once_with(output_path, 'w', encoding='utf-8')
        
        # Check that the written content combines frontmatter and body
        # mock_open_file().write.assert_called_once_with("---\ntitle: Test MD\n---\n\n# Hello World")
        # For more robust check if multiple writes are possible:
        written_content = "".join(call_args[0][0] for call_args in mock_open_file().write.call_args_list)
        self.assertEqual(written_content, "---\ntitle: Test MD\n---\n\n# Hello World")

        self.assertEqual(returned_path, output_path)

if __name__ == '__main__':
    unittest.main()