import pytest
import os
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call # Keep MagicMock and call
from ebooklib import epub

# Assuming toc.py is in synth_data_gen.generators.epub_components
from synth_data_gen.generators.epub_components import toc

def test_create_epub_ncx_simple(mocker: MockerFixture):
    """Test that create_epub_ncx_simple constructs a book with a simple NCX ToC."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')
    
    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_create_book.return_value = mock_book_instance
    
    # Mock the return of _add_epub_chapters to simulate chapter objects
    mock_chapter1 = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter1.file_name = "chap_01.xhtml"
    mock_chapter1.title = "Introduction"
    
    mock_chapter2 = mocker.MagicMock(spec=epub.EpubHtml)
    mock_chapter2.file_name = "chap_02.xhtml"
    mock_chapter2.title = "Further Thoughts"
    
    mock_add_chapters.return_value = [mock_chapter1, mock_chapter2]

    # Call the function to be tested
    toc.create_epub_ncx_simple(filename="test_ncx_simple.epub")

    # Assert _create_epub_book was called (details can be more specific if needed)
    mock_create_book.assert_called_once()
    
    # Assert _add_epub_chapters was called
    mock_add_chapters.assert_called_once()
    # assert mock_add_chapters.call_args[0][0] == mock_book_instance # Check book instance
    # assert isinstance(mock_add_chapters.call_args[0][1], list) # Check chapter_details

    # Assert that book.toc was set correctly for a simple NCX
    expected_toc_links_data = [
        {"href": "chap_01.xhtml", "title": "Introduction", "uid": "intro"},
        {"href": "chap_02.xhtml", "title": "Further Thoughts", "uid": "thoughts"}
    ]
    
    # Check if mock_book_instance.toc was set and has the correct number of items
    assert mock_book_instance.toc is not None
    assert len(mock_book_instance.toc) == len(expected_toc_links_data)

    # Compare attributes of each Link object
    for i, actual_link in enumerate(mock_book_instance.toc):
        expected_link_data = expected_toc_links_data[i]
        assert isinstance(actual_link, epub.Link)
        assert actual_link.href == expected_link_data["href"]
        assert actual_link.title == expected_link_data["title"]
        assert actual_link.uid == expected_link_data["uid"]
        
    # Assert that EpubNcx and EpubNav items were added
    # We need to check the arguments to add_item
    add_item_calls = mock_book_instance.add_item.call_args_list
    added_item_types = [type(args[0]) for args, kwargs in add_item_calls]
    
    assert epub.EpubNcx in added_item_types
    assert epub.EpubNav in added_item_types # create_epub_ncx_simple also adds EpubNav

    # Assert _write_epub_file was called
    mock_write_file.assert_called_once()
    # Check the filepath argument passed to _write_epub_file
    assert mock_write_file.call_args[0][1].endswith("toc/test_ncx_simple.epub")
def test_create_epub_ncx_nested(mocker: MockerFixture):
    """Test that create_epub_ncx_nested constructs a book with a nested NCX ToC."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')
    
    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.toc = [] # Initialize toc as a list to allow append/extend
    mock_create_book.return_value = mock_book_instance
    
    # Mock chapter objects
    mock_p1_intro = mocker.MagicMock(spec=epub.EpubHtml, file_name="part1_intro.xhtml", title="Part I: Foundations")
    mock_c1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="chap_01.xhtml", title="Chapter 1: Core Concepts")
    mock_s1_1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="sec_1_1.xhtml", title="Section 1.1: First Concept")
    mock_ss1_1_1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="sub_1_1_1.xhtml", title="Subsection 1.1.1: Sub-Detail")
    mock_s1_2 = mocker.MagicMock(spec=epub.EpubHtml, file_name="sec_1_2.xhtml", title="Section 1.2: Second Concept")
    mock_c2 = mocker.MagicMock(spec=epub.EpubHtml, file_name="chap_02.xhtml", title="Chapter 2: Advanced Topics")
    
    mock_add_chapters.return_value = [mock_p1_intro, mock_c1, mock_s1_1, mock_ss1_1_1, mock_s1_2, mock_c2]

    toc.create_epub_ncx_nested(filename="test_ncx_nested.epub")

    mock_create_book.assert_called_once()
    mock_add_chapters.assert_called_once()

    # Assert that book.toc was set correctly for a nested NCX
    # Based on the SUT: book.toc = ((link_p1_intro, (toc_c1, toc_c2)),)
    # toc_c1 = (link_c1, (toc_s1_1, toc_s1_2))
    # toc_s1_1 = (link_s1_1, (toc_ss1_1_1,))
    
    assert mock_book_instance.toc is not None
    assert len(mock_book_instance.toc) == 1 # Top level tuple
    
    top_level_tuple = mock_book_instance.toc[0]
    assert isinstance(top_level_tuple, tuple)
    assert len(top_level_tuple) == 2 # Link and its children tuple
    
    # Check Part I link
    part1_link = top_level_tuple[0]
    assert isinstance(part1_link, epub.Link)
    assert part1_link.href == "part1_intro.xhtml"
    assert part1_link.title == "Part I: Foundations"
    assert part1_link.uid == "p1intro_id"
    
    # Check children of Part I
    part1_children_tuple = top_level_tuple[1]
    assert isinstance(part1_children_tuple, tuple)
    assert len(part1_children_tuple) == 2 # toc_c1 and toc_c2
    
    # Check Chapter 1 (toc_c1)
    chapter1_tuple = part1_children_tuple[0]
    assert isinstance(chapter1_tuple, tuple)
    assert len(chapter1_tuple) == 2 # Link and its children tuple
    
    chapter1_link = chapter1_tuple[0]
    assert isinstance(chapter1_link, epub.Link)
    assert chapter1_link.href == "chap_01.xhtml"
    assert chapter1_link.title == "Chapter 1: Core Concepts"
    assert chapter1_link.uid == "c1_id"
    
    chapter1_children_tuple = chapter1_tuple[1]
    assert isinstance(chapter1_children_tuple, tuple)
    assert len(chapter1_children_tuple) == 2 # toc_s1_1 and toc_s1_2
    
    # Check Section 1.1 (toc_s1_1)
    section1_1_tuple = chapter1_children_tuple[0]
    assert isinstance(section1_1_tuple, tuple)
    assert len(section1_1_tuple) == 2 # Link and its children tuple
    
    section1_1_link = section1_1_tuple[0]
    assert isinstance(section1_1_link, epub.Link)
    assert section1_1_link.href == "sec_1_1.xhtml"
    assert section1_1_link.title == "Section 1.1: First Concept"
    assert section1_1_link.uid == "s1_1_id"
    
    section1_1_children_tuple = section1_1_tuple[1]
    assert isinstance(section1_1_children_tuple, tuple)
    assert len(section1_1_children_tuple) == 1 # toc_ss1_1_1
    
    subsection1_1_1_link = section1_1_children_tuple[0]
    assert isinstance(subsection1_1_1_link, epub.Link)
    assert subsection1_1_1_link.href == "sub_1_1_1.xhtml"
    assert subsection1_1_1_link.title == "Subsection 1.1.1: Sub-Detail"
    assert subsection1_1_1_link.uid == "ss1_1_1_id"

    # Check Section 1.2 (toc_s1_2)
    section1_2_link = chapter1_children_tuple[1]
    assert isinstance(section1_2_link, epub.Link)
    assert section1_2_link.href == "sec_1_2.xhtml"
    assert section1_2_link.title == "Section 1.2: Second Concept"
    assert section1_2_link.uid == "s1_2_id"

    # Check Chapter 2 (toc_c2)
    chapter2_link = part1_children_tuple[1]
    assert isinstance(chapter2_link, epub.Link)
    assert chapter2_link.href == "chap_02.xhtml"
    assert chapter2_link.title == "Chapter 2: Advanced Topics"
    assert chapter2_link.uid == "c2_id"

    add_item_calls = mock_book_instance.add_item.call_args_list
    added_item_types = [type(args[0]) for args, kwargs in add_item_calls]
    
    assert epub.EpubNcx in added_item_types
    assert epub.EpubNav in added_item_types

    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_ncx_nested.epub")
