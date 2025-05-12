import unittest
import os
from unittest.mock import patch, MagicMock, call
from ebooklib import epub

# Assuming toc.py is in synth_data_gen.generators.epub_components
from synth_data_gen.generators.epub_components import toc

class TestEpubTocComponents(unittest.TestCase):

    @patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    @patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    @patch('synth_data_gen.generators.epub_components.toc._create_epub_book')
    def test_create_epub_ncx_simple(self, mock_create_book, mock_add_chapters, mock_write_file):
        """Test that create_epub_ncx_simple constructs a book with a simple NCX ToC."""
        
        mock_book_instance = MagicMock(spec=epub.EpubBook)
        mock_create_book.return_value = mock_book_instance
        
        # Mock the return of _add_epub_chapters to simulate chapter objects
        mock_chapter1 = MagicMock(spec=epub.EpubHtml)
        mock_chapter1.file_name = "chap_01.xhtml"
        mock_chapter1.title = "Introduction"
        
        mock_chapter2 = MagicMock(spec=epub.EpubHtml)
        mock_chapter2.file_name = "chap_02.xhtml"
        mock_chapter2.title = "Further Thoughts"
        
        mock_add_chapters.return_value = [mock_chapter1, mock_chapter2]

        # Call the function to be tested
        toc.create_epub_ncx_simple(filename="test_ncx_simple.epub")

        # Assert _create_epub_book was called (details can be more specific if needed)
        mock_create_book.assert_called_once()
        
        # Assert _add_epub_chapters was called
        mock_add_chapters.assert_called_once()
        # self.assertEqual(mock_add_chapters.call_args[0][0], mock_book_instance) # Check book instance
        # self.assertIsInstance(mock_add_chapters.call_args[0][1], list) # Check chapter_details

        # Assert that book.toc was set correctly for a simple NCX
        expected_toc_links_data = [
            {"href": "chap_01.xhtml", "title": "Introduction", "uid": "intro"},
            {"href": "chap_02.xhtml", "title": "Further Thoughts", "uid": "thoughts"}
        ]
        
        # Check if mock_book_instance.toc was set and has the correct number of items
        self.assertIsNotNone(mock_book_instance.toc)
        self.assertEqual(len(mock_book_instance.toc), len(expected_toc_links_data))

        # Compare attributes of each Link object
        for i, actual_link in enumerate(mock_book_instance.toc):
            expected_link_data = expected_toc_links_data[i]
            self.assertIsInstance(actual_link, epub.Link)
            self.assertEqual(actual_link.href, expected_link_data["href"])
            self.assertEqual(actual_link.title, expected_link_data["title"])
            self.assertEqual(actual_link.uid, expected_link_data["uid"])
            
        # Assert that EpubNcx and EpubNav items were added
        # We need to check the arguments to add_item
        add_item_calls = mock_book_instance.add_item.call_args_list
        added_item_types = [type(args[0]) for args, kwargs in add_item_calls]
        
        self.assertIn(epub.EpubNcx, added_item_types)
        self.assertIn(epub.EpubNav, added_item_types) # create_epub_ncx_simple also adds EpubNav

        # Assert _write_epub_file was called
        mock_write_file.assert_called_once()
        # Check the filepath argument passed to _write_epub_file
        self.assertTrue(mock_write_file.call_args[0][1].endswith("toc/test_ncx_simple.epub"))

if __name__ == '__main__':
    unittest.main()