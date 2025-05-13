import os
import unittest
from ebooklib import epub
import zipfile

from synth_data_gen.generators.epub_components import page_numbers
from synth_data_gen.common.utils import EPUB_DIR

class TestEpubPageNumbers(unittest.TestCase):

    def setUp(self):
        self.output_dir = os.path.join(EPUB_DIR, "page_numbers")
        os.makedirs(self.output_dir, exist_ok=True)
        self.files_to_remove = []

    def tearDown(self):
        for f_path in self.files_to_remove:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_create_epub_pagenum_semantic_pagebreak_creates_file(self):
        filename = "pagenum_semantic_pagebreak.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        page_numbers.create_epub_pagenum_semantic_pagebreak(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_pagenum_semantic_pagebreak_content(self):
        filename = "pagenum_semantic_pagebreak.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        page_numbers.create_epub_pagenum_semantic_pagebreak(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        # DEBUG: Print all item IDs
        chapter_item_uid = "chapter_semantic_pagebreaks" # UID set in SUT

        # Check for CSS
        css_item = book.get_item_with_href('style/pgnum_semantic.css')
        self.assertIsNotNone(css_item, "CSS file 'style/pgnum_semantic.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn("span[epub|type=\"pagebreak\"]", css_content)

        # Check for chapter content
        chapter_item = book.get_item_with_id(chapter_item_uid)
        self.assertIsNotNone(chapter_item, f"Chapter item with UID '{chapter_item_uid}' not found.")

        if chapter_item:
            self.assertIsInstance(chapter_item, epub.EpubHtml, "Chapter item is not an EpubHtml object.")
            html_content = chapter_item.get_content().decode('utf-8')
            # Check for semantic page break (epub:type) - more robust checks
            self.assertIn('epub:type="pagebreak"', html_content)
            self.assertIn('id="Page_12"', html_content)
            self.assertIn('aria-label="12"', html_content)
            self.assertIn('role="doc-pagebreak"', html_content)
            self.assertIn('id="Page_13"', html_content)
            self.assertIn('aria-label="13"', html_content)
        else: # Should not happen if assertIsNotNone passes, but as a fallback
            self.fail(f"Chapter item with UID '{chapter_item_uid}' was None, cannot check content.")
        
        # Verify NAV document is the default one and does not contain page-list
        nav_item = book.get_item_with_href('nav.xhtml') # Default nav file name
        self.assertIsNotNone(nav_item, "NAV document 'nav.xhtml' not found.")
        if nav_item:
            nav_content = nav_item.get_content().decode('utf-8')
            self.assertIn('<nav epub:type="page-list"', nav_content, "Default NAV should contain page-list if pagebreak elements exist.")
            self.assertIn('<a href="c1_pgnum_semantic.xhtml#Page_12">12</a>', nav_content) # Check for page-list item
            self.assertIn('<a href="c1_pgnum_semantic.xhtml#Page_13">13</a>', nav_content) # Check for page-list item
    def test_create_epub_pagenum_kant_anchor_creates_file(self):
        filename = "pagenum_kant_anchor.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        # page_numbers.create_epub_pagenum_kant_anchor(filename=filename) # RED
        self.assertTrue(False, "SUT not called yet, this test should fail.") # RED

    def test_create_epub_pagenum_kant_anchor_content(self):
        filename = "pagenum_kant_anchor.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        # page_numbers.create_epub_pagenum_kant_anchor(filename=filename) # RED
        # book = epub.read_epub(expected_filepath) # RED

        # css_item = book.get_item_with_href('style/pgnum_kant_anchor.css')
        # self.assertIsNotNone(css_item)
        # css_content = css_item.get_content().decode('utf-8')
        # self.assertIn("a.calibre10-kantpage", css_content)

        # chapter_item = book.get_item_with_id("c1_kant_pgnum_anchor") # Assuming UID is c1_kant_pgnum_anchor
        # self.assertIsNotNone(chapter_item)
        # html_content = chapter_item.get_content().decode('utf-8')
        # self.assertIn('<a id="page_A25" class="calibre10-kantpage"></a>', html_content)
        # self.assertIn('<a id="page_B40" class="calibre10-kantpage"></a>', html_content)
        self.assertTrue(False, "SUT not called yet, this test should fail.") # RED

    # Add initial failing tests here based on functions in page_numbers.py

if __name__ == '__main__':
    unittest.main()