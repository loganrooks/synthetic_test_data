import os
import unittest
import zipfile
from ebooklib import epub

from synth_data_gen.generators.epub_components import multimedia
from synth_data_gen.common.utils import EPUB_DIR

class TestEpubMultimedia(unittest.TestCase):

    def setUp(self):
        self.output_dir = os.path.join(EPUB_DIR, "images_fonts")
        os.makedirs(self.output_dir, exist_ok=True)
        self.files_to_remove = []

    def tearDown(self):
        for f_path in self.files_to_remove:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_create_epub_image_as_special_text_creates_file(self):
        filename = "image_as_special_text.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        multimedia.create_epub_image_as_special_text(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_image_as_special_text_content(self):
        filename = "image_as_special_text.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        multimedia.create_epub_image_as_special_text(filename=filename)
        
        book = epub.read_epub(expected_filepath)
        
        # Check for CSS
        css_item = book.get_item_with_href('style/img_special_text.css')
        self.assertIsNotNone(css_item)
        css_content = css_item.get_content().decode('utf-8')
        self.assertIn("img.calibre18-hegel-img", css_content)

        # Check for image
        img_item = book.get_item_with_href('images/special_char_placeholder.png')
        self.assertIsNotNone(img_item)
        self.assertEqual(img_item.media_type, "image/png")

        # Check for chapter content
        chapter_item = book.get_item_with_href('c1_img_special_text.xhtml')
        self.assertIsNotNone(chapter_item, "Chapter c1_img_special_text.xhtml not found by Href.")
        if chapter_item:
            html_content = chapter_item.get_content().decode('utf-8')
            self.assertIn('<img alt="[special operator]" src="../images/special_char_placeholder.png" class="calibre18-hegel-img"/>', html_content)
        else:
            self.fail("Chapter item c1_img_special_text.xhtml was None.")

    def test_create_epub_font_obfuscated_creates_file(self):
        filename = "font_obfuscated.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)
        multimedia.create_epub_font_obfuscated(filename=filename)
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_epub_font_obfuscated_content_and_encryption_xml(self):
        filename = "font_obfuscated.epub"
        expected_filepath = os.path.join(self.output_dir, filename)
        self.files_to_remove.append(expected_filepath)
        
        # We need to patch _write_epub_file to inspect custom_files_to_add
        # or modify _write_epub_file to actually write it for testing.
        # For now, let's assume _write_epub_file is modified or we test structure.
        
        # SUT call
        multimedia.create_epub_font_obfuscated(filename=filename)
        
        book = epub.read_epub(expected_filepath)

        # Check for CSS
        css_item = book.get_item_with_href('style/font_obf.css')
        self.assertIsNotNone(css_item)
        css_content = css_item.get_content().decode('utf-8')
        self.assertIn("@font-face", css_content)
        self.assertIn("url('../fonts/obfuscated_font.ttf')", css_content)

        # Check for font item in manifest
        font_item = book.get_item_with_href('fonts/obfuscated_font.ttf')
        self.assertIsNotNone(font_item)
        self.assertEqual(font_item.media_type, "application/x-font-truetype")
        
        # Check for chapter content
        chapter_item = book.get_item_with_href('c1_font_obf.xhtml')
        self.assertIsNotNone(chapter_item, "Chapter c1_font_obf.xhtml not found by Href.")
        if chapter_item:
            html_content = chapter_item.get_content().decode('utf-8')
            self.assertIn("Text with Obfuscated Font", html_content)
            self.assertIn("encryption.xml", html_content) # Text mentions it
        else:
            self.fail("Chapter item c1_font_obf.xhtml was None.")

        # Check for encryption.xml (this is the tricky part as ebooklib doesn't directly support it)
        # The SUT adds it to a custom attribute `book.custom_files_to_add`.
        # A real test would require `_write_epub_file` to handle this or to inspect the ZIP.
        # For now, we'll simulate that `_write_epub_file` handles it.
        # This test will likely need adjustment based on how `_write_epub_file` is actually implemented.
        
        # To properly test encryption.xml, we'd need to unzip the .epub and check META-INF/encryption.xml
        # This is a simplified check assuming the file would be there if the SUT intended it.
        # A more robust test would involve a mock for _write_epub_file or unzipping.
        
        # Let's assume the SUT's mechanism for adding encryption.xml works.
        # We can't directly verify its content in the EPUB via ebooklib easily.
        # We will check if the book object has the custom attribute as a proxy.
        # This is not ideal but a limitation of testing this specific feature with ebooklib alone.
        
        # Re-create book object as SUT modifies it in place
        # This part of the test is more conceptual due to ebooklib limitations
        # on non-OEBPS META-INF files.
        
        # A better approach for testing encryption.xml would be to mock _write_epub_file
        # and assert that it's called with the correct parameters including the encryption.xml data.
        # Or, unzip the created epub and check for META-INF/encryption.xml.
        with zipfile.ZipFile(expected_filepath, 'r') as epub_zip:
            try:
                with epub_zip.open('META-INF/encryption.xml') as enc_file:
                    encryption_content = enc_file.read().decode('utf-8')
                    self.assertIn("<enc:EncryptionMethod Algorithm=\"http://www.idpf.org/2008/embedding\" />", encryption_content)
                    self.assertIn("<enc:CipherReference URI=\"OEBPS/fonts/obfuscated_font.ttf\" />", encryption_content)
            except KeyError:
                self.fail("META-INF/encryption.xml not found in EPUB archive.")


if __name__ == '__main__':
    unittest.main()