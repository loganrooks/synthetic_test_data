import os
from ebooklib import epub, ITEM_DOCUMENT
from synth_data_gen.common.utils import _add_epub_chapters, _write_epub_file

def create_epub2_with_guide(filename="epub2_with_guide.epub", write_file=True):
    book = epub.EpubBook()
    book.set_identifier("urn:uuid:sample-epub2-guide")
    book.set_title("Sample EPUB2 with Guide")
    book.set_language("en")

    # Create a cover page (placeholder)
    # Ensure UIDs are unique and used consistently for .id
    cover_xhtml = epub.EpubHtml(title='Cover', file_name='cover.xhtml', lang='en', uid='cover_page')
    cover_xhtml.content = b"<html><head><title>Cover</title></head><body><img src='images/cover.jpg' alt='Cover Image'/></body></html>"
    book.add_item(cover_xhtml)

    # Create chapter
    chapter1_content = "<h1>Chapter 1</h1><p>This is the first chapter with a guide reference.</p>"
    chapter1_details = {
        "title": "Chapter 1",
        "file_name": "chapter1.xhtml",
        "content": chapter1_content.encode('utf-8'), 
        "uid": "ch1" # This uid will be used for the EpubHtml item's id and the Link's uid
    }
    chapters_details = [chapter1_details]
    epub_html_chapters, toc_link_items = _add_epub_chapters(book, chapters_details, {}) 

    # Create NAV document (HTML ToC for guide, also used by EPUB3 if it were EPUB3)
    nav_xhtml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head>
<title>Table of Contents</title>
</head>
<body>
<nav epub:type="toc" id="toc_html">
  <h2>Table of Contents</h2>
  <ol>
    <li><a href="chapter1.xhtml">Chapter 1</a></li>
  </ol>
</nav>
<nav epub:type="landmarks" hidden="hidden">
  <h2>Landmarks</h2>
  <ol>
    <li><a epub:type="cover" href="cover.xhtml">Cover</a></li>
    <li><a epub:type="bodymatter" href="chapter1.xhtml">Beginning</a></li>
  </ol>
</nav>
</body>
</html>
"""
    nav_doc = epub.EpubHtml(title='Table of Contents', file_name='nav.xhtml', lang='en', uid='nav_xhtml_toc') 
    nav_doc.content = nav_xhtml_content.encode('utf-8') 
    book.add_item(nav_doc)
    
    # Set NCX data (machine-readable ToC for EPUB2)
    # toc_link_items is a list of epub.Link objects from _add_epub_chapters
    book.toc = tuple(toc_link_items)
    book.add_item(epub.EpubNcx()) # Explicitly add NCX item using the correct class
    
    # Define Guide items (EPUB2 specific semantic references)
    book.guide = [
        {'type': 'cover', 'title': 'Cover Image', 'href': 'cover.xhtml'},
        {'type': 'toc', 'title': 'Table of Contents', 'href': 'nav.xhtml'}, # Points to the HTML ToC
        {'type': 'text', 'title': 'Beginning', 'href': 'chapter1.xhtml'} # Main content start
    ]

    # Define Spine (linear reading order)
    # Ensure UIDs match those of items added to book.items
    # The nav_doc (HTML ToC) is often included in the spine for EPUB2 if it's meant to be readable.
    book.spine = [nav_doc.id, epub_html_chapters[0].id] 

    if write_file:
        _write_epub_file(book, filename)
    return book

def create_epub_opf_specific_meta(filename="opf_specific_meta.epub", write_file=True):
    book = epub.EpubBook()
    book.set_identifier("urn:uuid:sample-opf-meta")
    book.set_title("Sample OPF Specific Metadata")
    book.set_language("en")

    # Add some OPF specific metadata
    # These are added to the <metadata> section of the .opf file
    book.add_metadata('OPF', 'meta', '', {'name': 'calibre:series', 'content': 'My Test Series'})
    book.add_metadata('OPF', 'meta', '', {'name': 'calibre:series_index', 'content': '1'})
    book.add_metadata('DC', 'modified', '2024-01-01T00:00:00Z')
    # Example for ibooks specific metadata (though this might need a specific namespace handling by ebooklib)
    # book.add_metadata(None, 'meta', '', {'property': 'ibooks:version', 'content': '1.0.0'})


    # Add a dummy chapter to make it a valid EPUB
    chapter1_content = "<h1>Chapter 1</h1><p>Content for OPF meta test.</p>"
    chapter1_details = {
        "title": "Chapter 1",
        "file_name": "c1.xhtml",
        "content": chapter1_content.encode('utf-8'),
        "uid": "c1_opf"
    }
    epub_chapters, toc_links = _add_epub_chapters(book, [chapter1_details], {})
    book.toc = tuple(toc_links)
    book.spine = [epub_chapters[0].id]
    book.add_item(epub.EpubNcx())


    if write_file:
        _write_epub_file(book, filename)
    return book

def create_epub_spine_pagemap_ref(filename="spine_pagemap_ref.epub", write_file=True):
    book = epub.EpubBook()
    book.set_identifier("urn:uuid:sample-spine-pagemap")
    book.set_title("Sample EPUB with Spine Page Map")
    book.set_language("en")

    # Add a dummy chapter
    chapter1_content = "<h1>Chapter 1</h1><p>Content for spine page-map test.</p>"
    chapter1_details = {
        "title": "Chapter 1",
        "file_name": "c1_pagemap.xhtml",
        "content": chapter1_content.encode('utf-8'),
        "uid": "c1_pm"
    }
    epub_chapters, toc_links = _add_epub_chapters(book, [chapter1_details], {})
    book.toc = tuple(toc_links)
    
    # Create page-map.xml content
    # For simplicity, assume page 1 of c1_pagemap.xhtml is the target
    page_map_content = """<?xml version="1.0" encoding="UTF-8"?>