def test_create_epub_html_toc_linked(mocker: MockerFixture):
    """Test that create_epub_html_toc_linked constructs a book with a linked HTML ToC page."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')
    
    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.toc = []
    mock_create_book.return_value = mock_book_instance
    
    # Mock chapter objects
    mock_ch1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="chap_01.xhtml", title="Chapter 1: Beginnings")
    mock_ch2 = mocker.MagicMock(spec=epub.EpubHtml, file_name="chap_02.xhtml", title="Chapter 2: Developments")
    mock_ch3 = mocker.MagicMock(spec=epub.EpubHtml, file_name="chap_03.xhtml", title="Chapter 3: Conclusions")
    
    mock_add_chapters.return_value = [mock_ch1, mock_ch2, mock_ch3]

    # We will find the HTML ToC page from the book's items after SUT call
    
    toc.create_epub_html_toc_linked(filename="test_html_toc_linked.epub")

    mock_create_book.assert_called_once()
    mock_add_chapters.assert_called_once()

    # Find the HTML ToC page from the items added to the book
    html_toc_page_instance = None
    for call_args in mock_book_instance.add_item.call_args_list:
        item = call_args[0][0] # item is the first argument to add_item
        if isinstance(item, epub.EpubHtml) and item.file_name == 'toc.xhtml':
            html_toc_page_instance = item
            break
    assert html_toc_page_instance is not None, "HTML ToC page was not added to the book"
    
    # Check content of the HTML ToC page
    expected_html_toc_content = """<h1>Table of Contents</h1>
<ul>
    <li><a href="chap_01.xhtml">Chapter 1: Beginnings</a></li>
    <li><a href="chap_02.xhtml">Chapter 2: Developments</a><ul><li><a href="chap_02.xhtml#sec2.1">Section 2.1: First Development</a></li></ul></li>
    <li><a href="chap_03.xhtml">Chapter 3: Conclusions</a></li>
