import os
import zipfile
from ebooklib import epub

# Define output base directory relative to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "generated") # Restored for general use

# Define absolute default paths for potential use by components
EPUB_DIR = os.path.join(BASE_OUTPUT_DIR, "epub")
PDF_DIR = os.path.join(BASE_OUTPUT_DIR, "pdf")
MD_DIR = os.path.join(BASE_OUTPUT_DIR, "markdown")

# Subdirectory names, can be used by ensure_output_directories with a dynamic base_dir
EPUB_SUBDIR_NAME = "epub" # Renamed to avoid conflict with EPUB_DIR
PDF_SUBDIR_NAME = "pdf"   # Renamed to avoid conflict with PDF_DIR
MD_SUBDIR_NAME = "markdown" # Renamed to avoid conflict with MD_DIR

def ensure_output_directories(base_dir: str):
    """Ensures all necessary output subdirectories exist within the given base_dir."""
    
    # Ensure the base_dir itself exists
    os.makedirs(base_dir, exist_ok=True)

    # Use SUBDIR_NAME constants for clarity when creating paths within the dynamic base_dir
    epub_dir_dynamic = os.path.join(base_dir, EPUB_SUBDIR_NAME)
    pdf_dir_dynamic = os.path.join(base_dir, PDF_SUBDIR_NAME)
    md_dir_dynamic = os.path.join(base_dir, MD_SUBDIR_NAME)

    os.makedirs(os.path.join(epub_dir_dynamic, "toc"), exist_ok=True)
    os.makedirs(os.path.join(epub_dir_dynamic, "headers"), exist_ok=True)
    os.makedirs(os.path.join(epub_dir_dynamic, "notes"), exist_ok=True)
    os.makedirs(os.path.join(epub_dir_dynamic, "citations_bibliography"), exist_ok=True)
    os.makedirs(os.path.join(epub_dir_dynamic, "images_fonts"), exist_ok=True)
    os.makedirs(os.path.join(epub_dir_dynamic, "structure_metadata"), exist_ok=True)
    os.makedirs(os.path.join(epub_dir_dynamic, "content_types"), exist_ok=True)
    os.makedirs(os.path.join(epub_dir_dynamic, "general_edge_cases"), exist_ok=True)

    os.makedirs(os.path.join(pdf_dir_dynamic, "text_based"), exist_ok=True)
    os.makedirs(os.path.join(pdf_dir_dynamic, "image_based_ocr"), exist_ok=True)
    os.makedirs(os.path.join(pdf_dir_dynamic, "structure"), exist_ok=True)
    os.makedirs(os.path.join(pdf_dir_dynamic, "notes"), exist_ok=True)
    os.makedirs(os.path.join(pdf_dir_dynamic, "general_edge_cases"), exist_ok=True)

    os.makedirs(os.path.join(md_dir_dynamic, "basic"), exist_ok=True)
    os.makedirs(os.path.join(md_dir_dynamic, "extended"), exist_ok=True)
    os.makedirs(os.path.join(md_dir_dynamic, "frontmatter"), exist_ok=True)
    os.makedirs(os.path.join(md_dir_dynamic, "general_edge_cases"), exist_ok=True)

def _create_epub_book(identifier, title, author="Synthetic Data Generator", lang="en", custom_metadata=None, add_default_metadata=True):
    """Helper function to create a basic EpubBook object with common metadata."""
    book = epub.EpubBook()
    if add_default_metadata:
        if identifier: book.set_identifier(identifier)
        if title: book.set_title(title)
        if lang: book.set_language(lang)
        if author: book.add_author(author)
        book.add_metadata('DC', 'publisher', 'PhiloGraph Testing Inc.')
        book.add_metadata('DC', 'date', '2025-05-09', others={'event': 'publication'})
    
    if custom_metadata: # For adding specific or overriding metadata
        for prefix, name, value, others_dict in custom_metadata: 
            book.add_metadata(prefix, name, value, others=others_dict)
    return book

def _add_epub_chapters(book, chapter_details, default_style_item=None):
    """Helper to add chapters to the book and return chapter objects.
       Can link a default style item to all chapters."""
    chapters = []
    toc_items = [] # Initialize list for ToC items
    for i, detail in enumerate(chapter_details):
        ch_title = detail.get("title", f"Chapter {i+1}")
        ch_filename = detail.get("filename", f"chap_{i+1:02}.xhtml")
        ch_content = detail.get("content", f"<h1>{ch_title}</h1><p>Content for {ch_title}.</p>")
        ch_uid = detail.get("uid", ch_filename.split('.')[0]) # Use filename as uid if not provided
        
        chapter = epub.EpubHtml(title=ch_title, file_name=ch_filename, lang=book.language, uid=ch_uid)
        if isinstance(ch_content, str):
            chapter.content = ch_content.encode('utf-8')
        else:
            chapter.content = ch_content # Assume it's already bytes
        if default_style_item:
            chapter.add_item(default_style_item)
        book.add_item(chapter)
        chapters.append(chapter)
        toc_items.append(epub.Link(ch_filename, ch_title, ch_uid)) # Create a Link for ToC
    return chapters, toc_items

def _write_epub_file(book, filepath):
    """Helper function to write the EPUB file, with basic custom file handling."""
    
    # Standard EPUB writing
    epub.write_epub(filepath, book, {})

    # Post-process to add files to META-INF or other non-OEBPS locations
    if hasattr(book, 'custom_files_to_add'):
        try:
            with zipfile.ZipFile(filepath, 'a') as epub_zip:  # Open in append mode
                for rel_path, content_bytes in book.custom_files_to_add.items():
                    # Ensure the path is treated as relative to the ZIP root
                    # For META-INF, rel_path should be e.g., "META-INF/encryption.xml"
                    epub_zip.writestr(rel_path, content_bytes)
            # print(f"Successfully added custom files to EPUB: {filepath}") # Optional: for debugging
        except Exception as e:
            print(f"Error adding custom files to EPUB {filepath}: {e}")
            # Consider re-raising or more specific error handling
    print(f"Successfully created EPUB: {filepath}")

# Call this once if common.py is imported, or ensure main runner calls it.
# For now, let's assume the main runner will call ensure_output_directories().