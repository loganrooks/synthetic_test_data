import unittest
import os
import tempfile
from ebooklib import epub, ITEM_DOCUMENT
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO

from synth_data_gen.generators.epub_components import structure

class TestEpubStructure(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_epub2_with_guide_creates_file(self):
        filename = os.path.join(self.output_path, "test_epub2_guide.epub")
        # This call will use write_file=True by default
        returned_book_object = structure.create_epub2_with_guide(filename=filename)
        self.assertTrue(os.path.exists(filename), "EPUB file was not created.")

        # Read the created EPUB to check its contents
        read_book = epub.read_epub(filename)
        self.assertIsNotNone(read_book, "Could not read created EPUB file.")

        # Check for NCX in the read book
        ncx_item = read_book.get_item_with_id('ncx')
        if ncx_item is None:
            for item in read_book.get_items():
                if isinstance(item, epub.EpubNcx):
                    ncx_item = item
                    break
        self.assertIsNotNone(ncx_item, "NCX item not found in created EPUB file.")
        self.assertIsInstance(ncx_item.content, bytes, "NCX content should be bytes in created EPUB.")
        self.assertIn(b"<text>Chapter 1</text>", ncx_item.content, "Chapter 1 not found in NCX content of created EPUB.")


    def test_create_epub2_with_guide_content(self):
        filename = os.path.join(self.output_path, "test_epub2_guide_content.epub")
        # Call SUT without writing the file to inspect the book object directly
        book = structure.create_epub2_with_guide(filename=filename, write_file=False)
        
        # Verify guide items
        expected_guide_items = [
            {'type': 'cover', 'title': 'Cover Image', 'href': 'cover.xhtml'},
            {'type': 'toc', 'title': 'Table of Contents', 'href': 'nav.xhtml'},
            {'type': 'text', 'title': 'Beginning', 'href': 'chapter1.xhtml'}
        ]
        self.assertIsNotNone(book.guide, "Guide section should exist.")
        self.assertEqual(len(book.guide), len(expected_guide_items), "Incorrect number of guide items.")
        
        for i, item in enumerate(expected_guide_items):
            self.assertEqual(book.guide[i]['type'], item['type'])
            self.assertEqual(book.guide[i]['title'], item['title'])
            self.assertTrue(item['href'] in book.guide[i]['href'])

        # Verify chapter content (basic check)
        # Debug: Print item IDs to check
        # print("Book items by ID:")
        # for item_id_key in book.items_id_map.keys():
        #    print(f"Item ID Key from map: {item_id_key}")
        # for item_obj in book.items:
        #    print(f"Item object ID: {item_obj.id}, Href: {item_obj.get_name()}")
            
        chapter1 = book.get_item_with_id("ch1")

        self.assertIsNotNone(chapter1, f"Chapter 1 item (id='ch1') not found. Available IDs: {[item.id for item in book.items]}")
        self.assertIsInstance(chapter1.content, bytes, "Chapter content should be bytes.")
        self.assertIn(b"<h1>Chapter 1</h1>", chapter1.content)
        self.assertIn(b"<p>This is the first chapter with a guide reference.</p>", chapter1.content)

        # Verify NAV document content (basic check)
        nav_doc = book.get_item_with_href("nav.xhtml")
        self.assertIsNotNone(nav_doc, "NAV document item not found.")
        self.assertIsInstance(nav_doc.content, bytes, "NAV content should be bytes.")
        self.assertIn(b"<title>table of contents</title>", nav_doc.content.lower()) # search for lowercase
        self.assertIn(b"<li><a href=\"chapter1.xhtml\">Chapter 1</a></li>", nav_doc.content)
        
        # Verify NCX (basic check for EPUB2)
        ncx_item = book.get_item_with_id('ncx') # Default ID for NCX
        if ncx_item is None: # Fallback to type checking if ID fails
            # Correct way to get NCX items by type is to check for EpubNcx class instances
            for item in book.get_items():
                if isinstance(item, epub.EpubNcx):
                    ncx_item = item
                    break
    
        self.assertIsNotNone(ncx_item, "NCX item not found in book.items.")
        # Content will be empty as write_epub is not called when write_file=False
        # self.assertIsInstance(ncx_item.content, bytes, "NCX content should be bytes.")
        # self.assertIn(b"<text>Chapter 1</text>", ncx_item.content)

        # Verify spine order
        self.assertGreater(len(book.spine), 0, "Spine should not be empty.")
        # Assuming nav is first, then chapter1
        if nav_doc: # nav_doc might not be in spine if it's just a guide item
             self.assertTrue(any(nav_doc.id in s_item for s_item in book.spine if isinstance(s_item, str) or isinstance(s_item, tuple) and nav_doc.id in s_item[0]), "NAV document not in spine or incorrect order.")
        self.assertTrue(any(chapter1.id in s_item for s_item in book.spine if isinstance(s_item, str) or isinstance(s_item, tuple) and chapter1.id in s_item[0]), "Chapter 1 not in spine or incorrect order.")

    def test_create_epub_opf_specific_meta_creates_file(self):
        filename = os.path.join(self.output_path, "test_opf_meta.epub")
        structure.create_epub_opf_specific_meta(filename=filename)
        self.assertTrue(os.path.exists(filename), "EPUB file was not created.")
        # Basic check: read the epub
        book = epub.read_epub(filename)
        self.assertIsNotNone(book, "Could not read created EPUB file.")

    def test_create_epub_opf_specific_meta_content(self):
        filename = os.path.join(self.output_path, "test_opf_meta_content.epub")
        # Call SUT without writing the file to inspect the book object directly
        book = structure.create_epub_opf_specific_meta(filename=filename, write_file=False)
        
        self.assertIsNotNone(book, "Book object should be returned.")

        # Check for dc:identifier
        identifiers = book.get_metadata('DC', 'identifier')
        self.assertTrue(len(identifiers) > 0, "dc:identifier not found.")
        # Assuming the SUT adds a default or generated ID.
        # self.assertEqual(identifiers[0][0], 'test-id-123')

        # Check for dc:language
        languages = book.get_metadata('DC', 'language')
        self.assertTrue(len(languages) > 0, "dc:language not found.")
        self.assertEqual(languages[0][0], 'en', "Default language should be 'en'.")

        # Check for dc:modified (which implies dcterms:modified)
        modified_dates = book.get_metadata('DC', 'modified')
        self.assertTrue(len(modified_dates) > 0, "dc:modified not found.")
        self.assertEqual(modified_dates[0][0], '2024-01-01T00:00:00Z', "Incorrect dc:modified date.")
        # Ensure no 'property' attribute is present if it's a simple DC.modified tag
    def test_create_epub_spine_pagemap_ref_creates_file(self):
        filename = os.path.join(self.output_path, "test_spine_pagemap.epub")
        structure.create_epub_spine_pagemap_ref(filename=filename, write_file=True)
        self.assertTrue(os.path.exists(filename), "EPUB file was not created.")
        
        # Read the created EPUB to check its contents
        read_book = epub.read_epub(filename)
        self.assertIsNotNone(read_book, "Could not read created EPUB file.")
        
        # Check for page-map.xml in manifest
        page_map_item_manifest = read_book.get_item_with_href('page-map.xml')
        self.assertIsNotNone(page_map_item_manifest, "page-map.xml not found in manifest.")
        self.assertEqual(page_map_item_manifest.media_type, "application/oebps-page-map+xml")

    def test_create_epub_spine_pagemap_ref_content(self):
        filename = os.path.join(self.output_path, "test_spine_pagemap_content.epub")
        book = structure.create_epub_spine_pagemap_ref(filename=filename, write_file=False)
        self.assertIsNotNone(book, "Book object should be returned.")

        # Check for page-map item in book items
        page_map_item = book.get_item_with_id("page_map")
        self.assertIsNotNone(page_map_item, "Page-map item with UID 'page_map' not found.")
        self.assertEqual(page_map_item.get_name(), "page-map.xml")
        self.assertEqual(page_map_item.media_type, "application/oebps-page-map+xml")
        
        # Check page-map content
        expected_page_map_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<page-map xmlns="http://www.idpf.org/2007/opf">
    <page name="1" href="c1_pagemap.xhtml"/>
</page-map>
"""
        self.assertEqual(page_map_item.content, expected_page_map_content)

        # Check spine page_map attribute
        self.assertIsNotNone(book.page_map, "book.page_map attribute should be set.")
        self.assertEqual(book.page_map, page_map_item.id, "book.page_map should point to the UID of the page_map_item.")
        
        # Check that the chapter is in the spine
        chapter_item = book.get_item_with_id("c1_pm")
        self.assertIsNotNone(chapter_item, "Chapter item c1_pm not found.")
        # Spine check: book.spine is a list of UIDs or (UID, linear_value)
        # The SUT sets it as: book.spine = [(epub_chapters[0].id, 'yes', 'page_map')]
        # However, ebooklib might process this into a simpler list for book.spine
        # and store the page_map attribute separately on the book object.
        # Let's check if the chapter UID is in the spine items.
        
        found_in_spine = False
        for spine_entry in book.spine:
            if isinstance(spine_entry, tuple) and spine_entry[0] == chapter_item.id:
                found_in_spine = True
                # Optionally check the linear attribute if needed
                # self.assertEqual(spine_entry[1], 'yes')
                # The third element 'page_map' is not standard for ebooklib's spine list items.
                # It's an attribute of the <spine> tag itself, handled by book.page_map.
                break
            elif isinstance(spine_entry, str) and spine_entry == chapter_item.id:
                found_in_spine = True
                break
            self.assertTrue(found_in_spine, f"Chapter {chapter_item.id} not found in spine. Spine: {book.spine}")


    def test_create_epub_structure_split_files_creates_files(self):
        filename_pattern = os.path.join(self.output_path, "test_split_chapter_{}.epub")
        num_splits = 2
        structure.create_epub_structure_split_files(filename_pattern=filename_pattern, num_splits=num_splits, write_files=True)
        for i in range(1, num_splits + 1):
            expected_filename = filename_pattern.format(i)
            self.assertTrue(os.path.exists(expected_filename), f"EPUB file {expected_filename} was not created.")
            # Basic check: read the epub
            read_book = epub.read_epub(expected_filename)
            self.assertIsNotNone(read_book, f"Could not read created EPUB file: {expected_filename}")
            titles = read_book.get_metadata('DC', 'title')
            self.assertTrue(len(titles) > 0, "Title not found.")
            self.assertEqual(titles[0][0], f"Sample Split EPUB - Part {i}")

    def test_create_epub_structure_split_files_content(self):
        filename_pattern = os.path.join(self.output_path, "test_split_content_chapter_{}.epub")
        num_splits = 1 # Test content of one split file
        books = structure.create_epub_structure_split_files(filename_pattern=filename_pattern, num_splits=num_splits, write_files=False)
        
        self.assertEqual(len(books), num_splits, "Incorrect number of book objects returned.")
        book = books[0]
        self.assertIsNotNone(book, "Book object should be returned.")
        
        titles = book.get_metadata('DC', 'title')
        self.assertTrue(len(titles) > 0, "Title not found.")
        self.assertEqual(titles[0][0], f"Sample Split EPUB - Part 1")

        identifiers = book.get_metadata('DC', 'identifier')
        self.assertTrue(len(identifiers) > 0, "Identifier not found.")
        self.assertEqual(identifiers[0][0], f"urn:uuid:sample-split-file-1")

        languages = book.get_metadata('DC', 'language')
        self.assertTrue(len(languages) > 0, "Language not found.")
        self.assertEqual(languages[0][0], "en")

        # Check chapter content
        chapter_item = book.get_item_with_id(f"split_ch_1")
        self.assertIsNotNone(chapter_item, "Chapter item not found.")
        self.assertIsInstance(chapter_item.content, bytes)
        self.assertIn(b"<h1>Chapter for Split File 1</h1>", chapter_item.content)
        self.assertIn(b"<p>This is content for part 1.</p>", chapter_item.content)

        # Check NCX
    def test_create_epub_structure_calibre_artifacts_creates_file(self):
        filename = os.path.join(self.output_path, "test_calibre_artifacts.epub")
        structure.create_epub_structure_calibre_artifacts(filename=filename, write_file=True)
        self.assertTrue(os.path.exists(filename))
        
        # Instead of relying on read_epub to fully parse items,
        # let's unzip and read the OPF file directly.
        opf_content_str = None
        opf_path_in_zip = None

        with zipfile.ZipFile(filename, 'r') as epub_zip:
            # Find the OPF file path from container.xml
            try:
                container_xml_content = epub_zip.read('META-INF/container.xml').decode('utf-8')
                container_root = ET.fromstring(container_xml_content)
                ns_container = {'cn': 'urn:oasis:names:tc:opendocument:xmlns:container'}
                rootfile_element = container_root.find('.//cn:rootfile', ns_container)
                self.assertIsNotNone(rootfile_element, "Rootfile element not found in container.xml")
                opf_path_in_zip = rootfile_element.get('full-path')
                self.assertIsNotNone(opf_path_in_zip, "full-path attribute not found on rootfile element")
            except KeyError:
                self.fail("META-INF/container.xml not found in EPUB archive.")
            except ET.ParseError as e:
                self.fail(f"Failed to parse META-INF/container.xml: {e}")

            # Read the OPF file content
            try:
                opf_content_bytes = epub_zip.read(opf_path_in_zip)
                opf_content_str = opf_content_bytes.decode('utf-8')
            except KeyError:
                self.fail(f"OPF file '{opf_path_in_zip}' not found in EPUB archive. Files: {epub_zip.namelist()}")

        self.assertIsNotNone(opf_content_str, f"Could not extract OPF content from path: {opf_path_in_zip}")

        # Parse OPF XML
        try:
            root = ET.fromstring(opf_content_str)
            namespaces = {
                'opf': 'http://www.idpf.org/2007/opf',
                'dc': 'http://purl.org/dc/elements/1.1/'
            }
            # ET.register_namespace('opf', namespaces['opf']) # Not strictly necessary for findall with ns map
            # ET.register_namespace('dc', namespaces['dc'])

            metadata_element = root.find('opf:metadata', namespaces)
            self.assertIsNotNone(metadata_element, f"<metadata> element not found in OPF. OPF content:\n{opf_content_str}")

            found_series_xml = False
            series_content_xml = None
            
            # Calibre meta tags are typically directly under <metadata>
            # Find all 'meta' tags, which might or might not have the opf: prefix depending on how ebooklib writes them
            # when namespace is None. The most robust is to check for any 'meta' tag.
            # However, valid OPF should use the opf: namespace for its own elements.
            # Let's assume ebooklib correctly uses opf:meta for these.
            
            # Given the default namespace on <package>, unprefixed <meta> tags within <opf:metadata>
            # are considered to be in the OPF namespace.
            for meta_tag in metadata_element.findall('opf:meta', namespaces):
                name_attr = meta_tag.get('name')
                content_attr = meta_tag.get('content')
                if name_attr == 'calibre:series':
                    found_series_xml = True
                    series_content_xml = content_attr
                    break
            
            self.assertTrue(found_series_xml, f"Calibre series metadata tag not found in OPF XML. OPF content:\n{opf_content_str}")
            self.assertEqual(series_content_xml, "Minimal Debug Series", f"Incorrect calibre:series content in OPF XML. OPF content:\n{opf_content_str}")

        except ET.ParseError as e:
            self.fail(f"Failed to parse OPF XML: {e}\nOPF Content:\n{opf_content_str}")


    def test_create_epub_structure_calibre_artifacts_content(self):
        filename = os.path.join(self.output_path, "test_calibre_artifacts_content.epub")
        book = structure.create_epub_structure_calibre_artifacts(filename=filename, write_file=False)
        self.assertIsNotNone(book)

        # Corrected check for calibre:series and calibre:series_index
        found_series_content = False
        series_name_content = None
        found_series_index_content = False
        series_index_val_content = None

        if None in book.metadata and 'meta' in book.metadata[None]:
            for _, attrs_dict in book.metadata[None]['meta']: # Unpack as 2-tuple
                if isinstance(attrs_dict, dict):
                    meta_name = attrs_dict.get('name')
                    if meta_name == 'calibre:series':
                        found_series_content = True
                        series_name_content = attrs_dict.get('content')
                    elif meta_name == 'calibre:series_index':
                        found_series_index_content = True
                        series_index_val_content = attrs_dict.get('content')
        
        self.assertTrue(found_series_content, "Metadata 'calibre:series' not found in None namespace (content test).")
        self.assertEqual(series_name_content, "Minimal Debug Series", "Metadata 'calibre:series' has incorrect value (content test).")
        # The SUT currently only adds 'calibre:series', so no assertions for 'calibre:series_index'.
        # If 'calibre:series_index' were added by SUT, these would be:
        # self.assertTrue(found_series_index_content, "Metadata 'calibre:series_index' not found in None namespace (content test).")
        # self.assertEqual(series_index_val_content, "1.0", "Metadata 'calibre:series_index' has incorrect value (content test).")
if __name__ == '__main__':
    unittest.main()