</ul>"""
    # Normalize whitespace for comparison
    normalized_expected_content = "".join(expected_html_toc_content.split())
    # Ensure content is treated as string before split(), in case it's MagicMock
    actual_content_str = str(html_toc_page_instance.content)
    normalized_actual_content = "".join(actual_content_str.split())
    assert normalized_actual_content == normalized_expected_content
    
    # Assert that book.toc was set (for NCX)
    assert mock_book_instance.toc is not None
    assert len(mock_book_instance.toc) == 3
    assert mock_book_instance.toc[0].href == "chap_01.xhtml"
    assert mock_book_instance.toc[1].href == "chap_02.xhtml"
    assert mock_book_instance.toc[2].href == "chap_03.xhtml"

    # Assert that EpubNcx and EpubNav items were added, and the HTML ToC page
    add_item_calls = mock_book_instance.add_item.call_args_list
    added_items = [args[0] for args, kwargs in add_item_calls]
    
    assert any(isinstance(item, epub.EpubNcx) for item in added_items)
    assert any(isinstance(item, epub.EpubNav) for item in added_items)
    assert html_toc_page_instance in added_items # Check if the retrieved ToC page was added

    # Assert spine includes 'nav' and the HTML ToC page
    assert 'nav' in mock_book_instance.spine
    assert html_toc_page_instance in mock_book_instance.spine
    assert mock_ch1 in mock_book_instance.spine
    assert mock_ch2 in mock_book_instance.spine
    assert mock_ch3 in mock_book_instance.spine
    
    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_html_toc_linked.epub")
def test_create_epub_ncx_with_pagelist(mocker: MockerFixture):
    """Test that create_epub_ncx_with_pagelist constructs a book with NCX and a custom pageList placeholder."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    # No need to mock _add_epub_chapters as SUT creates chapters directly
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')
    
    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.toc = []
    mock_book_instance.custom_ncx_elements = "" # Initialize for SUT
    mock_create_book.return_value = mock_book_instance
    
    # Mock EpubHtml for chapters
    mock_c1 = mocker.MagicMock(spec=epub.EpubHtml)
    mock_c1.file_name = "chap_01.xhtml"
    mock_c1.title = "Chapter 1"
    
    mock_c2 = mocker.MagicMock(spec=epub.EpubHtml)
    mock_c2.file_name = "chap_02.xhtml"
    mock_c2.title = "Chapter 2"

    # Mock the epub.EpubHtml class to control chapter instances created by SUT
    # and to capture their details if needed.
    # SUT creates c1, c2 directly. We need to ensure these are MagicMocks if we want to inspect them.
    # However, the SUT adds them to book.items. We can check that.
    
    # Let SUT create its own EpubHtml items for chapters. We'll check them via add_item.
    created_items_by_sut = []
    def capture_added_item(item):
        created_items_by_sut.append(item)
        # Important: return the item itself if add_item is expected to return it,
        # or None if it's a method that doesn't return the item.
        # For MagicMock, the default return is another MagicMock, which is fine here.

    mock_book_instance.add_item = mocker.MagicMock(side_effect=capture_added_item)


    toc.create_epub_ncx_with_pagelist(filename="test_ncx_page_list.epub")

    mock_create_book.assert_called_once()
    
    # Assert chapters were created and added
    assert len(created_items_by_sut) >= 2 # c1, c2, ncx, nav, css
    
    chapter_items_added = [item for item in created_items_by_sut if isinstance(item, epub.EpubHtml) and item.file_name.startswith("chap_")]
    assert len(chapter_items_added) == 2
    assert chapter_items_added[0].file_name == "chap_01.xhtml"
    assert chapter_items_added[1].file_name == "chap_02.xhtml"

    # Assert that book.toc was set
    assert mock_book_instance.toc is not None
    assert len(mock_book_instance.toc) == 2
    assert mock_book_instance.toc[0].href == "chap_01.xhtml"
    assert mock_book_instance.toc[1].href == "chap_02.xhtml"

    # Assert custom_ncx_elements was set
    expected_custom_ncx = """
  <pageList>
    <pageTarget type="normal" id="pt_1" value="1" playOrder="1">
      <navLabel><text>1</text></navLabel>
      <content src="chap_01.xhtml#page_1"/>
    </pageTarget>
    <pageTarget type="normal" id="pt_2" value="2" playOrder="2">
      <navLabel><text>2</text></navLabel>
      <content src="chap_01.xhtml#page_2"/>
    </pageTarget>
    <pageTarget type="normal" id="pt_3" value="3" playOrder="3">
      <navLabel><text>3</text></navLabel>
      <content src="chap_02.xhtml#page_3"/>
    </pageTarget>
    <pageTarget type="normal" id="pt_4" value="4" playOrder="4">
      <navLabel><text>4</text></navLabel>
      <content src="chap_02.xhtml#page_4"/>
    </pageTarget>
  </pageList>
"""
    assert "".join(mock_book_instance.custom_ncx_elements.split()) == "".join(expected_custom_ncx.split())

    # Assert that EpubNcx and EpubNav items were added
    assert any(isinstance(item, epub.EpubNcx) for item in created_items_by_sut)
    assert any(isinstance(item, epub.EpubNav) for item in created_items_by_sut)

    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_ncx_page_list.epub")
