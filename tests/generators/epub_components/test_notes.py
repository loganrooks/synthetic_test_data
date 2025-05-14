import os
import unittest
from ebooklib import epub
import zipfile

from synth_data_gen.generators.epub_components import notes
from synth_data_gen.common.utils import EPUB_DIR

class TestEpubNotes(unittest.TestCase):

    def setUp(self):
        self.output_dir = os.path.join(EPUB_DIR, "notes")
        os.makedirs(self.output_dir, exist_ok=True)
        self.files_to_remove = []

    def tearDown(self):
        for f_path in self.files_to_remove:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_create_epub_footnote_hegel_sol_ref_creates_file(self):
        filename = "footnote_hegel_sol_ref.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_footnote_hegel_sol_ref(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_footnote_hegel_sol_ref_content(self):
        filename = "footnote_hegel_sol_ref.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_footnote_hegel_sol_ref(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        # Check for CSS
        css_item = book.get_item_with_href('style/fn_hegel_sol_ref.css')
        self.assertIsNotNone(css_item)
        css_content = css_item.get_content().decode('utf-8')
        self.assertIn("sup.calibre30-sol", css_content)
        self.assertIn(".fn-body-sol", css_content)

        # Check for chapter content
        chapter_found = False
        found_item_content = None
        # SUT for create_epub_footnote_hegel_sol_ref specifies "Text/c1_hegel_sol_fnref.xhtml"
        for item in book.get_items(): # Changed from get_items_of_type
            if isinstance(item, epub.EpubHtml) and item.file_name == "c1_hegel_sol_fnref.xhtml": # Check type here
                found_item_content = item.get_content().decode('utf-8')
                chapter_found = True
                break
        self.assertTrue(chapter_found, "Chapter item 'c1_hegel_sol_fnref.xhtml' not found.")
        if chapter_found and found_item_content:
            self.assertIn('<span><a id="textpos001"/><a href="#fnpos001"><sup class="calibre30-sol">1</sup></a></span>', found_item_content)
            self.assertIn('<div class="fn-body-sol" id="fnpos001">', found_item_content)
            self.assertIn('Hegel\'s discussion of Being (Sein) is foundational.', found_item_content)

    def test_create_epub_footnote_hegel_por_author_creates_file(self):
        filename = "footnote_hegel_por_author.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_footnote_hegel_por_author(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_footnote_hegel_por_author_content(self):
        filename = "footnote_hegel_por_author.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_footnote_hegel_por_author(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        # Check for CSS
        css_item = book.get_item_with_href('style/fn_hegel_por_author.css')
        self.assertIsNotNone(css_item, "CSS file 'style/fn_hegel_por_author.css' not found.")
        if css_item: 
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn("sup.calibre11-hpor", css_content)
            self.assertIn(".fn-author-hpor", css_content)

        # Check for chapter content
        chapter_found = False
        for item in book.get_items(): 
            if not isinstance(item, epub.EpubHtml): 
                continue
            if item.file_name == "c1_hegel_por_author_fn.xhtml":
                html_content = item.get_content().decode('utf-8')
                self.assertIn('<sup class="calibre11-hpor"><a id="ifn1" href="#fn1-author"><em class="calibre3-hpor">†</em></a></sup>', html_content)
                self.assertIn('<div class="fn-author-hpor" id="fn1-author">', html_content)
                self.assertIn("This is an author's own note", html_content)
                chapter_found = True
                break
        self.assertTrue(chapter_found, "Chapter content for Hegel PoR author footnotes not found.")

    def test_create_epub_footnote_marx_engels_reader_creates_file(self):
        filename = "footnote_marx_engels_reader.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_footnote_marx_engels_reader(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_footnote_marx_engels_reader_content(self):
        filename = "footnote_marx_engels_reader.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_footnote_marx_engels_reader(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/fn_marx_engels.css')
        self.assertIsNotNone(css_item, "CSS file 'style/fn_marx_engels.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn("a.calibre8-mer", css_content)
            self.assertIn("sup.calibre9-mer", css_content)
            self.assertIn(".endnote-section-mer", css_content)

        main_content_found = False
        notes_page_found = False
        main_chap_filename = "main_mer.xhtml"
        notes_page_filename = "notes_mer.xhtml"

        for item in book.get_items():
            if not isinstance(item, epub.EpubHtml):
                continue
            html_content = item.get_content().decode('utf-8')
            if item.file_name == main_chap_filename:
                self.assertIn('<h1>Critique of the Gotha Program</h1>', html_content)
                self.assertIn('<a id="footnote-ref01" href="notes_mer.xhtml#footnote01" class="calibre8-mer"><span><sup class="calibre9-mer">1</sup></span></a>', html_content)
                main_content_found = True
            elif item.file_name == notes_page_filename:
                self.assertIn('<h2>Notes</h2>', html_content)
                self.assertIn('<div class="endnote-item-mer" id="footnote01">', html_content)
                self.assertIn('This refers to the utopian socialists\' views on labor.', html_content)
                notes_page_found = True
        
        self.assertTrue(main_content_found, f"Main content file '{main_chap_filename}' not found or content incorrect.")
        self.assertTrue(notes_page_found, f"Notes page file '{notes_page_filename}' not found or content incorrect.")

    def test_create_epub_footnote_marcuse_dual_style_creates_file(self):
        filename = "footnote_marcuse_dual_style.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_footnote_marcuse_dual_style(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_footnote_marcuse_dual_style_content(self):
        filename = "footnote_marcuse_dual_style.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_footnote_marcuse_dual_style(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/fn_marcuse_dual.css')
        self.assertIsNotNone(css_item, "CSS file 'style/fn_marcuse_dual.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn("a.fn-marcuse-ast", css_content)
            self.assertIn("a.fn-marcuse-num sup", css_content)
            self.assertIn(".footnote-section-marcuse", css_content)

        chapter_found = False
        chap_filename = "c1_marcuse_dual_fn.xhtml"
        for item in book.get_items():
            if not isinstance(item, epub.EpubHtml):
                continue
            if item.file_name == chap_filename:
                html_content = item.get_content().decode('utf-8')
                self.assertIn('<a href="#fn-fnref_ast1" id="fn_ast1" class="fn-marcuse-ast">*</a>', html_content)
                self.assertIn('<p class="fn-marcuse"><a id="fn-fnref_ast1" href="#fn_ast1">*</a> Marcuse\'s original thesis', html_content)
                self.assertIn('<a href="#fn-fnref_num1" id="fn_num1" class="fn-marcuse-num"><sup>1</sup></a>', html_content)
                self.assertIn('<p class="fn-marcuse"><a id="fn-fnref_num1" href="#fn_num1">1.</a> See discussion on technological rationality.</p>', html_content)
                chapter_found = True
                break
        self.assertTrue(chapter_found, f"Chapter content for Marcuse dual style footnotes ('{chap_filename}') not found or content incorrect.")

    def test_create_epub_footnote_adorno_unlinked_creates_file(self):
        filename = "footnote_adorno_unlinked.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_footnote_adorno_unlinked(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_footnote_adorno_unlinked_content(self):
        filename = "footnote_adorno_unlinked.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_footnote_adorno_unlinked(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/fn_adorno_unlinked.css')
        self.assertIsNotNone(css_item, "CSS file 'style/fn_adorno_unlinked.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn("sup.calibre5-adorno", css_content)
            self.assertIn(".footnote-text-adorno", css_content)

        chapter_found = False
        chap_filename = "c1_adorno_unlinked_fn.xhtml"
        for item in book.get_items():
            if not isinstance(item, epub.EpubHtml):
                continue
            if item.file_name == chap_filename:
                html_content = item.get_content().decode('utf-8')
                self.assertIn('<sup class="calibre5-adorno"><small class="calibre6-adorno"><span class="calibre7-adorno">1</span></small></sup>', html_content)
                self.assertIn('<p class="footnote-text-adorno">1. This refers to Adorno\'s methodological approach.</p>', html_content)
                chapter_found = True
                break
        self.assertTrue(chapter_found, f"Chapter content for Adorno unlinked footnotes ('{chap_filename}') not found or content incorrect.")

    def test_create_epub_footnote_derrida_grammatology_dual_creates_files(self):
        filename = "footnote_derrida_grammatology_dual.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_footnote_derrida_grammatology_dual(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

        with zipfile.ZipFile(expected_filepath, 'r') as epub_zip:
            internal_files = epub_zip.namelist()
            self.assertIn("EPUB/Text/c1_grammatology.xhtml", internal_files)
            self.assertIn("EPUB/Text/fn_gram_c1_01.xhtml", internal_files)
            self.assertIn("EPUB/Text/fn_gram_c1_02.xhtml", internal_files)
            self.assertIn("EPUB/Text/notes_gram_consolidated.xhtml", internal_files)
            self.assertIn("EPUB/style/fn_derrida_gram.css", internal_files)

    def test_create_epub_footnote_derrida_grammatology_dual_content(self):
        filename = "footnote_derrida_grammatology_dual.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_footnote_derrida_grammatology_dual(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/fn_derrida_gram.css')
        self.assertIsNotNone(css_item, "CSS file 'style/fn_derrida_gram.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn("a.nounder-derrida", css_content)
            self.assertIn(".footnote-sep-file", css_content)

        main_chap_found = False
        fn1_page_found = False
        endnotes_page_found = False
        main_chap_filename = "Text/c1_grammatology.xhtml" 
        fn1_filename = "Text/fn_gram_c1_01.xhtml"
        endnotes_filename = "Text/notes_gram_consolidated.xhtml"

        for item in book.get_items():
            if not isinstance(item, epub.EpubHtml):
                continue
            html_content = item.get_content().decode('utf-8')
            if item.file_name == main_chap_filename:
                self.assertIn('<h1>The End of the Book and the Beginning of Writing</h1>', html_content)
                self.assertIn('<a class="nounder-derrida" href="../Text/fn_gram_c1_01.xhtml#fn_trace">*</a>', html_content)
                self.assertIn('<sup><a class="nounder-derrida" href="../Text/notes_gram_consolidated.xhtml#en_logo">1</a></sup>', html_content)
                main_chap_found = True
            elif item.file_name == fn1_filename:
                self.assertIn("<p class=\"footnote-sep-file\" id=\"fn_trace\">* On the concept of the trace and its implications for signification.</p>", html_content)
                fn1_page_found = True
            elif item.file_name == endnotes_filename:
                self.assertIn('<h2>Endnotes</h2>', html_content)
                self.assertIn('<p id="en_logo">1. For an extended discussion of logocentrism', html_content)
                endnotes_page_found = True
        
        self.assertTrue(main_chap_found, f"Main chapter file '{main_chap_filename}' not found or content incorrect.")
        self.assertTrue(fn1_page_found, f"Footnote file '{fn1_filename}' not found or content incorrect.")
        self.assertTrue(endnotes_page_found, f"Endnotes file '{endnotes_filename}' not found or content incorrect.")

    def test_create_epub_pippin_style_endnotes_creates_file(self):
        filename = "pippin_style_endnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_pippin_style_endnotes(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_pippin_style_endnotes_content(self):
        filename = "pippin_style_endnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_pippin_style_endnotes(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/pippin_notes.css')
        self.assertIsNotNone(css_item, "CSS file 'style/pippin_notes.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn("a.fnref", css_content)
            self.assertIn(".endnote-pippin", css_content)

        chapter_found = False
        notes_page_found = False
        chap_filename = "chap_pippin_fn.xhtml"
        notes_filename = "notes_pippin.xhtml"

        for item in book.get_items():
            if not isinstance(item, epub.EpubHtml):
                continue
            html_content = item.get_content().decode('utf-8')
            if item.file_name == chap_filename:
                self.assertIn('<h1>Test Chapter Content</h1>', html_content)
                self.assertIn('<a class="fnref" href="notes_pippin.xhtml#fn1" id="fnref1">1</a>', html_content)
                chapter_found = True
            elif item.file_name == notes_filename:
                self.assertIn('<h1>Test Notes</h1>', html_content)
                self.assertIn('<p id="fn1">This is a test note.</p>', html_content)
                notes_page_found = True
        
        self.assertTrue(chapter_found, f"Chapter file '{chap_filename}' not found or content incorrect.")
        self.assertTrue(notes_page_found, f"Notes page file '{notes_filename}' not found or content incorrect.")

    def test_create_epub_heidegger_ge_style_endnotes_creates_file(self):
        filename = "heidegger_ge_endnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_heidegger_ge_style_endnotes(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_heidegger_ge_style_endnotes_content(self):
        filename = "heidegger_ge_endnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_heidegger_ge_style_endnotes(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/heidegger_ge.css')
        self.assertIsNotNone(css_item, "CSS file 'style/heidegger_ge.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn(".footnote_number", css_content)
            self.assertIn(".endnote-heidegger-ge", css_content)

        chapter_found = False
        notes_page_found = False
        chap_filename = "chap_heidegger_ge.xhtml"
        notes_filename = "notes_heidegger_ge.xhtml"

        for item in book.get_items():
            if not isinstance(item, epub.EpubHtml):
                continue
            html_content = item.get_content().decode('utf-8')
            if item.file_name == chap_filename:
                self.assertIn('<div class="title-chapter"><span class="b">The Essence of Truth</span></div>', html_content)
                self.assertIn('<sup><a href="notes_heidegger_ge.xhtml#ftn_fn1" id="ref_ftn_fn1"><span><span class="footnote_number">1</span></span></a></sup>', html_content)
                chapter_found = True
            elif item.file_name == notes_filename:
                self.assertIn('<h1>Notes</h1>', html_content)
                self.assertIn('<p class="endnote-heidegger-ge" id="ftn_fn1">', html_content)
                self.assertIn("This is the first note, in the style of Heidegger's German Existentialism EPUBs.</p>", html_content)
                notes_page_found = True
        
        self.assertTrue(chapter_found, f"Chapter file '{chap_filename}' not found or content incorrect.")
        self.assertTrue(notes_page_found, f"Notes page file '{notes_filename}' not found or content incorrect.")

    def test_create_epub_heidegger_metaphysics_style_footnotes_creates_file(self):
        filename = "heidegger_metaphysics_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_heidegger_metaphysics_style_footnotes(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_heidegger_metaphysics_style_footnotes_content(self):
        filename = "heidegger_metaphysics_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_heidegger_metaphysics_style_footnotes(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/heidegger_meta.css')
        self.assertIsNotNone(css_item, "CSS file 'style/heidegger_meta.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn("sup a", css_content) 
            self.assertIn("section.notesSet", css_content)
            self.assertIn("li.noteEntry", css_content)

        chapter_found = False
        chap_filename = "chap_heidegger_meta_fn.xhtml"
        for item in book.get_items():
            if not isinstance(item, epub.EpubHtml):
                continue
            if item.file_name == chap_filename:
                html_content = item.get_content().decode('utf-8')
                self.assertIn('<sup><a aria-describedby="fn1_meta" epub:type="noteref" href="#fn1_meta" id="ft1_meta">1</a></sup>', html_content)
                self.assertIn('<section class="notesSet" role="doc-endnotes" epub:type="footnotes">', html_content)
                self.assertIn('<li class="noteEntry" id="fn1_meta" role="doc-footnote" epub:type="footnote">', html_content)
                self.assertIn('As elaborated in *Being and Time*. {TN: Translator\'s note - this is a simplification.}</p>', html_content)
                chapter_found = True
                break
        self.assertTrue(chapter_found, f"Chapter content for Heidegger Metaphysics style footnotes ('{chap_filename}') not found or content incorrect.")

    def test_create_epub_same_page_footnotes_creates_file(self):
        filename = "same_page_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_same_page_footnotes(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_same_page_footnotes_content(self):
        filename = "same_page_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_same_page_footnotes(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/notes.css')
        self.assertIsNotNone(css_item, "CSS file 'style/notes.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn(".footnote {", css_content)
            self.assertIn("sup a {", css_content)
            self.assertIn("font-size: 0.8em;", css_content)
            self.assertIn("color: blue;", css_content)

        chapter_found = False
        found_item_content = None
        chap_filename = "chap_footnotes.xhtml" 
        for item in book.get_items(): # Changed from get_items_of_type
            if isinstance(item, epub.EpubHtml) and item.file_name == chap_filename: # Check type here
                found_item_content = item.get_content().decode('utf-8')
                chapter_found = True
                break
        self.assertTrue(chapter_found, f"Chapter item '{chap_filename}' not found.")
        if chapter_found and found_item_content:
            self.assertIn('<h1>Chapter 1: The Burden of Proof</h1>', found_item_content)
            self.assertIn('<sup id="fnref1"><a href="#fn1">1</a></sup>', found_item_content) 
            self.assertIn('<sup id="fnref2"><a href="#fn2">2</a></sup>', found_item_content) 
            self.assertIn('<hr class="footnote-separator"/>', found_item_content)
            self.assertIn('<div class="footnotes">', found_item_content) 
            self.assertIn('<p id="fn1" class="footnote"><a href="#fnref1">1.</a> This claim is often debated in AI ethics circles, particularly concerning generative models.</p>', found_item_content) 
            self.assertIn('<p id="fn2" class="footnote"><a href="#fnref2">2.</a> See Turing\'s arguments on "Lady Lovelace\'s Objection" regarding machine originality.</p>', found_item_content) 

    def test_create_epub_endnotes_separate_file_creates_file(self):
        filename = "endnotes_separate_file.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_endnotes_separate_file(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_endnotes_separate_file_content(self):
        filename = "endnotes_separate_file.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_endnotes_separate_file(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/endnotes.css')
        self.assertIsNotNone(css_item, "CSS file 'style/endnotes.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn(".endnote-item", css_content)
            self.assertIn("sup a", css_content)

        chapter1_found = False
        chapter2_found = False
        notes_page_found = False
        chap1_filename = "chap_main.xhtml" 
        chap2_filename = "chap_main_page2.xhtml" 
        notes_filename = "endnotes.xhtml" 

        for item in book.get_items(): # Changed from get_items_of_type
            if isinstance(item, epub.EpubHtml): # Check type here
                html_content = item.get_content().decode('utf-8')
                if item.file_name == chap1_filename:
                    self.assertIn('<h1>Chapter 1: Existential Inquiries</h1>', html_content)
                    self.assertIn('<sup id="enref1"><a href="endnotes.xhtml#en1">1</a></sup>', html_content)
                    self.assertIn('<sup id="enref2"><a href="endnotes.xhtml#en2">2</a></sup>', html_content)
                    chapter1_found = True
                elif item.file_name == chap2_filename:
                    self.assertIn('<h1>Chapter 2: Power and Knowledge</h1>', html_content)
                    self.assertIn('<sup id="enref3"><a href="endnotes.xhtml#en3">3</a></sup>', html_content)
                    chapter2_found = True
                elif item.file_name == notes_filename:
                    self.assertIn('<h1>Endnotes</h1>', html_content)
                    self.assertIn('<div id="en1" class="endnote-item"><p><a href="chap_main.xhtml#enref1">1.</a> The concept of "Dasein" is central to Heidegger\'s Being and Time.</p></div>', html_content)
                    self.assertIn('<div id="en2" class="endnote-item"><p><a href="chap_main.xhtml#enref2">2.</a> This refers to the Socratic paradox, "I know that I know nothing."</p></div>', html_content)
                    self.assertIn('<div id="en3" class="endnote-item"><p><a href="chap_main_page2.xhtml#enref3">3.</a> Foucault\'s analysis of power structures is detailed in "Discipline and Punish".</p></div>', html_content)
                    notes_page_found = True
        
        self.assertTrue(chapter1_found, f"Chapter file '{chap1_filename}' not found or content incorrect.")
        self.assertTrue(chapter2_found, f"Chapter file '{chap2_filename}' not found or content incorrect.")
        self.assertTrue(notes_page_found, f"Notes page file '{notes_filename}' not found or content incorrect.")

    def test_create_epub_kant_style_footnotes_creates_file(self):
        filename = "kant_style_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_kant_style_footnotes(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_kant_style_footnotes_content(self):
        filename = "kant_style_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_kant_style_footnotes(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/kant_notes.css')
        self.assertIsNotNone(css_item, "CSS file 'style/kant_notes.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn(".calibre9 {", css_content)
            self.assertIn("p.footnotes {", css_content) 

        chapter_found = False
        chap_filename = "chap_kant_fn.xhtml" 
        for item in book.get_items(): 
            if not isinstance(item, epub.EpubHtml): 
                continue
            
            if item.file_name == chap_filename: 
                html_content = item.get_content().decode('utf-8')
                self.assertIn('<sup class="calibre18"><em class="calibre1"><a id="Fkantfn1" href="#Fkantfr1" class="calibre9">1</a></em></sup>', html_content)
                self.assertIn('<p id="Fkantfr1" class="footnotes"><sup class="calibre18"><em class="calibre1"><a href="#Fkantfn1" class="calibre9">1.</a></em></sup> See Critique of Pure Reason, B19.</p>', html_content)
                chapter_found = True
                break
        self.assertTrue(chapter_found, f"Chapter content for Kant style footnotes ('{chap_filename}') not found or content incorrect.")

    def test_create_epub_dual_note_system_creates_file(self):
        filename = "dual_note_system.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_dual_note_system(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_dual_note_system_content(self):
        filename = "dual_note_system.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_dual_note_system(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/dual_notes.css')
        self.assertIsNotNone(css_item, "CSS file 'style/dual_notes.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn(".footnote-author", css_content)
            self.assertIn(".endnote-editor-ref sup a", css_content)
            self.assertIn(".footnote-author-ref sup a", css_content)
            self.assertIn(".endnote-item", css_content)

        chapter_found = False
        notes_page_found = False
        chap_filename = "chap_dual.xhtml" 
        endnotes_filename = "editor_endnotes.xhtml" 

        for item in book.get_items(): # Changed from get_items_of_type
            if isinstance(item, epub.EpubHtml): # Check type here
                html_content = item.get_content().decode('utf-8')
                if item.file_name == chap_filename:
                    self.assertIn('<h1>The State and Ethical Life</h1>', html_content)
                    self.assertIn('<sup class="footnote-author-ref"><a id="authorFNrefStar" href="#authorFNStar">*</a></sup>', html_content)
                    self.assertIn('<sup class="endnote-editor-ref"><a id="editorENref1" href="editor_endnotes.xhtml#editorEN1">1</a></sup>', html_content)
                    self.assertIn('<div class="footnotes-author">', html_content)
                    self.assertIn('Author\'s own clarification: This refers to the rational state, not any empirical instantiation.</p>', html_content)
                    chapter_found = True
                elif item.file_name == endnotes_filename:
                    self.assertIn('<h1>Editor\'s Endnotes</h1>', html_content)
                    self.assertIn('<div id="editorEN1" class="endnote-item">', html_content)
                    self.assertIn('This passage refers to the political climate of early 19th century Prussia.</p>', html_content)
                    notes_page_found = True
        
        self.assertTrue(chapter_found, f"Chapter file '{chap_filename}' not found or content incorrect.")
        self.assertTrue(notes_page_found, f"Editor's endnotes file '{endnotes_filename}' not found or content incorrect.")

    def test_create_epub_hegel_sol_style_footnotes_creates_file(self):
        filename = "hegel_sol_style_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_hegel_sol_style_footnotes(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_hegel_sol_style_footnotes_content(self):
        filename = "hegel_sol_style_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_hegel_sol_style_footnotes(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        css_item = book.get_item_with_href('style/hegel_sol.css') 
        self.assertIsNotNone(css_item, "CSS file 'style/hegel_sol.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn("font-size: 0.75em; vertical-align: super;", css_content) # Check for the properties of .calibre30
            self.assertIn("margin: 0; padding: 0; font-size: 0.9em;", css_content) # Check for the properties of .calibre14

        chapter_found = False
        chap_filename = "chap_hegel_sol_fn.xhtml" 
        for item in book.get_items(): # Changed from get_items_of_type
            if isinstance(item, epub.EpubHtml) and item.file_name == chap_filename: # Check type here
                html_content = item.get_content().decode('utf-8')
                self.assertIn('<span><a id="hegelFNref1"/><a href="#hegelFN1"><sup class="calibre30">1</sup></a></span>', html_content) 
                self.assertIn('<div class="calibre32" id="hegelFN1">', html_content) 
                self.assertIn('This is discussed extensively in the opening sections of the Science of Logic. The transition is not merely a juxtaposition but an immanent development.', html_content)
                chapter_found = True
                break
        self.assertTrue(chapter_found, f"Chapter content for Hegel SoL style footnotes ('{chap_filename}') not found or content incorrect.")
    def test_create_epub_kant_style_footnotes_creates_file(self):
        filename = "kant_style_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        notes.create_epub_kant_style_footnotes(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_kant_style_footnotes_content(self):
        filename = "kant_style_footnotes.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        notes.create_epub_kant_style_footnotes(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        # # Check for CSS
        # css_item = book.get_item_with_href('style/kant_notes.css')
        # self.assertIsNotNone(css_item, "CSS file 'style/kant_notes.css' not found.")
        # if css_item:
        #     css_content = css_item.get_content().decode('utf-8')
        #     self.assertIn(".footnote-kant", css_content) # Placeholder CSS class

        # # Check for chapter content
        # chapter_found = False
        # chap_filename = "chap_kant_fn.xhtml" # Placeholder chapter filename
        # for item in book.get_items_of_type(epub.EpubHtml):
        #     if item.file_name == chap_filename:
        #         html_content = item.get_content().decode('utf-8')
        #         # Add specific assertions for Kant-style footnote references and content
        #         self.assertIn("Placeholder Kant footnote reference", html_content)
        #         self.assertIn("Placeholder Kant footnote text", html_content)
        #         chapter_found = True
        #         break
        # self.assertTrue(chapter_found, f"Chapter content for Kant style footnotes ('{chap_filename}') not found.")
        
        # Check for CSS
        css_item = book.get_item_with_href('style/kant_notes.css')
        self.assertIsNotNone(css_item, "CSS file 'style/kant_notes.css' not found.")
        if css_item:
            css_content = css_item.get_content().decode('utf-8')
            self.assertIn(".footnote-kant", css_content) # Placeholder CSS class

        # Check for chapter content
        chapter_found = False
        chap_filename = "chap_kant_fn.xhtml" # Placeholder chapter filename
        for item in book.get_items(): # Changed from get_items_of_type
            if isinstance(item, epub.EpubHtml) and item.file_name == chap_filename: # Check type here
                html_content = item.get_content().decode('utf-8')
                # Add specific assertions for Kant-style footnote references and content
                self.assertIn('<a href="#fn1_kant" id="fnref1_kant" epub:type="noteref">1</a>', html_content)
                # Break down the assertion for the footnote div to be less whitespace sensitive
                self.assertIn('<div class="footnote-kant" id="fn1_kant" epub:type="footnote">', html_content)
                self.assertIn('<p><a href="#fnref1_kant" epub:type="backlink">1.</a> This is a Kant-style footnote. It appears on the same page, typically separated by a rule.</p>', html_content)
                self.assertIn('</div>', html_content) # Ensure the div closes after the paragraph
                chapter_found = True
                break
        self.assertTrue(chapter_found, f"Chapter content for Kant style footnotes ('{chap_filename}') not found.")

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()