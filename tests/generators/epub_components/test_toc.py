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