def test_create_epub_missing_ncx(mocker: MockerFixture):
    """Test that create_epub_missing_ncx creates an EPUB3 with NavDoc but no NCX."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')
    
    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.items = [] # To check items added
    mock_create_book.return_value = mock_book_instance
    
    mock_c_alpha = mocker.MagicMock(spec=epub.EpubHtml, file_name="c_alpha.xhtml", title="Chapter Alpha")
    mock_c_beta = mocker.MagicMock(spec=epub.EpubHtml, file_name="c_beta.xhtml", title="Chapter Beta")
    mock_add_chapters.return_value = [mock_c_alpha, mock_c_beta]

    # Mock the EpubHtml for NavDoc
    mock_nav_doc_item_instance = mocker.MagicMock(spec=epub.EpubHtml)
    mock_nav_doc_item_instance.file_name = "nav.xhtml"
    mock_nav_doc_item_instance.properties = [] # SUT appends 'nav'
    
    # Patch epub.EpubHtml to return our mock *only* when nav.xhtml is being created
    original_epub_html = epub.EpubHtml 
    def selective_epub_html_mock(title, file_name, lang):
        if file_name == "nav.xhtml":
            # Configure the mock instance that will be returned for nav.xhtml
            mock_nav_doc_item_instance.title = title
            # mock_nav_doc_item_instance.file_name = file_name # already set
            mock_nav_doc_item_instance.lang = lang
            return mock_nav_doc_item_instance
        return original_epub_html(title=title, file_name=file_name, lang=lang)

    mocker.patch('synth_data_gen.generators.epub_components.toc.epub.EpubHtml', side_effect=selective_epub_html_mock)
    
    # Capture items added to the book
    added_items_capture = []
    def capture_add_item(item):
        added_items_capture.append(item)
    mock_book_instance.add_item = mocker.MagicMock(side_effect=capture_add_item)

    toc.create_epub_missing_ncx(filename="test_missing_ncx.epub")

    mock_create_book.assert_called_once()
    mock_add_chapters.assert_called_once()
    
    # Assert EPUB version is 3.0
    assert mock_book_instance.epub_version == "3.0"

    # Assert NavDoc was created and configured
    assert mock_nav_doc_item_instance is not None
    assert mock_nav_doc_item_instance.file_name == "nav.xhtml"
    assert 'nav' in mock_nav_doc_item_instance.properties
    
    expected_nav_content_parts = [
        '<nav epub:type="toc" id="toc">',
        '<li><a href="c_alpha.xhtml">Chapter Alpha</a></li>',
        '<li><a href="c_beta.xhtml">Chapter Beta</a></li>',
        '<nav epub:type="landmarks" hidden="">',
        '<li><a epub:type="bodymatter" href="c_alpha.xhtml">Start of Content</a></li>'
    ]
    actual_nav_content_str = str(mock_nav_doc_item_instance.content)
    for part in expected_nav_content_parts:
        assert part in actual_nav_content_str
def test_create_epub_navdoc_full(mocker: MockerFixture):
    """Test that create_epub_navdoc_full creates an EPUB3 with a comprehensive NavDoc."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')

    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.items = []
    mock_book_instance.spine = []
    mock_book_instance.toc = []
    mock_create_book.return_value = mock_book_instance
    
    # Mock EpubNav specifically, as SUT creates it directly
    mock_nav_instance = mocker.MagicMock(spec=epub.EpubNav)
    mock_nav_instance.configure_mock(
        file_name="nav.xhtml",
        media_type="application/xhtml+xml",
        properties=[],
        add_item=mocker.MagicMock()
    )
    mocker.patch('synth_data_gen.generators.epub_components.toc.epub.EpubNav', return_value=mock_nav_instance)

    # Capture items added to the book instance
    added_items_to_book = []
    def capture_book_add_item(item):
        added_items_to_book.append(item)
    mock_book_instance.add_item = mocker.MagicMock(side_effect=capture_book_add_item)

    # SUT calls epub.EpubHtml for cover and chapters. These will be real instances.
    # SUT also calls epub.EpubItem for CSS. This will also be real.

    toc.create_epub_navdoc_full(filename="test_navdoc_full.epub")

    mock_create_book.assert_called_once()
    assert mock_book_instance.epub_version == "3.0"

    # Find the created items by inspecting what was added to the book
    found_cover = next((item for item in added_items_to_book if isinstance(item, epub.EpubHtml) and item.file_name == "cover.xhtml"), None)
    found_c1 = next((item for item in added_items_to_book if isinstance(item, epub.EpubHtml) and item.file_name == "ch1.xhtml"), None)
    found_c2 = next((item for item in added_items_to_book if isinstance(item, epub.EpubHtml) and item.file_name == "ch2.xhtml"), None)
    # The nav_instance added to the book should be our mock_nav_instance
    assert mock_nav_instance in added_items_to_book

    assert found_cover is not None and found_cover.title == "Cover"
    assert found_c1 is not None and found_c1.title == "Chapter 1"
    assert found_c2 is not None and found_c2.title == "Chapter 2"
    
    # Check book.toc (used by EpubNav to generate its content)
    assert len(mock_book_instance.toc) == 2
    assert mock_book_instance.toc[0].href == "ch1.xhtml"
    assert mock_book_instance.toc[0].title == "Chapter 1"
    assert mock_book_instance.toc[1].href == "ch2.xhtml"
    assert mock_book_instance.toc[1].title == "Chapter 2"

    # Spine check
    assert len(mock_book_instance.spine) == 4
    # The SUT sets spine = ['nav', cover_page] + chapters
    # 'nav' in spine refers to the EpubNav item.
    assert mock_book_instance.spine[0] == 'nav'
    assert mock_book_instance.spine[1] == found_cover
    assert mock_book_instance.spine[2] == found_c1
    assert mock_book_instance.spine[3] == found_c2
    
    # Check that CSS was added to chapters and nav_doc
    # The SUT adds main_css to cover_page, c1, c2, and default_nav (our mock_nav_instance)
    # We can check if add_item was called on these mocks/found items with the CSS
    found_css = next((item for item in added_items_to_book if isinstance(item, epub.EpubItem) and item.media_type == "text/css"), None)
    assert found_css is not None
    
    # Check add_item calls on the chapter/cover/nav items for the CSS
    # Note: found_cover, found_c1, found_c2 are real EpubHtml, so they have real add_item
    # We need to mock their add_item if we want to assert on it.
    # For simplicity, this test will assume SUT's internal add_item calls are correct if main items are structured.
    # A more granular test could mock add_item on each chapter mock.
    # For now, we check that our mock_nav_instance had add_item called.
    mock_nav_instance.add_item.assert_called_with(found_css)


    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_navdoc_full.epub")
