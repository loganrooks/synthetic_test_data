"""
This module provides functions for generating NCX and Navigation documents for EPUB files.
"""
from ebooklib import epub
from typing import List, Dict, Any, Optional, Tuple, Union

def create_ncx(book: epub.EpubBook, chapters_data: List[epub.EpubHtml], toc_settings: Dict[str, Any]) -> None:
    """
    Creates an NCX document (EpubNcx object) and populates the book.toc.
    
    Args:
        book (epub.EpubBook): The book object to add NCX to.
        chapters_data (list): A list of EpubHtml items representing the chapters
        toc_settings (dict): Configuration for ToC generation.
    """
    if not chapters_data:
        return

    # Create links for chapters
    toc_links = []
    for chapter in chapters_data:
        if hasattr(chapter, 'file_name') and hasattr(chapter, 'title'):
            uid = chapter.file_name.split('.')[0] + "_ncx_id"
            toc_links.append(epub.Link(chapter.file_name, chapter.title, uid))
    
    # Set the book's Table of Contents
    book.toc = tuple(toc_links)
    
    # Add the NCX item to the book
    ncx_item = epub.EpubNcx()
    book.add_item(ncx_item)

def create_nav_document(book: epub.EpubBook, chapters_data: List[epub.EpubHtml], toc_settings: Dict[str, Any], epub_version: str) -> Optional[epub.EpubHtml]:
    """
    Creates a Navigation Document for EPUB3.
    
    Args:
        book (epub.EpubBook): The book object
        chapters_data (list): A list of EpubHtml items representing the chapters
        toc_settings (dict): Configuration for ToC generation
        epub_version (str): The EPUB version as a string (e.g., "3.0")
        
    Returns:
        epub.EpubHtml: The navigation document item that should be added to the book
    """
    if not epub_version.startswith("3") or not chapters_data:
        return None
    
    # Function to generate HTML list items recursively
    def _generate_html_list_items(items, current_depth=1, max_depth=None):
        html_parts = []
        
        for item in items:
            if isinstance(item, epub.Link):
                link_object = item
                children_tuple = None
            elif isinstance(item, tuple) and len(item) > 0:
                if isinstance(item[0], epub.Link):
                    link_object = item[0]
                    if len(item) > 1 and isinstance(item[1], (list, tuple)):
                        children_tuple = item[1]
                    else:
                        children_tuple = None
                else:
                    continue  # Skip if not a valid tuple structure
            else:
                continue  # Skip unknown item types
                
            list_item_html = f'<li><a href="{link_object.href}">{link_object.title}</a>'
            
            # Recursively process children if they exist and depth allows
            if children_tuple and (max_depth is None or (current_depth + 1) <= max_depth):
                children_html = _generate_html_list_items(children_tuple, current_depth + 1, max_depth)
                if children_html:
                    list_item_html += f"\n<ol>\n{children_html}</ol>\n"
            
            list_item_html += "</li>"
            html_parts.append(list_item_html)
        
        return "\n".join(html_parts) if html_parts else ""
    
    # Get TOC max depth from settings
    toc_max_depth = toc_settings.get("max_depth", 3)
    
    # Generate TOC HTML
    toc_items_source = book.toc if hasattr(book, 'toc') and book.toc else []
    toc_html_items = _generate_html_list_items(toc_items_source, 1, toc_max_depth)
    
    # Create navigation document content
    book_lang = book.get_metadata("DC", "language")[0][0] if book.get_metadata("DC", "language") else "en"
    
    nav_content = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{book_lang}">
<head>
  <title>{book.title} - Navigation</title>
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Table of Contents</h1>
    <ol>
{toc_html_items}
    </ol>
  </nav>
'''
    
    # Add landmarks section if configured
    if toc_settings.get("include_landmarks", False) and chapters_data:
        first_chapter_href = chapters_data[0].file_name if hasattr(chapters_data[0], 'file_name') else '#'
        nav_content += f'''
  <nav epub:type="landmarks" hidden="">
    <h1>Landmarks</h1>
    <ol>
      <li><a epub:type="bodymatter" href="{first_chapter_href}">Start of Content</a></li>
    </ol>
  </nav>
'''
    
    # Add page list if configured
    if toc_settings.get("include_page_list_in_toc", False):
        nav_content += '''
  <nav epub:type="page-list" hidden="">
    <h1>Page List</h1>
    <ol>
      <!-- Page list items would go here -->
    </ol>
  </nav>
'''
    
    nav_content += '''
