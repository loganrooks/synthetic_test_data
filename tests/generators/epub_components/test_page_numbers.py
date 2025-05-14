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
        page_numbers.create_epub_pagenum_kant_anchor(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_pagenum_kant_anchor_content(self):
        filename = "pagenum_kant_anchor.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        page_numbers.create_epub_pagenum_kant_anchor(filename=filename)
        book = epub.read_epub(expected_filepath)

        css_item = book.get_item_with_href('style/pgnum_kant_anchor.css')
        self.assertIsNotNone(css_item, "CSS file 'style/pgnum_kant_anchor.css' not found.")
        css_content = css_item.get_content().decode('utf-8')
        self.assertIn("a.calibre10-kantpage", css_content)

        chapter_item = book.get_item_with_id("c1_kant_pgnum_anchor")
        
        self.assertIsNotNone(chapter_item, "Chapter item with UID 'c1_kant_pgnum_anchor' not found.")
        html_content = chapter_item.get_content().decode('utf-8')
        self.assertIn('<a id="page_A25" class="calibre10-kantpage"/>', html_content)
        self.assertIn('<a id="page_B40" class="calibre10-kantpage"/>', html_content)

    # Add initial failing tests here based on functions in page_numbers.py
    def test_create_epub_pagenum_taylor_anchor_creates_file(self):
        filename = "pagenum_taylor_anchor.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        page_numbers.create_epub_pagenum_taylor_anchor(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_pagenum_taylor_anchor_content(self):
        filename = "pagenum_taylor_anchor.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        page_numbers.create_epub_pagenum_taylor_anchor(filename=filename)
        book = epub.read_epub(expected_filepath)

        css_item = book.get_item_with_href('style/pgnum_taylor_anchor.css')
        self.assertIsNotNone(css_item, "CSS file 'style/pgnum_taylor_anchor.css' not found.")
        css_content = css_item.get_content().decode('utf-8')
        self.assertIn("a.calibre3-taylorpage", css_content)

        chapter_item = book.get_item_with_id("c1_taylor_pgnum_anchor") # Assuming UID based on SUT
        self.assertIsNotNone(chapter_item, "Chapter item with UID 'c1_taylor_pgnum_anchor' not found.")
        html_content = chapter_item.get_content().decode('utf-8')
        self.assertIn('<a id="page_123" class="calibre3-taylorpage"/>', html_content)
        self.assertIn('<a id="page_124" class="calibre3-taylorpage"/>', html_content)
    def test_create_epub_pagenum_deleuze_plain_text_creates_file(self):
        filename = "pagenum_deleuze_plain_text.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        page_numbers.create_epub_pagenum_deleuze_plain_text(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_pagenum_deleuze_plain_text_content(self):
        filename = "pagenum_deleuze_plain_text.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        page_numbers.create_epub_pagenum_deleuze_plain_text(filename=filename)
        book = epub.read_epub(expected_filepath)

        css_item = book.get_item_with_href('style/pgnum_deleuze_plain.css')
        self.assertIsNotNone(css_item, "CSS file 'style/pgnum_deleuze_plain.css' not found.")
        # css_content = css_item.get_content().decode('utf-8') # Basic CSS, no specific check needed

        chapter_item = book.get_item_with_id("c1_deleuze_pgnum_plain") # Assuming UID
        self.assertIsNotNone(chapter_item, "Chapter item with UID 'c1_deleuze_pgnum_plain' not found.")
        html_content = chapter_item.get_content().decode('utf-8')
        self.assertIn("This is detailed further as the argument unfolds. xl The schizoanalytic project", html_content)
        self.assertIn("Consider the body without organs (BwO) as a surface for these processes. xli \nIt is not a pre-existing entity but a limit that is continually approached and repelled.", html_content)
        self.assertIn("This text simulates page numbers like \"xlii\" or \"45\" appearing directly in the text flow", html_content)

if __name__ == '__main__':
    unittest.main()