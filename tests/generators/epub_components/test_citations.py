import os
import unittest
from unittest.mock import patch, MagicMock
from ebooklib import epub # Reverted to original import

from synth_data_gen.generators.epub_components import citations
from synth_data_gen.common.utils import EPUB_DIR

class TestEpubCitations(unittest.TestCase):

    def setUp(self):
        # Ensure the output directory for EPUBs exists
        os.makedirs(os.path.join(EPUB_DIR, "citations_bibliography"), exist_ok=True)

    def tearDown(self):
        # Clean up created files
        files_to_remove = [
            os.path.join(EPUB_DIR, "citations_bibliography", "citation_kant_intext.epub"),
            os.path.join(EPUB_DIR, "citations_bibliography", "citation_taylor_intext_italic.epub"),
            os.path.join(EPUB_DIR, "citations_bibliography", "citation_rosenzweig_biblioref.epub"),
        ]
        for f_path in files_to_remove:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_create_epub_citation_kant_intext_creates_file(self):
        """
        Test that create_epub_citation_kant_intext creates an EPUB file.
        """
        filename = "citation_kant_intext.epub"
        expected_filepath = os.path.join(EPUB_DIR, "citations_bibliography", filename)
        
        # Ensure file doesn't exist before test
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
            
        citations.create_epub_citation_kant_intext(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_citation_kant_intext_content(self):
        """
        Test that create_epub_citation_kant_intext includes Kant-specific CSS and content.
        """
        filename = "citation_kant_intext.epub"
        citations.create_epub_citation_kant_intext(filename=filename)
        
        filepath = os.path.join(EPUB_DIR, "citations_bibliography", filename)
        book = epub.read_epub(filepath) # Use epub.read_epub
        
        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items(): # Iterate through all items
            if item.file_name == "style/cite_kant.css" and item.media_type == "text/css": # Corrected attribute access
                style_item_content = item.get_content().decode('utf-8')
                # print(f"DEBUG_FOUND_CSS_CONTENT: '{style_item_content}'") # Optional debug
                if ".kant-citation { font-style: italic; color: #444; }" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Kant-specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example citation in content
        content_found = False
        # ITEM_DOCUMENT is 2 in ebooklib.epub (or iterate all documents)
        # More robustly, find by expected file name for the chapter
        found_chapter_item = False
        for item in book.get_items():
            # print(f"DEBUG_ITEM_NAME: {item.get_name()}, type: {type(item)}") # Optional debug
            if item.get_name() == "c1_kant_cite.xhtml": # Check specific chapter file
                found_chapter_item = True
                content = item.get_content().decode('utf-8')
                if '<span class="kant-citation">(KrV, A 73 / B 98)</span>' in content:
                    content_found = True
                break
        self.assertTrue(found_chapter_item, "Chapter item 'c1_kant_cite.xhtml' not found in EPUB.")
        self.assertTrue(content_found, "Kant-specific citation example not found in content.")

    def test_create_epub_citation_taylor_intext_italic_creates_file(self):
        """
        Test that create_epub_citation_taylor_intext_italic creates an EPUB file.
        """
        filename = "citation_taylor_intext_italic.epub"
        expected_filepath = os.path.join(EPUB_DIR, "citations_bibliography", filename)
        
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
            
        citations.create_epub_citation_taylor_intext_italic(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_citation_taylor_intext_italic_content(self):
        """
        Test that create_epub_citation_taylor_intext_italic includes Taylor-specific CSS and content.
        """
        filename = "citation_taylor_intext_italic.epub"
        citations.create_epub_citation_taylor_intext_italic(filename=filename)
        
        filepath = os.path.join(EPUB_DIR, "citations_bibliography", filename)
        book = epub.read_epub(filepath)
        
        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/cite_taylor.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "em.calibre8-taylor { font-style: italic; }" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Taylor-specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example citation in content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_taylor_cite.xhtml":
                content = item.get_content().decode('utf-8')
                if 'Hegel’s <em class="calibre8-taylor">Phenomenology of Spirit</em>' in content:
                    content_found = True
                break
        self.assertTrue(content_found, "Taylor-specific citation example not found in content.")

    def test_create_epub_citation_rosenzweig_biblioref_creates_file(self):
        """
        Test that create_epub_citation_rosenzweig_biblioref creates an EPUB file.
        """
        filename = "citation_rosenzweig_biblioref.epub"
        expected_filepath = os.path.join(EPUB_DIR, "citations_bibliography", filename)
        
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
            
        citations.create_epub_citation_rosenzweig_biblioref(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_citation_rosenzweig_biblioref_content(self):
        """
        Test that create_epub_citation_rosenzweig_biblioref includes Rosenzweig-specific structures.
        """
        filename = "citation_rosenzweig_biblioref.epub"
        citations.create_epub_citation_rosenzweig_biblioref(filename=filename)
        
        filepath = os.path.join(EPUB_DIR, "citations_bibliography", filename)
        book = epub.read_epub(filepath)
        
        # Check for CSS style for biblioref
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/cite_rosen_bibref.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if 'a[epub|type="biblioref"]' in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Rosenzweig-specific CSS (biblioref) not found. Style item content: '{style_item_content}'")

        # Check for biblioref and biblioentry in main content and bibliography page
        biblioref_found_in_main = False
        biblioentry_found_in_bib = False
        backlink_found_in_bib = False
        bibliography_page_exists = False

        main_chap_filename = "c1_rosen_bibref.xhtml"
        bib_page_filename = "bibliography_rosen.xhtml"

        for item in book.get_items():
            item_name = item.get_name()
            if item_name == main_chap_filename:
                content = item.get_content().decode('utf-8')
                if 'epub:type="biblioref"' in content and 'href="bibliography_rosen.xhtml#hegel1802"' in content:
                    biblioref_found_in_main = True
            elif item_name == bib_page_filename:
                bibliography_page_exists = True
                content = item.get_content().decode('utf-8')
                if 'epub:type="biblioentry" id="hegel1802"' in content:
                    biblioentry_found_in_bib = True
                if 'epub:type="backlink" href="c1_rosen_bibref.xhtml#ref_hegel1802"' in content:
                    backlink_found_in_bib = True
        
        self.assertTrue(bibliography_page_exists, f"Bibliography page '{bib_page_filename}' not found.")
        self.assertTrue(biblioref_found_in_main, "epub:type=\"biblioref\" not found in main chapter.")
        self.assertTrue(biblioentry_found_in_bib, "epub:type=\"biblioentry\" not found in bibliography page.")
        self.assertTrue(backlink_found_in_bib, "epub:type=\"backlink\" not found in bibliography page.")

if __name__ == '__main__':
    unittest.main()