<page-map xmlns="http://www.idpf.org/2007/opf">
    <page name="1" href="c1_pagemap.xhtml"/>
</page-map>
""".encode('utf-8')

    # Create EpubItem for page-map.xml
    page_map_item = epub.EpubItem(
        uid="page_map",
        file_name="page-map.xml",
        media_type="application/oebps-page-map+xml", # Correct media type
        content=page_map_content
    )
    book.add_item(page_map_item)

    # Set spine, including the page-map reference
    # The 'page_map' attribute in the spine tuple refers to the UID of the page_map_item
    book.spine = [(epub_chapters[0].id, 'yes', 'page_map')] # Example: linear='yes', page_map='page_map_uid'
    # According to IDPF OPF 2.0.1, the spine item can have a page-map attribute.
    # However, ebooklib's spine is a list of UIDs or (UID, linear_value).
    # For page-map, it's typically an attribute on the <spine> element itself: <spine toc="ncx" page-map="page_map_uid">
    # ebooklib handles this via book.page_map = page_map_item.id (or page_map_item.file_name if preferred by some readers)
    
    book.page_map = page_map_item.id # Set the page_map attribute on the book object for ebooklib

    book.add_item(epub.EpubNcx())

    if write_file:
        _write_epub_file(book, filename)
    return book

def create_epub_structure_split_files(filename_pattern="split_file_chapter_{}.epub", num_splits=3, write_files=True):
    books = []
    for i in range(1, num_splits + 1):
        book = epub.EpubBook()
        current_filename = filename_pattern.format(i)
        
        book.set_identifier(f"urn:uuid:sample-split-file-{i}")
        book.set_title(f"Sample Split EPUB - Part {i}")
        book.set_language("en")

        chapter_content = f"<h1>Chapter for Split File {i}</h1><p>This is content for part {i}.</p>"
        chapter_details = {
            "title": f"Chapter Part {i}",
            "file_name": f"split_chap_{i}.xhtml",
            "content": chapter_content.encode('utf-8'),
            "uid": f"split_ch_{i}"
        }
        
        epub_chapters, toc_links = _add_epub_chapters(book, [chapter_details], {})
        book.toc = tuple(toc_links)
        book.spine = [epub_chapters[0].id]
        book.add_item(epub.EpubNcx())

        if write_files:
            _write_epub_file(book, current_filename)
        books.append(book)
    return books

def create_epub_structure_calibre_artifacts(filename="calibre_artifacts.epub", write_file=True):
    book = epub.EpubBook()
    book.set_identifier("urn:uuid:sample-calibre-artifacts-minimal")
    book.set_title("Minimal EPUB with Calibre Artifact")
    book.set_language("en")

    # Add ONE Calibre-specific metadata tag
    book.add_metadata(None, 'meta', None, {'name': 'calibre:series', 'content': 'Minimal Debug Series'})

    # Add a single minimal chapter
    chapter_content = "<h1>Minimal Chapter</h1><p>Content.</p>"
    chapter_details = {
        "title": "Minimal Chapter",
        "file_name": "chap_minimal.xhtml",
        "content": chapter_content.encode('utf-8'),
        "uid": "chap_min"
    }
    # Use _add_epub_chapters which adds to book.items
    epub_chapters, toc_links = _add_epub_chapters(book, [chapter_details], {})
    
    # Explicitly set spine
    book.spine = [epub_chapters[0].id]
    
    # Set toc for NCX generation
    book.toc = tuple(toc_links)

    # OPF is handled by ebooklib automatically.
    # Explicitly add NCX as it might be referenced by default in the spine.
    book.add_item(epub.EpubNcx())

    if write_file:
        _write_epub_file(book, filename)
    return book

def create_epub_structure_adobe_artifacts(filename="adobe_artifacts.epub"):
    # Placeholder for SUT
    pass

def create_epub_accessibility_epub_type(filename="accessibility_epub_type.epub"):
    # Placeholder for SUT
    pass

def create_epub_minimal_metadata(filename="minimal_metadata.epub"):
    # Placeholder for SUT
    pass