def test_create_epub_ncx_links_to_anchors(mocker: MockerFixture):
    """Test that create_epub_ncx_links_to_anchors creates an NCX with links to anchors."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')

    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.items = []
    mock_book_instance.spine = []
    mock_book_instance.toc = [] 
    mock_create_book.return_value = mock_book_instance

    mock_c1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="c1_anchors.xhtml", title="Chapter One")
    mock_c2 = mocker.MagicMock(spec=epub.EpubHtml, file_name="c2_anchors.xhtml", title="Chapter Two")
    mock_add_chapters.return_value = [mock_c1, mock_c2]
    
    added_items_capture = []
    def capture_add_item(item):
        added_items_capture.append(item)
    mock_book_instance.add_item = mocker.MagicMock(side_effect=capture_add_item)

    toc.create_epub_ncx_links_to_anchors(filename="test_ncx_links_to_anchors.epub")

    mock_create_book.assert_called_once()
    mock_add_chapters.assert_called_once()

    # Assert ToC structure
    # book.toc = (
    #     (toc_c1_main, (toc_c1_s1_1, toc_c1_s1_2)),
    #     (toc_c2_main, (toc_c2_s2_1,))
    # )
    assert mock_book_instance.toc is not None
    assert len(mock_book_instance.toc) == 2

    # Chapter 1 main link and its children
    c1_main_tuple = mock_book_instance.toc[0]
    assert isinstance(c1_main_tuple, tuple)
    assert len(c1_main_tuple) == 2
    c1_main_link = c1_main_tuple[0]
    assert isinstance(c1_main_link, epub.Link)
    assert c1_main_link.href == "c1_anchors.xhtml#main_title"
    assert c1_main_link.title == "Chapter One: Anchors Away"
    assert c1_main_link.uid == "c1_main_anchor"

    c1_children_tuple = c1_main_tuple[1]
    assert isinstance(c1_children_tuple, tuple)
    assert len(c1_children_tuple) == 2
    
    c1_s1_1_link = c1_children_tuple[0]
    assert isinstance(c1_s1_1_link, epub.Link)
    assert c1_s1_1_link.href == "c1_anchors.xhtml#sec1_1"
    assert c1_s1_1_link.title == "Section 1.1"
    assert c1_s1_1_link.uid == "c1_s1_1_anchor"

    c1_s1_2_link = c1_children_tuple[1]
    assert isinstance(c1_s1_2_link, epub.Link)
    assert c1_s1_2_link.href == "c1_anchors.xhtml#sec1_2"
    assert c1_s1_2_link.title == "Section 1.2"
    assert c1_s1_2_link.uid == "c1_s1_2_anchor"

    # Chapter 2 main link and its children
    c2_main_tuple = mock_book_instance.toc[1]
    assert isinstance(c2_main_tuple, tuple)
    assert len(c2_main_tuple) == 2
    c2_main_link = c2_main_tuple[0]
    assert isinstance(c2_main_link, epub.Link)
    assert c2_main_link.href == "c2_anchors.xhtml#chap2_title"
    assert c2_main_link.title == "Chapter Two: More Anchors"
    assert c2_main_link.uid == "c2_main_anchor"

    c2_children_tuple = c2_main_tuple[1]
    assert isinstance(c2_children_tuple, tuple)
    assert len(c2_children_tuple) == 1

    c2_s2_1_link = c2_children_tuple[0]
    assert isinstance(c2_s2_1_link, epub.Link)
    assert c2_s2_1_link.href == "c2_anchors.xhtml#sec2_1"
    assert c2_s2_1_link.title == "Section 2.1"
    assert c2_s2_1_link.uid == "c2_s2_1_anchor"

    # Assert NCX and Nav items were added
    assert any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
    assert any(isinstance(item, epub.EpubNav) for item in added_items_capture)

    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_ncx_links_to_anchors.epub")
def test_create_epub_ncx_problematic_entries(mocker: MockerFixture):
    """Test that create_epub_ncx_problematic_entries creates an NCX with a very long title."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')

    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.items = []
    mock_book_instance.spine = []
    mock_book_instance.toc = [] 
    mock_create_book.return_value = mock_book_instance

    long_title = "This is an excessively long title for a chapter that really should have been summarized, but for the sake of testing problematic NCX entries, we are putting a whole paragraph, or at least a very long sentence, into the navLabel text to see how parsers and reading systems handle such an edge case. It might be truncated, or it might cause display issues, or it might be handled perfectly fine. The point is to test the boundaries and robustness of the system when faced with non-standard or poorly formed metadata within the NCX Table of Contents structure."
    mock_c1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="c1_problem.xhtml", title="Normal Chapter")
    mock_c2_problem = mocker.MagicMock(spec=epub.EpubHtml, file_name="c2_problem.xhtml", title=long_title)
    mock_c3 = mocker.MagicMock(spec=epub.EpubHtml, file_name="c3_problem.xhtml", title="Another Chapter")
    
    mock_add_chapters.return_value = [mock_c1, mock_c2_problem, mock_c3]
    
    added_items_capture = []
    def capture_add_item(item):
        added_items_capture.append(item)
    mock_book_instance.add_item = mocker.MagicMock(side_effect=capture_add_item)

    toc.create_epub_ncx_problematic_entries(filename="test_ncx_problematic_entries.epub")

    mock_create_book.assert_called_once()
    mock_add_chapters.assert_called_once()

    # Assert ToC structure and content
    assert mock_book_instance.toc is not None
    assert len(mock_book_instance.toc) == 3
    
    assert mock_book_instance.toc[0].href == "c1_problem.xhtml"
    assert mock_book_instance.toc[0].title == "Normal Chapter"
    assert mock_book_instance.toc[0].uid == "c1_problem_toc"
    
    assert mock_book_instance.toc[1].href == "c2_problem.xhtml"
    assert mock_book_instance.toc[1].title == long_title
    assert mock_book_instance.toc[1].uid == "c2_problem_toc"

    assert mock_book_instance.toc[2].href == "c3_problem.xhtml"
    assert mock_book_instance.toc[2].title == "Another Chapter"
    assert mock_book_instance.toc[2].uid == "c3_problem_toc"

    # Assert NCX and Nav items were added
    assert any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
    assert any(isinstance(item, epub.EpubNav) for item in added_items_capture)

    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_ncx_problematic_entries.epub")
