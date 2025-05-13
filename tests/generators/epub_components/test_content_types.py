import os
import unittest
from ebooklib import epub

from synth_data_gen.generators.epub_components import content_types
from synth_data_gen.common.utils import EPUB_DIR

class TestEpubContentTypes(unittest.TestCase):

    def setUp(self):
        os.makedirs(os.path.join(EPUB_DIR, "content_types"), exist_ok=True)

    def tearDown(self):
        files_to_remove = [
            os.path.join(EPUB_DIR, "content_types", "content_dialogue.epub"),
            os.path.join(EPUB_DIR, "content_types", "content_epigraph.epub"),
            os.path.join(EPUB_DIR, "content_types", "content_blockquote_styled.epub"),
            os.path.join(EPUB_DIR, "content_types", "content_internal_cross_refs.epub"),
            os.path.join(EPUB_DIR, "content_types", "content_forced_page_breaks.epub"),
            os.path.join(EPUB_DIR, "content_types", "poetry_formatting.epub"),
        ]
        for f_path in files_to_remove:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_create_epub_content_dialogue_creates_file(self):
        filename = "content_dialogue.epub"
        expected_filepath = os.path.join(EPUB_DIR, "content_types", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        content_types.create_epub_content_dialogue(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_content_dialogue_content(self):
        filename = "content_dialogue.epub"
        content_types.create_epub_content_dialogue(filename=filename)
        filepath = os.path.join(EPUB_DIR, "content_types", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/dialogue.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "p.speaker { font-weight: bold; margin-bottom: 0.2em; }" in style_item_content and \
                   "p.dialogue { margin-left: 2em; margin-bottom: 0.8em; }" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Dialogue-specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example dialogue content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_dialogue.xhtml":
                html_content = item.get_content().decode('utf-8')
                if '<p class="speaker">Alex:</p>' in html_content and \
                   '<p class="dialogue">The nature of consciousness, it seems to me, remains the most profound mystery.</p>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Dialogue example content not found.")

    def test_create_epub_content_epigraph_creates_file(self):
        filename = "content_epigraph.epub"
        expected_filepath = os.path.join(EPUB_DIR, "content_types", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        content_types.create_epub_content_epigraph(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_content_epigraph_content(self):
        filename = "content_epigraph.epub"
        content_types.create_epub_content_epigraph(filename=filename)
        filepath = os.path.join(EPUB_DIR, "content_types", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/epigraph.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "div.epigraph-pippin" in style_item_content and \
                   "p.epf-pippin" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Epigraph-specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example epigraph content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_epigraph.xhtml":
                html_content = item.get_content().decode('utf-8')
                if '<div class="epigraph-pippin">' in html_content and \
                   '<p class="epf-pippin">"The owl of Minerva spreads its wings only with the falling of the dusk."</p>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Epigraph example content not found.")

    def test_create_epub_content_blockquote_styled_creates_file(self):
        filename = "content_blockquote_styled.epub"
        expected_filepath = os.path.join(EPUB_DIR, "content_types", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        content_types.create_epub_content_blockquote_styled(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_content_blockquote_styled_content(self):
        filename = "content_blockquote_styled.epub"
        content_types.create_epub_content_blockquote_styled(filename=filename)
        filepath = os.path.join(EPUB_DIR, "content_types", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/blockquote.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "blockquote.calibre14-hegelsol" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Blockquote-specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example blockquote content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_blockquote.xhtml":
                html_content = item.get_content().decode('utf-8')
                if '<blockquote class="calibre14-hegelsol">' in html_content and \
                   "the starry heavens above me and the moral law within me." in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Blockquote example content not found.")

    def test_create_epub_content_internal_cross_refs_creates_file(self):
        filename = "content_internal_cross_refs.epub"
        expected_filepath = os.path.join(EPUB_DIR, "content_types", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        content_types.create_epub_content_internal_cross_refs(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_content_internal_cross_refs_content(self):
        filename = "content_internal_cross_refs.epub"
        content_types.create_epub_content_internal_cross_refs(filename=filename)
        filepath = os.path.join(EPUB_DIR, "content_types", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/xref.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "a.xref-pippin" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Cross-reference CSS not found. Style item content: '{style_item_content}'")

        # Check for cross-reference and target in content
        xref_found_in_c1 = False
        target_found_in_c2 = False
        c1_filename = "c1_xref.xhtml"
        c2_filename = "c2_xref.xhtml"

        for item in book.get_items():
            item_name = item.get_name()
            if item_name == c1_filename:
                html_content = item.get_content().decode('utf-8')
                if '<a class="xref-pippin" href="c2_xref.xhtml#target_section">' in html_content:
                    xref_found_in_c1 = True
            elif item_name == c2_filename:
                html_content = item.get_content().decode('utf-8')
                if 'id="target_section"' in html_content:
                    target_found_in_c2 = True
        
        self.assertTrue(xref_found_in_c1, "Cross-reference link not found in chapter 1.")
        self.assertTrue(target_found_in_c2, "Cross-reference target id not found in chapter 2.")

    def test_create_epub_content_forced_page_breaks_creates_file(self):
        filename = "content_forced_page_breaks.epub"
        expected_filepath = os.path.join(EPUB_DIR, "content_types", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        content_types.create_epub_content_forced_page_breaks(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_content_forced_page_breaks_content(self):
        filename = "content_forced_page_breaks.epub"
        content_types.create_epub_content_forced_page_breaks(filename=filename)
        filepath = os.path.join(EPUB_DIR, "content_types", filename)
        book = epub.read_epub(filepath)

        # Check for forced page break style in content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_forcebreak.xhtml":
                html_content = item.get_content().decode('utf-8')
                # Check for two instances of the page break style
                if html_content.count('style="page-break-before: always;"') >= 2:
                    content_found = True
                break
        self.assertTrue(content_found, "Forced page break style not found in content as expected.")

    def test_create_epub_poetry_creates_file(self):
        filename = "poetry_formatting.epub"
        expected_filepath = os.path.join(EPUB_DIR, "content_types", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        content_types.create_epub_poetry(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_poetry_content(self):
        filename = "poetry_formatting.epub"
        content_types.create_epub_poetry(filename=filename)
        filepath = os.path.join(EPUB_DIR, "content_types", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/poetry.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if ".poem {" in style_item_content and \
                   ".stanza {" in style_item_content and \
                   ".poemline {" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Poetry-specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example poetry content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "ode_synthetic.xhtml":
                html_content = item.get_content().decode('utf-8')
                if '<div class="poem">' in html_content and \
                   '<p class="poemline">Born of code, not feathered quill,</p>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Poetry example content not found.")

if __name__ == '__main__':
    unittest.main()