</body>
</html>'''
    
    # Create the nav document
    nav_item = epub.EpubHtml(
        title="Navigation",
        file_name="nav.xhtml",
        lang=book_lang,
        content=nav_content
    )
    nav_item.properties.append('nav')  # Mark as navigation
    
    return nav_item

def create_ncx(book: epub.EpubBook, chapters_data: List[epub.EpubHtml], toc_settings: Dict[str, Any]) -> None:
    """
    Creates an NCX document (EpubNcx object) and populates the book.toc.
    
    Args:
        book (epub.EpubBook): The book object to add NCX to.
        chapters_data (list): A list of EpubHtml items representing the chapters
        toc_settings (dict): Configuration for ToC generation.
    """
    if not chapters_data:
        return

    # Create links for chapters
    toc_links = []
    for chapter in chapters_data:
        if hasattr(chapter, 'file_name') and hasattr(chapter, 'title'):
            uid = chapter.file_name.split('.')[0] + "_ncx_id"
            toc_links.append(epub.Link(chapter.file_name, chapter.title, uid))
    
    # Set the book's Table of Contents
    book.toc = tuple(toc_links)
    
    # Add the NCX item to the book
    ncx_item = epub.EpubNcx()
    book.add_item(ncx_item)

def create_nav_document(book: epub.EpubBook, chapters_data: List[epub.EpubHtml], toc_settings: Dict[str, Any], epub_version: str) -> Optional[epub.EpubHtml]:
    """
    Creates a Navigation Document for EPUB3.
    
    Args:
        book (epub.EpubBook): The book object
        chapters_data (list): A list of EpubHtml items representing the chapters
        toc_settings (dict): Configuration for ToC generation
        epub_version (str): The EPUB version as a string (e.g., "3.0")
        
    Returns:
        epub.EpubHtml: The navigation document item that should be added to the book
    """
    if not epub_version.startswith("3") or not chapters_data:
        return None
    
    # Function to generate HTML list items recursively
    def _generate_html_list_items(items, current_depth=1, max_depth=None):
        html_parts = []
        
        for item in items:
            if isinstance(item, epub.Link):
                link_object = item
                children_tuple = None
            elif isinstance(item, tuple) and len(item) > 0:
                if isinstance(item[0], epub.Link):
                    link_object = item[0]
                    if len(item) > 1 and isinstance(item[1], (list, tuple)):
                        children_tuple = item[1]
                    else:
                        children_tuple = None
                else:
                    continue  # Skip if not a valid tuple structure
            else:
                continue  # Skip unknown item types
                
            list_item_html = f'<li><a href="{link_object.href}">{link_object.title}</a>'
            
            # Recursively process children if they exist and depth allows
            if children_tuple and (max_depth is None or (current_depth + 1) <= max_depth):
                children_html = _generate_html_list_items(children_tuple, current_depth + 1, max_depth)
                if children_html:
                    list_item_html += f"\n<ol>\n{children_html}</ol>\n"
            
            list_item_html += "</li>"
            html_parts.append(list_item_html)
        
        return "\n".join(html_parts) if html_parts else ""
    
    # Get TOC max depth from settings
    toc_max_depth = toc_settings.get("max_depth", 3)
    
    # Generate TOC HTML
    toc_items_source = book.toc if hasattr(book, 'toc') and book.toc else []
    toc_html_items = _generate_html_list_items(toc_items_source, 1, toc_max_depth)
    
    # Create navigation document content
    book_lang = book.get_metadata("DC", "language")[0][0] if book.get_metadata("DC", "language") else "en"
    
    nav_content = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{book_lang}">
<head>
  <title>{book.title} - Navigation</title>
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Table of Contents</h1>
    <ol>
{toc_html_items}
    </ol>
  </nav>
'''
    
    # Add landmarks section if configured
    if toc_settings.get("include_landmarks", False) and chapters_data:
        first_chapter_href = chapters_data[0].file_name if hasattr(chapters_data[0], 'file_name') else '#'
        nav_content += f'''
  <nav epub:type="landmarks" hidden="">
    <h1>Landmarks</h1>
    <ol>
      <li><a epub:type="bodymatter" href="{first_chapter_href}">Start of Content</a></li>
    </ol>
  </nav>
'''
    
    # Add page list if configured
    if toc_settings.get("include_page_list_in_toc", False):
        nav_content += '''
  <nav epub:type="page-list" hidden="">
    <h1>Page List</h1>
    <ol>
      <!-- Page list items would go here -->
    </ol>
  </nav>
'''
    
    nav_content += '''
</body>
</html>'''
    
    # Create the nav document
    nav_item = epub.EpubHtml(
        title="Navigation",
        file_name="nav.xhtml",
        lang=book_lang,
        content=nav_content
    )
    nav_item.properties.append('nav')  # Mark as navigation
    
    return nav_item