def test_create_epub_ncx_inconsistent_depth(mocker: MockerFixture):
    """Test that create_epub_ncx_inconsistent_depth creates a flat NCX for potentially nested content."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')

    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.items = []
    mock_book_instance.spine = []
    mock_book_instance.toc = [] 
    mock_create_book.return_value = mock_book_instance

    mock_p1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="p1_depth.xhtml", title="Part I")
    mock_p1c1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="p1c1_depth.xhtml", title="Chapter 1 (Under Part I)")
    mock_c2 = mocker.MagicMock(spec=epub.EpubHtml, file_name="c2_depth.xhtml", title="Standalone Chapter 2")
    mock_c2s1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="c2s1_depth.xhtml", title="Section 2.1 (Under Chapter 2)")
    mock_c3 = mocker.MagicMock(spec=epub.EpubHtml, file_name="c3_depth.xhtml", title="Standalone Chapter 3")
    
    mock_add_chapters.return_value = [mock_p1, mock_p1c1, mock_c2, mock_c2s1, mock_c3]
    
    added_items_capture = []
    def capture_add_item(item):
        added_items_capture.append(item)
    mock_book_instance.add_item = mocker.MagicMock(side_effect=capture_add_item)

    toc.create_epub_ncx_inconsistent_depth(filename="test_ncx_inconsistent_depth.epub")

    mock_create_book.assert_called_once()
    mock_add_chapters.assert_called_once()

    # Assert ToC structure is flat as defined in SUT
    assert mock_book_instance.toc is not None
    assert len(mock_book_instance.toc) == 5 
    
    expected_toc_data = [
        {"href": "p1_depth.xhtml", "title": "Part I", "uid": "p1_d_id"},
        {"href": "p1c1_depth.xhtml", "title": "Chapter 1 (Under Part I)", "uid": "p1c1_d_id"},
        {"href": "c2_depth.xhtml", "title": "Standalone Chapter 2", "uid": "c2_d_id"},
        {"href": "c2s1_depth.xhtml", "title": "Section 2.1 (Under Chapter 2)", "uid": "c2s1_d_id"},
        {"href": "c3_depth.xhtml", "title": "Standalone Chapter 3", "uid": "c3_d_id"}
    ]

    for i, actual_link in enumerate(mock_book_instance.toc):
        assert isinstance(actual_link, epub.Link)
        assert actual_link.href == expected_toc_data[i]["href"]
        assert actual_link.title == expected_toc_data[i]["title"]
        assert actual_link.uid == expected_toc_data[i]["uid"]
        # Ensure no nesting in the direct book.toc list
        assert not isinstance(actual_link, tuple)


    # Assert NCX and Nav items were added
    assert any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
    assert any(isinstance(item, epub.EpubNav) for item in added_items_capture)

    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_ncx_inconsistent_depth.epub")
def test_create_epub_ncx_lists_footnote_files(mocker: MockerFixture):
    """Test that create_epub_ncx_lists_footnote_files creates an NCX listing footnote files."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters_util = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')

    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.items = []
    mock_book_instance.spine = []
    mock_book_instance.toc = [] 
    mock_create_book.return_value = mock_book_instance

    # Mock main chapter
    mock_main_c1 = mocker.MagicMock(spec=epub.EpubHtml, file_name="text_c1.xhtml", title="Main Text Chapter 1")
    mock_add_chapters_util.return_value = [mock_main_c1] # _add_epub_chapters returns a list

    # SUT creates footnote EpubHtml items directly. We'll capture them via add_item.
    added_items_capture = []
    # Mock add_item on the book instance to capture all items
    original_add_item = mock_book_instance.add_item
    def capture_add_item_side_effect(item):
        added_items_capture.append(item)
        return original_add_item(item) # Call the original mock's behavior if needed
    mock_book_instance.add_item = mocker.MagicMock(side_effect=capture_add_item_side_effect)
    
    # SUT creates footnote EpubHtml items directly. We will find them in added_items_capture.
    # No need to mock epub.EpubHtml globally for this test.

    toc.create_epub_ncx_lists_footnote_files(filename="test_ncx_lists_footnote_files.epub")

    mock_create_book.assert_called_once()
    mock_add_chapters_util.assert_called_once() # For the main chapter

    # Assert footnote pages were created and added by finding them in the captured items
    fn1_page_found = next((item for item in added_items_capture if isinstance(item, epub.EpubHtml) and item.file_name == "footnotes/fn_c1_01.xhtml"), None)
    fn2_page_found = next((item for item in added_items_capture if isinstance(item, epub.EpubHtml) and item.file_name == "footnotes/fn_c1_02.xhtml"), None)
    
    assert fn1_page_found is not None, "Footnote page 1 not found in added items"
    assert fn2_page_found is not None, "Footnote page 2 not found in added items"
    assert fn1_page_found.title == "Footnote 1-1" # Check title if needed
    assert fn2_page_found.title == "Footnote 1-2"
    
    # Assert ToC structure
    assert mock_book_instance.toc is not None
    assert len(mock_book_instance.toc) == 3
    
    assert mock_book_instance.toc[0].href == "text_c1.xhtml"
    assert mock_book_instance.toc[0].title == "Main Text Chapter 1"
    assert mock_book_instance.toc[0].uid == "text_c1_toc"
    
    assert mock_book_instance.toc[1].href == "footnotes/fn_c1_01.xhtml"
    assert mock_book_instance.toc[1].title == "Footnote 1 (File)"
    assert mock_book_instance.toc[1].uid == "fn1_file_toc"

    assert mock_book_instance.toc[2].href == "footnotes/fn_c1_02.xhtml"
    assert mock_book_instance.toc[2].title == "Footnote 2 (File)"
    assert mock_book_instance.toc[2].uid == "fn2_file_toc"

    # Assert NCX and Nav items were added
    assert any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
    assert any(isinstance(item, epub.EpubNav) for item in added_items_capture)
    
    # Assert spine order
    assert mock_main_c1 in mock_book_instance.spine
    assert fn1_page_found in mock_book_instance.spine # Corrected variable name
    assert fn2_page_found in mock_book_instance.spine # Corrected variable name
    assert 'nav' in mock_book_instance.spine # Or the nav item itself

    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_ncx_lists_footnote_files.epub")
