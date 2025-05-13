import os
import unittest
from ebooklib import epub

from synth_data_gen.generators.epub_components import headers
from synth_data_gen.common.utils import EPUB_DIR

class TestEpubHeaders(unittest.TestCase):

    def setUp(self):
        os.makedirs(os.path.join(EPUB_DIR, "headers"), exist_ok=True)

    def tearDown(self):
        files_to_remove = [
            os.path.join(EPUB_DIR, "headers", "taylor_hegel_headers.epub"),
            os.path.join(EPUB_DIR, "headers", "sennet_style_headers.epub"),
            os.path.join(EPUB_DIR, "headers", "div_style_headers.epub"),
            os.path.join(EPUB_DIR, "headers", "header_mixed_content.epub"),
            os.path.join(EPUB_DIR, "headers", "header_rosenzweig_hegel.epub"),
            os.path.join(EPUB_DIR, "headers", "header_derrida_gift_death.epub"),
            os.path.join(EPUB_DIR, "headers", "header_bch_p_strong.epub"),
            os.path.join(EPUB_DIR, "headers", "header_derrida_specters_p.epub"),
            os.path.join(EPUB_DIR, "headers", "header_kaplan_div.epub"),
            os.path.join(EPUB_DIR, "headers", "header_foucault_style.epub"),
            os.path.join(EPUB_DIR, "headers", "header_descartes_dict_p.epub"),
            os.path.join(EPUB_DIR, "headers", "p_tag_headers.epub"),
            os.path.join(EPUB_DIR, "headers", "headers_edition_markers.epub"),
        ]
        for f_path in files_to_remove:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_create_epub_taylor_hegel_headers_creates_file(self):
        filename = "taylor_hegel_headers.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_taylor_hegel_headers(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_taylor_hegel_headers_content(self):
        filename = "taylor_hegel_headers.epub"
        headers.create_epub_taylor_hegel_headers(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/taylor_h.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "h3.h1 span.small" in style_item_content and \
                   "h3.h3a em" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Taylor/Hegel specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "chap_taylor_1.xhtml":
                html_content = item.get_content().decode('utf-8')
                if '<h3 class="h1" id="ch1_num"><span class="small">CHAPTER I</span></h3>' in html_content and \
                   '<h3 class="h3a" id="ch1_title"><em>The Aim of the Enterprise</em></h3>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Taylor/Hegel header example content not found.")

    def test_create_epub_sennet_style_headers_creates_file(self):
        filename = "sennet_style_headers.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_sennet_style_headers(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_sennet_style_headers_content(self):
        filename = "sennet_style_headers.epub"
        headers.create_epub_sennet_style_headers(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/sennet_h.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "h1.title" in style_item_content and \
                   "h3.title5" in style_item_content and \
                   "h2.title6" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Sennet-specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "part_sennet_1.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<h1 class="title" id="part1">' in html_content and \
                   '<h3 class="title5" id="ch1_num_sennet">CHAPTER ONE</h3>' in html_content and \
                   '<h2 class="title6" id="ch1_title_sennet">The Troubled Craftsman</h2>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Sennet header example content not found.")

    def test_create_epub_div_style_headers_creates_file(self):
        filename = "div_style_headers.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_div_style_headers(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_div_style_headers_content(self):
        filename = "div_style_headers.epub"
        headers.create_epub_div_style_headers(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/div_h.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if ".title-chapter span.b" in style_item_content and \
                   ".subtitle-chapter span.i" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Div-style header CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "chap_div_h1.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<div class="title-chapter" id="main_title_div"><span class="b">THE QUESTION OF BEING</span></div>' in html_content and \
                   '<div class="subtitle-chapter" id="sub_title_div"><span class="i">An Ontological Inquiry</span></div>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Div-style header example content not found.")

    def test_create_epub_header_mixed_content_creates_file(self):
        filename = "header_mixed_content.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_header_mixed_content(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_header_mixed_content_content(self):
        filename = "header_mixed_content.epub"
        headers.create_epub_header_mixed_content(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/header_mix.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "h1 small" in style_item_content and \
                   "h2 small" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Mixed content header CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_mixhead.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<h1 id="ch1">The Grand Philosophical Journey <small>An Introduction</small></h1>' in html_content and \
                   '<h2 id="sec1_1_mix">First Section <small>(Preliminary Remarks)</small></h2>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Mixed content header example content not found.")

    def test_create_epub_header_rosenzweig_hegel_creates_file(self):
        filename = "header_rosenzweig_hegel.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_header_rosenzweig_hegel(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_header_rosenzweig_hegel_content(self):
        filename = "header_rosenzweig_hegel.epub"
        headers.create_epub_header_rosenzweig_hegel(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/header_rosen.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "h1.chapter span.cn span.bor" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Rosenzweig/Hegel specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_rosen.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<h1 class="chapter" id="c1_rosen">The Dialectic of the State <span class="cn"><span class="bor">I</span></span></h1>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Rosenzweig/Hegel header example content not found.")

    def test_create_epub_header_derrida_gift_death_creates_file(self):
        filename = "header_derrida_gift_death.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_header_derrida_gift_death(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_header_derrida_gift_death_content(self):
        filename = "header_derrida_gift_death.epub"
        headers.create_epub_header_derrida_gift_death(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/header_derrida_gd.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "h3.chapnum-derrida-gd" in style_item_content and \
                   "h2.chaptitle-derrida-gd" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Derrida Gift of Death specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_derrida_gd.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<h3 class="chapnum-derrida-gd" id="c1_num_gd">ONE</h3>' in html_content and \
                   '<h2 class="chaptitle-derrida-gd" id="c1_title_gd">Secrets of European Responsibility</h2>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Derrida Gift of Death header example content not found.")

    def test_create_epub_header_bch_p_strong_creates_file(self):
        filename = "header_bch_p_strong.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_header_bch_p_strong(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_header_bch_p_strong_content(self):
        filename = "header_bch_p_strong.epub"
        headers.create_epub_header_bch_p_strong(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/header_bch.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "p.c9-bch strong.calibre3-bch" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Byung-Chul Han specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_bch.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<p class="c9-bch" id="bch_title1"><strong class="calibre3-bch">THE BURNOUT SOCIETY</strong></p>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Byung-Chul Han header example content not found.")

    def test_create_epub_header_derrida_specters_p_creates_file(self):
        filename = "header_derrida_specters_p.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_header_derrida_specters_p(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_header_derrida_specters_p_content(self):
        filename = "header_derrida_specters_p.epub"
        headers.create_epub_header_derrida_specters_p(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/header_derrida_sp.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "p.chapter-number_1-sp" in style_item_content and \
                   "p.chapter-title_2-sp" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Derrida Specters specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_derrida_sp.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<p class="chapter-number_1-sp" id="c1_num_sp"><a href="#c1_num_sp"><b>1</b></a></p>' in html_content and \
                   '<p class="chapter-title_2-sp" id="c1_title_sp"><a href="#c1_title_sp"><b>Injunctions of Marx</b></a></p>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Derrida Specters header example content not found.")

    def test_create_epub_header_kaplan_div_creates_file(self):
        filename = "header_kaplan_div.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_header_kaplan_div(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_header_kaplan_div_content(self):
        filename = "header_kaplan_div.epub"
        headers.create_epub_header_kaplan_div(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/header_kaplan.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "div.chapter-number-kaplan" in style_item_content and \
                   "div.chapter-title-kaplan" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Kaplan specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "c1_kaplan.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<div class="chapter-number-kaplan" id="c1_num_kaplan">ONE</div>' in html_content and \
                   '<div class="chapter-title-kaplan" id="c1_title_kaplan">The End of Oslow</div>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Kaplan header example content not found.")

    def test_create_epub_header_foucault_style_creates_file(self):
        filename = "header_foucault_style.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_header_foucault_style(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_header_foucault_style_content(self):
        filename = "header_foucault_style.epub"
        headers.create_epub_header_foucault_style(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/foucault_h.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "h1.foucault-header" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Foucault specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "chap_foucault_1.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<h1 class="foucault-header"><a id="p23"/>1<br/>________________<br/>THE UNITIES OF DISCOURSE</h1>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Foucault header example content not found.")

    def test_create_epub_header_descartes_dict_p_creates_file(self):
        filename = "header_descartes_dict_p.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_header_descartes_dict_p(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_header_descartes_dict_p_content(self):
        filename = "header_descartes_dict_p.epub"
        headers.create_epub_header_descartes_dict_p(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/header_descartes_dict.css" and item.media_type == "text/css":
                style_item_content = item.get_content().decode('utf-8')
                if "p.ChapTitle-dd" in style_item_content and \
                   "p.AHead-dd" in style_item_content and \
                   "p.BHead-dd" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"Descartes Dictionary specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "entry_mind_dd.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<p class="ChapTitle-dd" id="title_mind"><a href="#title_mind">MIND (Mens)</a></p>' in html_content and \
                   '<p class="AHead-dd" id="ahead_substance"><strong>Mind as Substance</strong></p>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "Descartes Dictionary header example content not found.")

    def test_create_epub_p_tag_headers_creates_file(self):
        filename = "p_tag_headers.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_p_tag_headers(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_p_tag_headers_content(self):
        filename = "p_tag_headers.epub"
        headers.create_epub_p_tag_headers(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for CSS style
        css_found = False
        style_item_content = None
        for item in book.get_items():
            if item.file_name == "style/main.css" and item.media_type == "text/css": # As per SUT
                style_item_content = item.get_content().decode('utf-8')
                if "p.h1-style" in style_item_content and \
                   "p.h2-style" in style_item_content and \
                   "p.h3-style" in style_item_content:
                    css_found = True
                break
        self.assertTrue(css_found, f"P-tag header specific CSS not found. Style item content: '{style_item_content}'")

        # Check for example header content
        content_found = False
        for item in book.get_items():
            if item.get_name() == "chap_01_p_headers.xhtml": # As per SUT
                html_content = item.get_content().decode('utf-8')
                if '<p class="h1-style">Chapter 1: The Illusion of Structure</p>' in html_content and \
                   '<p class="h2-style">Section 1.1: Semantic Ambiguity</p>' in html_content:
                    content_found = True
                break
        self.assertTrue(content_found, "P-tag header example content not found.")

    def test_create_epub_headers_with_edition_markers_creates_file(self):
        filename = "headers_edition_markers.epub"
        expected_filepath = os.path.join(EPUB_DIR, "headers", filename)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        headers.create_epub_headers_with_edition_markers(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_headers_with_edition_markers_content(self):
        filename = "headers_edition_markers.epub"
        headers.create_epub_headers_with_edition_markers(filename=filename)
        filepath = os.path.join(EPUB_DIR, "headers", filename)
        book = epub.read_epub(filepath)

        # Check for example header content
        content_found_kant_a = False
        content_found_kant_b = False
        
        chapter_a_name = "kant_a_section.xhtml"
        chapter_b_name = "kant_b_section.xhtml"

        for item in book.get_items(): # Iterate all items
            if not isinstance(item, epub.EpubHtml): # Skip non-HTML items
                continue

            html_content = item.get_content().decode('utf-8')
            # Use item.file_name for matching as it's more reliable for chapter files
            if item.file_name == chapter_a_name:
                # More robust checks, less sensitive to exact HTML attributes generated by ebooklib
                self.assertIn('id="a1"', html_content, f"ID a1 not found in {chapter_a_name}")
                self.assertIn("The Transcendental Aesthetic [A 19 / B 33]", html_content, f"H1 text not found in {chapter_a_name}")
                
                self.assertIn('id="a1_sec1"', html_content, f"ID a1_sec1 not found in {chapter_a_name}")
                self.assertIn("Section I: Of Space [A 22 / B 37]", html_content, f"H2 text not found in {chapter_a_name}")
                
                self.assertIn("Some text about space... [A 23 / B 38]", html_content, f"P text not found in {chapter_a_name}")
                content_found_kant_a = True # If all asserts pass, content is found

            elif item.file_name == chapter_b_name:
                # More robust checks for B edition
                self.assertIn('id="b1"', html_content, f"ID b1 not found in {chapter_b_name}")
                self.assertIn("The Transcendental Aesthetic [B 33 / A 19] - Revised", html_content, f"H1 text not found in {chapter_b_name}")

                self.assertIn('id="b1_sec1"', html_content, f"ID b1_sec1 not found in {chapter_b_name}")
                self.assertIn("Section I: Of Space (Revised) [B 37 / A 22]", html_content, f"H2 text not found in {chapter_b_name}")
                
                self.assertIn("Some B edition text about space... [B 38 / A 23]", html_content, f"P text not found in {chapter_b_name}")
                content_found_kant_b = True # If all asserts pass, content is found
    
        # Ensure both chapters were found and processed
        self.assertTrue(content_found_kant_a, f"Kant A chapter ({chapter_a_name}) was not processed or assertions failed.")
        self.assertTrue(content_found_kant_b, f"Kant B chapter ({chapter_b_name}) was not processed or assertions failed.")

if __name__ == '__main__':
    unittest.main()