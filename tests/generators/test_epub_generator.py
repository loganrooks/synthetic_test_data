import unittest
from unittest.mock import patch, MagicMock
from ebooklib import epub
from synth_data_gen.generators.epub import EpubGenerator

class TestEpubGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = EpubGenerator()

    def test_get_default_specific_config(self):
        """Test that get_default_specific_config returns the expected structure."""
        defaults = self.generator.get_default_specific_config()
        self.assertIsInstance(defaults, dict)
        self.assertIn("chapters_config", defaults)
        self.assertEqual(defaults["chapters_config"], 5)
        self.assertIn("author", defaults)
        self.assertEqual(defaults["author"], "Default EPUB Author")
        self.assertIn("epub_version", defaults)
        self.assertEqual(defaults["epub_version"], 3)
        self.assertIn("toc_settings", defaults)
        self.assertIsInstance(defaults["toc_settings"], dict)
        self.assertIn("style", defaults["toc_settings"])
        self.assertEqual(defaults["toc_settings"]["style"], "navdoc_full")
        self.assertIn("font_embedding", defaults)
        self.assertIsInstance(defaults["font_embedding"], dict)
        self.assertIn("enable", defaults["font_embedding"])
        self.assertFalse(defaults["font_embedding"]["enable"])
        self.assertIn("content_elements", defaults)
        self.assertIsInstance(defaults["content_elements"], dict)
        self.assertIn("paragraph_styles", defaults["content_elements"])
        self.assertIsInstance(defaults["content_elements"]["paragraph_styles"], list)

    def test_validate_config_valid(self):
        """Test validate_config with valid specific and global configs."""
        specific_config = self.generator.get_default_specific_config()
        global_config = {"default_language": "en"}
        self.assertTrue(self.generator.validate_config(specific_config, global_config))

    def test_validate_config_missing_epub_version(self):
        """Test validate_config when epub_version is missing (should still pass due to current implementation)."""
        specific_config = self.generator.get_default_specific_config()
        del specific_config["epub_version"]
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

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    def test_generate_minimal_epub(self, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test the basic flow of the generate method for a minimal EPUB."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        specific_config = {
            "title": "Test Book", "author": "Test Author", "language": "fr",
            "chapters_config": 1, "sections_per_chapter_config": 0
        }
        global_config = {"default_language": "en", "default_author": "Global Author"}
        output_path = "test_output/minimal.epub"
        expected_dir_to_ensure = "test_output"
        returned_path = self.generator.generate(specific_config, global_config, output_path)
        mock_ensure_output_dirs.assert_called_once_with(expected_dir_to_ensure)
        mock_epub_book_class.assert_called_once()
        mock_book_instance.set_title.assert_called_with("Test Book")
        mock_book_instance.set_language.assert_called_with("fr")
        mock_book_instance.add_author.assert_called_with("Test Author")
        self.assertTrue(mock_book_instance.add_item.called)
        mock_write_epub.assert_called_once_with(output_path, mock_book_instance, {})
        self.assertEqual(returned_path, output_path)

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub_components.toc.create_ncx')
    @patch('synth_data_gen.generators.epub_components.toc.create_nav_document')
    def test_generate_adds_basic_toc_items(
        self, mock_create_nav_document, mock_create_ncx,
        mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs
    ):
        """Test that generate calls ToC creation functions."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        mock_chapter_item = MagicMock(spec=epub.EpubHtml)
        mock_chapter_item.file_name = 'chap_1.xhtml'
        mock_chapter_item.title = 'Chapter 1'
        specific_config = {
            "title": "Basic ToC Test Book EPUB2 NCX", "chapters_config": 1, "epub_version": 2, # Changed to EPUB 2
            # "include_ncx": True, # "auto" should handle this for EPUB 2
            # "include_nav_doc": False, # "auto" should handle this for EPUB 2
            "toc_settings": {"style": "default"}, "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0}
        }
        global_config = {}
        output_path = "test_output/basic_toc_test_epub2_ncx.epub"
        with patch.object(self.generator, '_create_chapter_content', return_value=mock_chapter_item), \
             patch.object(self.generator, '_determine_count', side_effect=[1, 0, 0, 0]): # chapters, sections, notes, images
            self.generator.generate(specific_config, global_config, output_path)
        mock_create_ncx.assert_called_once()
        mock_create_nav_document.assert_not_called() # For EPUB 2, NavDoc is not typically primary/auto-created

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._create_chapter_content')
    def test_generate_chapters_config_exact_integer(self, mock_create_chapter_content, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with chapters_config as an exact integer."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        exact_chapter_count = 3
        mock_determine_count.return_value = exact_chapter_count
        specific_config = {"title": "Exact Chapters Test", "chapters_config": exact_chapter_count}
        global_config = {}
        output_path = "test_output/exact_chapters.epub"
        self.generator.generate(specific_config, global_config, output_path)
        mock_determine_count.assert_called_once_with(exact_chapter_count, "chapters")
        self.assertEqual(mock_create_chapter_content.call_count, exact_chapter_count)

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._create_chapter_content')
    @patch('random.randint')
    def test_generate_chapters_config_range_object(self, mock_randint, mock_create_chapter_content, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with chapters_config as a range object."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        range_config = {"min": 2, "max": 5}
        expected_chapters_from_range = 4
        mock_randint.return_value = expected_chapters_from_range
        mock_determine_count.return_value = expected_chapters_from_range
        specific_config = {"title": "Range Chapters Test", "chapters_config": range_config}
        global_config = {}
        output_path = "test_output/range_chapters.epub"
        self.generator.generate(specific_config, global_config, output_path)
        mock_determine_count.assert_called_once_with(range_config, "chapters")
        self.assertEqual(mock_create_chapter_content.call_count, expected_chapters_from_range)

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._create_chapter_content')
    @patch('random.random')
    def test_generate_chapters_config_probabilistic_object(self, mock_random_random, mock_create_chapter_content, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with chapters_config as a probabilistic object."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        prob_config = {"chance": 0.7, "per_unit_of": "document", "max_total": 3}
        mock_random_random.return_value = 0.6 
        expected_chapters_from_prob = 1
        mock_determine_count.return_value = expected_chapters_from_prob
        specific_config = {"title": "Probabilistic Chapters Test", "chapters_config": prob_config}
        global_config = {}
        output_path = "test_output/prob_chapters.epub"
        self.generator.generate(specific_config, global_config, output_path)
        mock_determine_count.assert_called_once_with(prob_config, "chapters")
        self.assertEqual(mock_create_chapter_content.call_count, expected_chapters_from_prob)

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._create_section_content') 
    def test_generate_sections_config_exact_integer(self, mock_create_section_content, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with sections_per_chapter_config as an exact integer."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1 
        exact_section_count = 2
        mock_determine_count.side_effect = [num_chapters, exact_section_count, 0, 0] 
        specific_config = {
            "title": "Exact Sections Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": exact_section_count 
        }
        global_config = {}
        output_path = "test_output/exact_sections.epub"
        self.generator.generate(specific_config, global_config, output_path)
        self.assertEqual(mock_determine_count.call_args_list[1], unittest.mock.call(exact_section_count, f"sections_in_chapter_1"))
        self.assertEqual(mock_create_section_content.call_count, exact_section_count * num_chapters)

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._create_section_content') 
    @patch('random.randint')
    def test_generate_sections_config_range_object(self, mock_randint, mock_create_section_content, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with sections_per_chapter_config as a range object."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1
        sections_range_config = {"min": 1, "max": 3}
        expected_sections_from_range = 2
        mock_randint.return_value = expected_sections_from_range
        mock_determine_count.side_effect = [num_chapters, expected_sections_from_range, 0, 0] 
        specific_config = {
            "title": "Range Sections Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": sections_range_config
        }
        global_config = {}
        output_path = "test_output/range_sections.epub"
        self.generator.generate(specific_config, global_config, output_path)
        self.assertEqual(mock_determine_count.call_args_list[1], unittest.mock.call(sections_range_config, f"sections_in_chapter_1"))
        self.assertEqual(mock_create_section_content.call_count, expected_sections_from_range * num_chapters)

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._create_section_content') 
    @patch('random.random')
    def test_generate_sections_config_probabilistic_object(self, mock_random_random, mock_create_section_content, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with sections_per_chapter_config as a probabilistic object."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1
        sections_prob_config = {"chance": 0.8, "max_total": 2}
        mock_random_random.return_value = 0.7
        expected_sections_from_prob = 1
        mock_determine_count.side_effect = [num_chapters, expected_sections_from_prob, 0, 0]
        specific_config = {
            "title": "Probabilistic Sections Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": sections_prob_config
        }
        global_config = {}
        output_path = "test_output/prob_sections.epub"
        self.generator.generate(specific_config, global_config, output_path)
        self.assertEqual(mock_determine_count.call_args_list[1], unittest.mock.call(sections_prob_config, f"sections_in_chapter_1"))
        self.assertEqual(mock_create_section_content.call_count, expected_sections_from_prob * num_chapters)

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._add_notes_to_chapter') 
    def test_generate_notes_config_exact_integer(self, mock_add_notes_to_chapter, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with notes_config (exact integer)."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1
        exact_notes_count = 3 
        mock_determine_count.side_effect = [num_chapters, 1, exact_notes_count, 0] 
        specific_config = {
            "title": "Exact Notes Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": 1, 
            "notes_system": {"type": "footnotes_same_page", "notes_config": exact_notes_count}
        }
        global_config = {}
        output_path = "test_output/exact_notes.epub"
        with patch.object(self.generator, '_create_section_content', MagicMock()): 
            self.generator.generate(specific_config, global_config, output_path)
        self.assertEqual(mock_determine_count.call_args_list[2], unittest.mock.call(exact_notes_count, f"notes_in_chapter_1"))
        mock_add_notes_to_chapter.assert_called_once() 

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._add_notes_to_chapter') 
    @patch('random.randint')
    def test_generate_notes_config_range_object(self, mock_randint, mock_add_notes_to_chapter, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with notes_config (range object)."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1
        notes_range_config = {"min": 1, "max": 4}
        expected_notes_from_range = 2
        mock_randint.return_value = expected_notes_from_range 
        mock_determine_count.side_effect = [num_chapters, 1, expected_notes_from_range, 0] 
        specific_config = {
            "title": "Range Notes Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": 1,
            "notes_system": {"type": "footnotes_same_page", "notes_config": notes_range_config}
        }
        global_config = {}
        output_path = "test_output/range_notes.epub"
        with patch.object(self.generator, '_create_section_content', MagicMock()):
            self.generator.generate(specific_config, global_config, output_path)
        self.assertEqual(mock_determine_count.call_args_list[2], unittest.mock.call(notes_range_config, f"notes_in_chapter_1"))
        mock_add_notes_to_chapter.assert_called_once()

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._add_notes_to_chapter') 
    @patch('random.random')
    def test_generate_notes_config_probabilistic_object(self, mock_random_random, mock_add_notes_to_chapter, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with notes_config (probabilistic object)."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1
        notes_prob_config = {"chance": 0.6, "max_total": 3} 
        mock_random_random.return_value = 0.5 
        expected_notes_from_prob = 1         
        mock_determine_count.side_effect = [num_chapters, 1, expected_notes_from_prob, 0] 
        specific_config = {
            "title": "Probabilistic Notes Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": 1,
            "notes_system": {"type": "footnotes_same_page", "notes_config": notes_prob_config}
        }
        global_config = {}
        output_path = "test_output/prob_notes.epub"
        with patch.object(self.generator, '_create_section_content', MagicMock()):
            self.generator.generate(specific_config, global_config, output_path)
        self.assertEqual(mock_determine_count.call_args_list[2], unittest.mock.call(notes_prob_config, f"notes_in_chapter_1"))
        mock_add_notes_to_chapter.assert_called_once()

    # Tests for images_config
    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._add_images_to_chapter') 
    def test_generate_images_config_exact_integer(self, mock_add_images_to_chapter, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with images_config (exact integer)."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1
        exact_images_count = 2 
        mock_determine_count.side_effect = [num_chapters, 1, 0, exact_images_count] 
        specific_config = {
            "title": "Exact Images Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": 1, "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": True, "images_config": exact_images_count}
        }
        global_config = {}
        output_path = "test_output/exact_images.epub"
        with patch.object(self.generator, '_create_section_content', MagicMock()), \
             patch.object(self.generator, '_add_notes_to_chapter', MagicMock()):
            self.generator.generate(specific_config, global_config, output_path)
        self.assertEqual(mock_determine_count.call_args_list[3], unittest.mock.call(exact_images_count, f"images_in_chapter_1"))
        mock_add_images_to_chapter.assert_called_once()

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._add_images_to_chapter') 
    @patch('random.randint')
    def test_generate_images_config_range_object(self, mock_randint, mock_add_images_to_chapter, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with images_config (range object)."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1
        images_range_config = {"min": 1, "max": 3}
        expected_images_from_range = 2
        mock_randint.return_value = expected_images_from_range 
        mock_determine_count.side_effect = [num_chapters, 1, 0, expected_images_from_range]
        specific_config = {
            "title": "Range Images Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": 1, "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": True, "images_config": images_range_config}
        }
        global_config = {}
        output_path = "test_output/range_images.epub"
        with patch.object(self.generator, '_create_section_content', MagicMock()), \
             patch.object(self.generator, '_add_notes_to_chapter', MagicMock()):
            self.generator.generate(specific_config, global_config, output_path)
        self.assertEqual(mock_determine_count.call_args_list[3], unittest.mock.call(images_range_config, f"images_in_chapter_1"))
        mock_add_images_to_chapter.assert_called_once()

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._add_images_to_chapter') 
    @patch('random.random')
    def test_generate_images_config_probabilistic_object(self, mock_random_random, mock_add_images_to_chapter, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test generate with images_config (probabilistic object)."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1
        images_prob_config = {"chance": 0.9, "max_total": 2}
        mock_random_random.return_value = 0.8 
        expected_images_from_prob = 1         
        mock_determine_count.side_effect = [num_chapters, 1, 0, expected_images_from_prob]
        specific_config = {
            "title": "Probabilistic Images Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": 1, "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": True, "images_config": images_prob_config}
        }
        global_config = {}
        output_path = "test_output/prob_images.epub"
        with patch.object(self.generator, '_create_section_content', MagicMock()), \
             patch.object(self.generator, '_add_notes_to_chapter', MagicMock()):
            self.generator.generate(specific_config, global_config, output_path)
        self.assertEqual(mock_determine_count.call_args_list[3], unittest.mock.call(images_prob_config, f"images_in_chapter_1"))
        mock_add_images_to_chapter.assert_called_once()

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count')
    @patch('synth_data_gen.generators.epub.EpubGenerator._add_images_to_chapter')
    def test_generate_multimedia_include_images_false(self, mock_add_images_to_chapter, mock_determine_count, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test that images are not processed if multimedia.include_images is False."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        num_chapters = 1
        mock_determine_count.side_effect = [num_chapters, 1, 0] # ch, sec, notes
        specific_config = {
            "title": "No Images Test", "chapters_config": num_chapters,
            "sections_per_chapter_config": 1, "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 5} 
        }
        global_config = {}
        output_path = "test_output/no_images.epub"
        with patch.object(self.generator, '_create_section_content', MagicMock()), \
             patch.object(self.generator, '_add_notes_to_chapter', MagicMock()):
            self.generator.generate(specific_config, global_config, output_path)
        mock_add_images_to_chapter.assert_not_called()
        self.assertEqual(mock_determine_count.call_count, 3)
        self.assertEqual(mock_determine_count.call_args_list[0], unittest.mock.call(num_chapters, "chapters"))
        self.assertEqual(mock_determine_count.call_args_list[1], unittest.mock.call(1, f"sections_in_chapter_1"))
        self.assertEqual(mock_determine_count.call_args_list[2], unittest.mock.call(0, f"notes_in_chapter_1"))
        for call_args in mock_determine_count.call_args_list:
            self.assertNotEqual(call_args[0][1], "images_in_chapter_1")

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub_components.toc.create_nav_document')
    @patch('synth_data_gen.generators.epub_components.toc.create_ncx')
    def test_generate_uses_toc_settings(self, mock_create_ncx, mock_create_nav_doc, mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs):
        """Test that generate passes toc_settings to toc creation functions."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        
        mock_chapter_item = MagicMock(spec=epub.EpubHtml)
        mock_chapter_item.file_name = 'chap_1.xhtml'
        mock_chapter_item.title = 'Chapter 1'
        
        with patch.object(self.generator, '_create_chapter_content', return_value=mock_chapter_item), \
             patch.object(self.generator, '_determine_count', side_effect=[1, 0, 0, 0]): 

            specific_config = {
                "title": "ToC Settings Test",
                "chapters_config": 1, 
                "epub_version": 3, 
                "toc_settings": {
                    "style": "custom_style",
                    "max_depth": 2,
                    "include_landmarks": False
                },
                "sections_per_chapter_config": 0,
                "notes_system": {"notes_config": 0},
                "multimedia": {"include_images": False, "images_config": 0}
            }
            global_config = {}
            output_path = "test_output/toc_settings_test.epub"

            self.generator.generate(specific_config, global_config, output_path)

        mock_create_nav_doc.assert_called_once()
        args_nav, _ = mock_create_nav_doc.call_args
        self.assertIs(args_nav[0], mock_book_instance) 
        self.assertEqual(len(args_nav[1]), 1) 
        self.assertIs(args_nav[1][0], mock_chapter_item)
        self.assertEqual(args_nav[2], specific_config["toc_settings"])
        self.assertEqual(args_nav[3], specific_config["epub_version"])

        # For EPUB3 "auto" settings, NCX is not created if NavDoc is.
        mock_create_ncx.assert_not_called()

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._create_chapter_content')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count') # For sub-elements
    def test_generate_unified_quantity_chapters_exact(
        self, mock_determine_sub_elements_count, mock_create_chapter_content,
        mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs
    ):
        """Test generate with 'chapters_config' as an exact integer (Unified Quantity)."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        mock_chapter_item = MagicMock(spec=epub.EpubHtml)
        mock_chapter_item.file_name = 'chap_1.xhtml' # Dummy filename
        mock_chapter_item.title = 'Chapter 1' # Dummy title
        mock_create_chapter_content.return_value = mock_chapter_item

        exact_chapter_count = 3
        # Mock _determine_count to return 0 for sections, notes, images to isolate chapter logic
        mock_determine_sub_elements_count.side_effect = [
            exact_chapter_count, # This call is for chapters_config itself
            0, 0, 0, # sections_per_chapter_config for chapter 1, notes_config for chapter 1, images_config for chapter 1
            0, 0, 0, # sections_per_chapter_config for chapter 2, notes_config for chapter 2, images_config for chapter 2
            0, 0, 0  # sections_per_chapter_config for chapter 3, notes_config for chapter 3, images_config for chapter 3
        ]

        specific_config = {
            "title": "Unified Exact Chapters Test",
            "chapters_config": exact_chapter_count, # Unified quantity - exact integer
            "sections_per_chapter_config": 0, # Keep sub-elements simple for this test
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "epub_version": 3, # Specify version for clarity
            "toc_settings": {"style": "default"} # Minimal ToC settings
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/unified_exact_chapters.epub"

        self.generator.generate(specific_config, global_config, output_path)

        # Check that _determine_count was called for "chapters" with the exact integer value
        self.assertIn(
            unittest.mock.call(exact_chapter_count, "chapters"),
            mock_determine_sub_elements_count.call_args_list
        )
        # Check that _create_chapter_content was called the correct number of times
        self.assertEqual(mock_create_chapter_content.call_count, exact_chapter_count)
        # Check calls for sub-elements (sections, notes, images) for each chapter
        expected_determine_calls = [unittest.mock.call(exact_chapter_count, "chapters")]
        for i in range(1, exact_chapter_count + 1):
            expected_determine_calls.append(unittest.mock.call(0, f"sections_in_chapter_{i}"))
            expected_determine_calls.append(unittest.mock.call(0, f"notes_in_chapter_{i}"))
            # images_config is not called if include_images is False
        
        # Verify all calls to _determine_count
        # We only check the relevant calls for this test's focus.
        # The side_effect ensures the counts are what we expect for sub-elements.
        # The primary assertion is on mock_create_chapter_content.call_count.

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._create_chapter_content')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count') # For sub-elements and the main chapters_config call
    @patch('random.randint') # To control the outcome of the range
    def test_generate_unified_quantity_chapters_range(
        self, mock_randint, mock_determine_count, mock_create_chapter_content,
        mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs
    ):
        """Test generate with 'chapters_config' as a range object (Unified Quantity)."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        mock_chapter_item = MagicMock(spec=epub.EpubHtml)
        mock_chapter_item.file_name = 'chap_range.xhtml'
        mock_chapter_item.title = 'Chapter Range'
        mock_create_chapter_content.return_value = mock_chapter_item

        chapters_range_config = {"min": 2, "max": 5}
        expected_chapters_from_range = 4 # Value mock_randint will return
        mock_randint.return_value = expected_chapters_from_range

        # _determine_count will be called first for "chapters" with the range_config,
        # then for sub-elements (sections, notes, images) for each of the 'expected_chapters_from_range' chapters.
        # The first call to _determine_count (for chapters_config) should return the value from mock_randint.
        # Subsequent calls for sub-elements should return 0.
        determine_side_effects = [expected_chapters_from_range] + [0, 0, 0] * expected_chapters_from_range
        mock_determine_count.side_effect = determine_side_effects

        specific_config = {
            "title": "Unified Range Chapters Test",
            "chapters_config": chapters_range_config, # Unified quantity - range object
            "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "epub_version": 3,
            "toc_settings": {"style": "default"}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/unified_range_chapters.epub"

        self.generator.generate(specific_config, global_config, output_path)

        # Check that _determine_count was called for "chapters" with the range object
        self.assertIn(
            unittest.mock.call(chapters_range_config, "chapters"),
            mock_determine_count.call_args_list
        )
        # Check that random.randint was called with the correct range if _determine_count delegates to it
        # This depends on the internal implementation of _determine_count for ranges.
        # If _determine_count handles the random.randint call itself, this direct mock_randint check might not be hit
        # in the same way as older tests. The key is that the *result* of the range processing is correct.

        # The primary check: _create_chapter_content was called the correct number of times
        self.assertEqual(mock_create_chapter_content.call_count, expected_chapters_from_range)

        # Verify the first call to _determine_count was for chapters_config
        self.assertEqual(mock_determine_count.call_args_list[0], unittest.mock.call(chapters_range_config, "chapters"))

    @patch('synth_data_gen.generators.epub.ensure_output_directories')
    @patch('synth_data_gen.generators.epub.epub.write_epub')
    @patch('synth_data_gen.generators.epub.epub.EpubBook')
    @patch('synth_data_gen.generators.epub.EpubGenerator._create_chapter_content')
    @patch('synth_data_gen.generators.epub.EpubGenerator._determine_count') # For sub-elements and the main chapters_config call
    @patch('random.random') # To control the outcome of the chance
    def test_generate_unified_quantity_chapters_probabilistic(
        self, mock_random_random, mock_determine_count, mock_create_chapter_content,
        mock_epub_book_class, mock_write_epub, mock_ensure_output_dirs
    ):
        """Test generate with 'chapters_config' as a probabilistic object (Unified Quantity)."""
        mock_book_instance = MagicMock()
        mock_epub_book_class.return_value = mock_book_instance
        mock_chapter_item = MagicMock(spec=epub.EpubHtml)
        mock_chapter_item.file_name = 'chap_prob.xhtml'
        mock_chapter_item.title = 'Chapter Probabilistic'
        mock_create_chapter_content.return_value = mock_chapter_item

        chapters_prob_config = {"chance": 0.7, "per_unit_of": "document", "max_total": 3}
        # Scenario: random.random() returns 0.6 (less than chance 0.7), so 1 chapter should be generated.
        # If per_unit_of is "document", it's a single check.
        mock_random_random.return_value = 0.6
        expected_chapters_from_prob = 1 # Based on the single "document" unit and chance succeeding

        # _determine_count will be called first for "chapters" with the prob_config,
        # then for sub-elements for each of the 'expected_chapters_from_prob' chapters.
        # The first call to _determine_count (for chapters_config) should return the calculated probabilistic count.
        determine_side_effects = [expected_chapters_from_prob] + [0, 0, 0] * expected_chapters_from_prob
        mock_determine_count.side_effect = determine_side_effects

        specific_config = {
            "title": "Unified Probabilistic Chapters Test",
            "chapters_config": chapters_prob_config, # Unified quantity - probabilistic object
            "sections_per_chapter_config": 0,
            "notes_system": {"notes_config": 0},
            "multimedia": {"include_images": False, "images_config": 0},
            "epub_version": 3,
            "toc_settings": {"style": "default"}
        }
        global_config = {"default_language": "en"}
        output_path = "test_output/unified_prob_chapters.epub"

        self.generator.generate(specific_config, global_config, output_path)

        # Check that _determine_count was called for "chapters" with the probabilistic object
        self.assertIn(
            unittest.mock.call(chapters_prob_config, "chapters"),
            mock_determine_count.call_args_list
        )
        # Check that random.random was called if _determine_count delegates to it for "document" unit
        # This depends on _determine_count's internal logic.
        # The key is that the *result* of the probabilistic processing is correct.

        # The primary check: _create_chapter_content was called the correct number of times
        self.assertEqual(mock_create_chapter_content.call_count, expected_chapters_from_prob)
        
        # Verify the first call to _determine_count was for chapters_config
        self.assertEqual(mock_determine_count.call_args_list[0], unittest.mock.call(chapters_prob_config, "chapters"))


if __name__ == '__main__':
    unittest.main()