def test_create_epub_html_toc_p_tags(mocker: MockerFixture):
    """Test that create_epub_html_toc_p_tags creates an HTML ToC with <p> tags and classes."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters_util = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')

    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.items = []
    mock_book_instance.spine = []
    mock_book_instance.toc = [] 
    mock_create_book.return_value = mock_book_instance

    # Mock chapters returned by _add_epub_chapters
    mock_chapters_list = [mocker.MagicMock(spec=epub.EpubHtml, file_name=f"file_{i}.xhtml", title=f"Title {i}") for i in range(5)]
    mock_add_chapters_util.return_value = mock_chapters_list
    
    added_items_capture = []
    def capture_add_item(item):
        added_items_capture.append(item)
    mock_book_instance.add_item = mocker.MagicMock(side_effect=capture_add_item)

    # SUT creates the HTML ToC page directly. We'll find it in added_items_capture.
    
    toc.create_epub_html_toc_p_tags(filename="test_html_toc_p_tags.epub")

    mock_create_book.assert_called_once()
    mock_add_chapters_util.assert_called_once()

    # Find the HTML ToC page
    html_toc_page_found = next((item for item in added_items_capture if isinstance(item, epub.EpubHtml) and item.file_name == "toc_p_style.xhtml"), None)
    assert html_toc_page_found is not None, "HTML ToC page (toc_p_style.xhtml) not found."
    assert html_toc_page_found.title == "Table of Contents (P-Tag Style)"

    # Check content of the HTML ToC page
    expected_html_content_parts = [
        '<p class="toc-part"><a href="part1.xhtml">Part I: The Groundwork</a></p>',
        '<p class="toc-chapter"><a href="part1_chap1.xhtml">Chapter 1: First Principles</a></p>',
        '<p class="toc-section"><a href="part1_chap1.xhtml#sec1">Section 1.1: Initial Thoughts</a></p>',
        '<p class="toc-chapter"><a href="part1_chap2.xhtml">Chapter 2: Second Principles</a></p>',
        '<p class="toc-part"><a href="part2.xhtml">Part II: The Structure</a></p>',
        '<p class="toc-chapter"><a href="part2_chap1.xhtml">Chapter 3: Building Blocks</a></p>'
    ]
    actual_content_str = str(html_toc_page_found.content)
    for part in expected_html_content_parts:
        assert part in actual_content_str

    # Assert NCX and Nav items were added
    assert any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
    assert any(isinstance(item, epub.EpubNav) for item in added_items_capture)

    # Assert basic NCX ToC was set up (SUT sets this up as a nested structure)
    assert len(mock_book_instance.toc) == 2 # SUT creates a 2-item top-level ToC

    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_html_toc_p_tags.epub")
def test_create_epub_html_toc_non_linked(mocker: MockerFixture):
    """Test that create_epub_html_toc_non_linked creates an HTML ToC with non-linked entries."""
    mock_write_file = mocker.patch('synth_data_gen.generators.epub_components.toc._write_epub_file')
    mock_add_chapters_util = mocker.patch('synth_data_gen.generators.epub_components.toc._add_epub_chapters')
    mock_create_book = mocker.patch('synth_data_gen.generators.epub_components.toc._create_epub_book')

    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.items = []
    mock_book_instance.spine = []
    mock_book_instance.toc = [] 
    mock_create_book.return_value = mock_book_instance

    # Mock chapters returned by _add_epub_chapters
    mock_chapters_list = [mocker.MagicMock(spec=epub.EpubHtml, file_name=f"file_{i}.xhtml", title=f"Title {i}") for i in range(3)]
    mock_add_chapters_util.return_value = mock_chapters_list
    
    added_items_capture = []
    def capture_add_item(item):
        added_items_capture.append(item)
    mock_book_instance.add_item = mocker.MagicMock(side_effect=capture_add_item)
    
    toc.create_epub_html_toc_non_linked(filename="test_html_toc_non_linked.epub")

    mock_create_book.assert_called_once()
    mock_add_chapters_util.assert_called_once()

    # Find the HTML ToC page
    html_toc_page_found = next((item for item in added_items_capture if isinstance(item, epub.EpubHtml) and item.file_name == "toc_non_linked.xhtml"), None)
    assert html_toc_page_found is not None, "HTML ToC page (toc_non_linked.xhtml) not found."
    assert html_toc_page_found.title == "Table of Contents (Non-Linked)"

    # Check content of the HTML ToC page
    expected_html_content_parts = [
        "<h1>Table of Contents (Non-Linked)</h1>",
        "<li>Chapter 1: The Adventure Begins</li>",
        "<li>Chapter 2: The Plot Thickens</li>",
        "<li>Chapter 3: The Grand Finale</li>"
    ]
    actual_content_str = str(html_toc_page_found.content)
    for part in expected_html_content_parts:
        assert part in actual_content_str
    assert "<a href" not in actual_content_str # Ensure no links

    # Assert NCX and Nav items were added
    assert any(isinstance(item, epub.EpubNcx) for item in added_items_capture)
    assert any(isinstance(item, epub.EpubNav) for item in added_items_capture)

    # Assert basic NCX ToC was set up
    assert len(mock_book_instance.toc) == 3 

    mock_write_file.assert_called_once()
    assert mock_write_file.call_args[0][1].endswith("toc/test_html_toc_non_linked.epub")
def test_create_ncx_basic_structure(mocker: MockerFixture):
    """Test that create_ncx generates a basic NCX structure."""
    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.uid = "test_uid"
    mock_book_instance.title = "Test Book Title"
    mock_book_instance.toc = [] # Will be populated by create_ncx

    chapters_data = [
        {'title': 'Chapter 1', 'href': 'ch1.xhtml', 'uid': 'ch1_uid', 'children': []},
        {'title': 'Chapter 2', 'href': 'ch2.xhtml', 'uid': 'ch2_uid', 'children': []}
    ]

    toc_settings = {
        "style": "ncx_simple", # Corresponds to what create_ncx might expect
        "max_depth": 3,
        "include_landmarks": False, # Not relevant for basic NCX
        "include_page_list_in_toc": False, # Not for basic NCX
        "ncx_problematic_label_chance": 0.0,
        "ncx_list_footnote_files_chance": 0.0
    }

    # Call the SUT
    ncx_item = toc.create_ncx(mock_book_instance, chapters_data, toc_settings)

    assert isinstance(ncx_item, epub.EpubNcx)
    assert ncx_item.file_name == 'toc.ncx'
    
    # Basic check for NCX content structure (can be more detailed)
    # For now, we'll check if the book's toc attribute was populated as expected by create_ncx
    # This assumes create_ncx will populate book.toc with epub.Link objects or nested tuples
    
    # The SUT `create_ncx` is expected to populate `book_instance.toc`
    # with a structure that `ebooklib` then uses to generate the NCX XML.
    # Let's assert the structure of `book_instance.toc`
    
    assert len(mock_book_instance.toc) == 2
def test_create_ncx_nested_structure(mocker: MockerFixture):
    """Test that create_ncx generates a nested NCX structure."""
    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    mock_book_instance.uid = "test_nested_uid"
    mock_book_instance.title = "Test Nested Book Title"
    mock_book_instance.toc = []

    chapters_data = [
        {'title': 'Part 1', 'href': 'p1.xhtml', 'uid': 'p1_uid', 'children': [
            {'title': 'Chapter 1.1', 'href': 'p1c1.xhtml', 'uid': 'p1c1_uid', 'children': [
                {'title': 'Section 1.1.1', 'href': 'p1c1s1.xhtml', 'uid': 'p1c1s1_uid', 'children': []}
            ]},
            {'title': 'Chapter 1.2', 'href': 'p1c2.xhtml', 'uid': 'p1c2_uid', 'children': []}
        ]},
        {'title': 'Part 2', 'href': 'p2.xhtml', 'uid': 'p2_uid', 'children': []}
    ]

    toc_settings = {
        "style": "ncx_deeply_nested", 
        "max_depth": 3,
        "include_landmarks": False,
        "include_page_list_in_toc": False,
        "ncx_problematic_label_chance": 0.0,
        "ncx_list_footnote_files_chance": 0.0
    }

    ncx_item = toc.create_ncx(mock_book_instance, chapters_data, toc_settings)

    assert isinstance(ncx_item, epub.EpubNcx)
    assert ncx_item.file_name == 'toc.ncx'

    # Assert the nested structure of book.toc
    assert len(mock_book_instance.toc) == 2 # Part 1, Part 2

    # Part 1
    part1_tuple = mock_book_instance.toc[0]
    assert isinstance(part1_tuple, tuple), "Part 1 should be a tuple (Link, children_tuple)"
    assert len(part1_tuple) == 2, "Part 1 tuple should have 2 elements (Link, children_tuple)"
    part1_link = part1_tuple[0]
    assert isinstance(part1_link, epub.Link), "First element of Part 1 tuple should be a Link"
    assert part1_link.title == "Part 1"
    assert part1_link.href == "p1.xhtml"

    part1_children_tuple = part1_tuple[1]
    assert isinstance(part1_children_tuple, tuple)
    assert len(part1_children_tuple) == 2 # Chapter 1.1, Chapter 1.2

    # Chapter 1.1 (under Part 1)
    chapter1_1_tuple = part1_children_tuple[0]
    assert isinstance(chapter1_1_tuple, tuple)
    assert len(chapter1_1_tuple) == 2
    chapter1_1_link = chapter1_1_tuple[0]
    assert isinstance(chapter1_1_link, epub.Link)
    assert chapter1_1_link.title == "Chapter 1.1"
    
    chapter1_1_children_tuple = chapter1_1_tuple[1]
    assert isinstance(chapter1_1_children_tuple, tuple)
    assert len(chapter1_1_children_tuple) == 1 # Section 1.1.1

    # Section 1.1.1 (under Chapter 1.1)
    section1_1_1_link = chapter1_1_children_tuple[0] # No children, so it's a direct link
    assert isinstance(section1_1_1_link, epub.Link)
    assert section1_1_1_link.title == "Section 1.1.1"

    # Chapter 1.2 (under Part 1)
    chapter1_2_link = part1_children_tuple[1] # No children, so it's a direct link
    assert isinstance(chapter1_2_link, epub.Link)
    assert chapter1_2_link.title == "Chapter 1.2"

    # Part 2
    part2_link = mock_book_instance.toc[1] # No children, so it's a direct link
    assert isinstance(part2_link, epub.Link)
    assert part2_link.title == "Part 2"
    assert part2_link.href == "p2.xhtml"
def test_create_nav_document_basic_structure(mocker: MockerFixture):
    """Test that create_nav_document generates a basic NAV document structure."""
    mock_book_instance = mocker.MagicMock(spec=epub.EpubBook)
    # Minimal book attributes needed by SUT
    mock_book_instance.title = "Test Nav Book"
    mock_book_instance.lang = "en"
    mock_book_instance.uid = "test_nav_uid"
    mock_book_instance.toc = [] # Will be populated by create_nav_document or its helpers

    chapters_data = [
        {'title': 'Chapter 1 Nav', 'href': 'ch1_nav.xhtml', 'uid': 'ch1_nav_uid', 'children': []},
        {'title': 'Chapter 2 Nav', 'href': 'ch2_nav.xhtml', 'uid': 'ch2_nav_uid', 'children': []}
    ]
    
    toc_settings = {
        "style": "navdoc_basic", # To guide NavDoc creation
        "max_depth": 3,
        "include_landmarks": True, # Test with landmarks
        "include_page_list_in_toc": False # Test without page-list initially
    }
    epub_version = "3.0" # NavDoc is EPUB 3

    # Call the SUT
    nav_item = toc.create_nav_document(mock_book_instance, chapters_data, toc_settings, epub_version)

    assert isinstance(nav_item, epub.EpubHtml) # NAV Doc is an EpubHtml item with 'nav' property
    assert nav_item.file_name == 'nav.xhtml' # Default name for EpubNav / NavDoc HTML
    assert nav_item.media_type == 'application/xhtml+xml'
    assert 'nav' in nav_item.properties
    
    # Check content of the NAV document
    # This will be a string of XHTML. We need to parse or check for key elements.
    # For now, let's check for some expected substrings.
    nav_content = nav_item.content.decode('utf-8') # Assuming content is bytes

    assert '<nav epub:type="toc"' in nav_content
    assert '<h1>Table of Contents</h1>' in nav_content # Default title
    assert '<li><a href="ch1_nav.xhtml">Chapter 1 Nav</a></li>' in nav_content
    assert '<li><a href="ch2_nav.xhtml">Chapter 2 Nav</a></li>' in nav_content
    
    assert '<nav epub:type="landmarks"' in nav_content
    # A basic landmark might be to the first chapter if no other landmarks are defined
    # The SUT's placeholder might not generate this correctly yet.
    # This test is designed to FAIL with the placeholder SUT.

    # A more thorough test would involve parsing ncx_item.content (XML)
    # For now, this checks the intermediate structure set on the book object.
    # The actual XML generation is handled by ebooklib based on book.toc and book.custom_ncx_elements
    # The current placeholder SUT for create_ncx might not set book.toc correctly.
    # This test is designed to FAIL with the placeholder SUT.