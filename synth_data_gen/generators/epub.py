import os
import random # Added import
from typing import Any, Dict, List
from ebooklib import epub

from ..core.base import BaseGenerator
# Assuming utils.py contains the necessary helper functions.
# Adjust if these were moved/refactored elsewhere during initial migration.
from ..common.utils import ensure_output_directories #, _create_epub_book, _add_epub_chapters, _write_epub_file

# Import epub_components - these might be refactored into helper classes or methods
from .epub_components import (
    citations,
    content_types,
    headers,
    multimedia,
    notes,
    page_numbers,
    structure,
    toc,
)

class EpubGenerator(BaseGenerator):
    """
    Generator for EPUB files.
    """
    GENERATOR_ID = "epub"

    def get_default_specific_config(self) -> Dict[str, Any]:
        """
        Returns the default specific configuration for EPUB generation.
        Refer to specifications/synthetic_data_package_specification.md for details.
        """
        # This should reflect the defaults in the specification document
        # For brevity, returning a simplified version.
        # A more complete version would be derived from the spec.
        return {
            "chapters_config": 5,
            "sections_per_chapter_config": 2,
            "epigraph_config": 0,
            "author": "Default EPUB Author",
            "title_prefix": "Synthetic EPUB: ",
            "language": "en",
            "publisher": "SynthPress EPUB Division",
            "epub_version": 3,
            "include_ncx": "auto",
            "include_nav_doc": "auto",
            "font_embedding": {"enable": False},
            "toc_settings": {"style": "navdoc_full", "max_depth": 3, "include_landmarks": True, "include_page_list_in_toc": True},
            "page_numbering": {"style": "epub3_semantic", "link_to_page_markers": True},
            "notes_system": {"type": "footnotes_same_page", "notes_config": 0},
            "citations_bibliography": {"in_text_citation_style": "none", "bibliography_style": {"style": "dedicated_file_list"}},
            "multimedia": {"include_images": True, "images_config": 0},
            "content_elements": {
                "paragraph_styles": [{"class_name": "indent", "chance": 0.7}, {"class_name": "noindent", "chance": 0.2}],
                "heading_styles": {"chapter_title_style": "standard_h_tags", "section_header_style": "standard_h_tags"},
                "list_styles": {"include_ordered_lists": True, "include_unordered_lists": True, "list_items_config": 5, "max_list_nesting_depth": 2},
            },
            "structural_elements": {"include_front_matter": True, "include_back_matter": True},
            "typography_layout": {"base_font_family": ["Liberation Serif", "serif"], "line_spacing_multiplier": 1.5, "text_alignment": "justify"},
            "edge_cases": {} # All default to 0.0
        }

    def validate_config(self, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> bool:
        """
        Validates the EPUB specific configuration.
        """
        if not super().validate_config(specific_config, global_config):
            return False
        
        # Example: Check for required fields in epub_specific_settings
        if "epub_version" not in specific_config:
            print("Warning: epub_version not found in specific_config, using default.")
            # Or raise InvalidConfigError
        
        # Add more detailed validation based on epub_specific_settings schema
        # For example, check types, ranges, allowed values for various keys.
        # This is a placeholder for more comprehensive validation.
        return True

    def _determine_count(self, config_value: Any, element_name_for_logging: str = "element") -> int:
        """
        Determines the count of an element based on its configuration value.
        Handles integer, range object, or probabilistic object.
        """
        if isinstance(config_value, int):
            return config_value
        elif isinstance(config_value, dict):
            if "min" in config_value and "max" in config_value:
                min_val = config_value.get("min", 0)
                max_val = config_value.get("max", 0)
                if not (isinstance(min_val, int) and isinstance(max_val, int) and min_val <= max_val):
                    print(f"Warning: Invalid range for {element_name_for_logging}: {config_value}. Defaulting to 0.")
                    return 0
                return random.randint(min_val, max_val)
            elif "chance" in config_value:
                chance = config_value.get("chance", 0.0)
                # per_unit_of = config_value.get("per_unit_of", "document") # Not used in this simplified version yet
                max_total = config_value.get("max_total", 1) # Default to generating 1 if chance met
                
                if not (isinstance(chance, float) and 0.0 <= chance <= 1.0):
                    print(f"Warning: Invalid chance for {element_name_for_logging}: {chance}. Defaulting to 0.")
                    return 0
                
                if random.random() < chance:
                    # For simplicity, if chance hits, generate 1 up to max_total.
                    # A more complex version might involve another random number for count.
                    return min(1, max_total) if isinstance(max_total, int) and max_total >=0 else 1
                return 0
            else:
                print(f"Warning: Unknown dictionary structure for {element_name_for_logging} count: {config_value}. Defaulting to 0.")
                return 0
        else:
            print(f"Warning: Unknown config type for {element_name_for_logging} count: {config_value}. Defaulting to 0.")
            return 0

    def _create_chapter_content(self, book: epub.EpubBook, chapter_number: int, chapter_title: str, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> epub.EpubHtml:
        """
        Creates and adds a single chapter's content to the EPUB book.
        This is a placeholder and will be expanded with epub_components.
        """
        # Placeholder content generation
        chapter_content_html = f"<h1>{chapter_title}</h1>"
        
        # Simulate sections using _determine_count
        default_sections_config = self.get_default_specific_config().get("content_elements", {}).get("sections_per_chapter_config", 1)
        sections_config = specific_config.get("sections_per_chapter_config", default_sections_config)
        num_sections = self._determine_count(sections_config, f"sections_in_chapter_{chapter_number}")

        for j in range(num_sections):
            section_number = j + 1
            section_title = f"Section {chapter_number}.{section_number}" # Placeholder
            # self._create_section_content will eventually add to chapter_content_html or directly to book items
            self._create_section_content(book, chapter_number, section_number, section_title, specific_config, global_config)
            # For now, to keep the existing structure somewhat, we add a placeholder to the HTML.
            # This will be refined when _create_section_content is fully implemented.
            chapter_content_html += f"<!-- Section {chapter_number}.{section_number} content generated by _create_section_content -->"
        
        # Add content from content_types.py (e.g., blockquotes, lists)
        # Example: chapter_content_html += content_types.generate_blockquote(specific_config.get("content_elements", {}).get("blockquote_styles", {}))

        # Notes generation for the chapter
        notes_system_config = specific_config.get("notes_system", self.get_default_specific_config()["notes_system"])
        notes_config_value = notes_system_config.get("notes_config", 0) # Default to 0 if not present
        num_notes = self._determine_count(notes_config_value, f"notes_in_chapter_{chapter_number}")

        # Create the chapter EpubHtml item
        c = epub.EpubHtml(title=chapter_title, file_name=f'chap_{chapter_number}.xhtml', lang=specific_config.get("language", global_config.get("default_language", "en")))
        c.content = chapter_content_html # Content before notes
        
        # Add notes (placeholder call, actual note addition will modify c.content or add related items)
        if num_notes > 0: # Only call if notes are expected
            self._add_notes_to_chapter(book, c, chapter_number, num_notes, specific_config, global_config)

        # Image generation for the chapter
        multimedia_config = specific_config.get("multimedia", self.get_default_specific_config()["multimedia"])
        include_images = multimedia_config.get("include_images", False)
        if include_images:
            images_config_value = multimedia_config.get("images_config", 0)
            num_images = self._determine_count(images_config_value, f"images_in_chapter_{chapter_number}")
            if num_images > 0:
                self._add_images_to_chapter(book, c, chapter_number, num_images, specific_config, global_config)

        book.add_item(c)
        return c

    def _add_notes_to_chapter(self, book: epub.EpubBook, chapter_item: epub.EpubHtml, chapter_number: int, num_notes: int, specific_config: Dict[str, Any], global_config: Dict[str, Any]):
        """
        Adds notes to a given chapter.
        This is a placeholder and will be expanded with epub_components.notes.
        """
        # Placeholder: In a real implementation, this would generate note content
        # and integrate it into chapter_item.content or add separate note files.
        # For TDD, its existence and callability with the right num_notes are key.
        pass

    def _add_images_to_chapter(self, book: epub.EpubBook, chapter_item: epub.EpubHtml, chapter_number: int, num_images: int, specific_config: Dict[str, Any], global_config: Dict[str, Any]):
        """
        Adds images to a given chapter.
        This is a placeholder and will be expanded with epub_components.multimedia.
        """
        # Placeholder: In a real implementation, this would generate image items,
        # reference them in chapter_item.content, and add them to the book.
        pass

    def _get_font_path(self, font_name: str, specific_config: Dict[str, Any]) -> str | None:
        """
        Tries to find a font file.
        Placeholder: very simplified. Real version would search system paths, project paths etc.
        """
        # For testing, assume fonts are in a 'fonts' subdir or directly accessible if full path given
        if os.path.exists(font_name): # Allows absolute paths or paths relative to CWD for tests
            return font_name
        
        # Try common extensions if just a name is given
        common_extensions = ['.ttf', '.otf']
        for ext in common_extensions:
            if os.path.exists(font_name + ext):
                return font_name + ext
        
        # Placeholder for more sophisticated search (e.g. in a bundled 'fonts' dir)
        # print(f"Warning: Font '{font_name}' not found.")
        return None

    def _create_section_content(self, book: epub.EpubBook, chapter_number: int, section_number: int, section_title: str, specific_config: Dict[str, Any], global_config: Dict[str, Any]):
        """
        Creates and adds a single section's content within a chapter.
        This is a placeholder and will be expanded with epub_components.
        For now, it does nothing to allow tests to pass by mocking it.
        """
        # Placeholder: In a real implementation, this would generate section HTML,
        # add it to the chapter's EpubHtml item, or create separate EpubHtml items for sections.
        # For TDD purposes, its existence and callability are what's being tested initially.
        pass

    def generate(self, specific_config: Dict[str, Any], global_config: Dict[str, Any], output_path: str) -> str:
        """
        Generates a single EPUB file.
        """
        # Ensure output directory exists
        ensure_output_directories(os.path.dirname(output_path))

        book = epub.EpubBook()

        # 1. Set Metadata (from global_config and specific_config)
        book.set_identifier(specific_config.get("isbn", f"urn:uuid:{os.urandom(16).hex()}"))
        title = specific_config.get('title', 'Untitled')
        title_prefix = specific_config.get('title_prefix')
        if title_prefix:
            book.set_title(f"{title_prefix}{title}")
        else:
            book.set_title(title)
        book.set_language(specific_config.get("language", global_config.get("default_language", "en")))
        book.add_author(specific_config.get("author", global_config.get("default_author", "Unknown Author")))
        book.add_publisher(specific_config.get("publisher", global_config.get("default_publisher", "SynthPress")))
        
        # publication_date, series_name, series_number etc.

        # 2. Create Content (Chapters, Sections)
        default_chapters_config = self.get_default_specific_config()["chapters_config"]
        chapters_config_value = specific_config.get("chapters_config", default_chapters_config)
        num_chapters = self._determine_count(chapters_config_value, "chapters")

        chapters_content: List[epub.EpubHtml] = []
        for i in range(num_chapters):
            chapter_number = i + 1
            chapter_title = f"Chapter {chapter_number}" # Placeholder title
            # Actual title generation will be more complex, possibly using epub_components.structure
            
            chapter_item = self._create_chapter_content(book, chapter_number, chapter_title, specific_config, global_config)
            chapters_content.append(chapter_item)
            # book.add_item(chapter_item) # Already added in _create_chapter_content

        # 3. Create Table of Contents (NCX and/or NavDoc)
        default_specific_config = self.get_default_specific_config()
        toc_settings = specific_config.get("toc_settings", default_specific_config["toc_settings"])
        epub_version_str = str(specific_config.get("epub_version", default_specific_config["epub_version"])) # Ensure string for startswith
        
        include_ncx_flag = specific_config.get("include_ncx", default_specific_config["include_ncx"])
        include_nav_doc_flag = specific_config.get("include_nav_doc", default_specific_config["include_nav_doc"])

        actual_include_nav_doc = False
        if isinstance(include_nav_doc_flag, bool):
            actual_include_nav_doc = include_nav_doc_flag
        elif include_nav_doc_flag == "auto":
            if epub_version_str.startswith("3"):
                actual_include_nav_doc = True
        
        actual_include_ncx = False
        if isinstance(include_ncx_flag, bool):
            actual_include_ncx = include_ncx_flag
        elif include_ncx_flag == "auto":
            if epub_version_str.startswith("2"):
                actual_include_ncx = True
            elif epub_version_str.startswith("3") and not actual_include_nav_doc: # Include NCX for EPUB3 if NavDoc is not being included
                actual_include_ncx = True
        
        if actual_include_ncx:
            toc.create_ncx(book, chapters_content, toc_settings)
            # create_ncx is expected to set book.toc and add the NCX item

        if actual_include_nav_doc:
            # The test expects epub_version as an int for the mock, but config stores it as int.
            epub_version_int = specific_config.get("epub_version", default_specific_config["epub_version"])
            toc.create_nav_document(book, chapters_content, toc_settings, epub_version_int)
            # create_nav_document is expected to add the NavDoc item

        # Ensure book.toc is set if not by specific functions (e.g. if only one type of ToC is generated)
        # This is a fallback, ideally toc.create_ncx or toc.create_nav_document handles book.toc
        if not book.toc and chapters_content:
             book.toc = tuple(epub.Link(ch.file_name, ch.title, ch.file_name.split('.')[0] + "_fallback_id") for ch in chapters_content)

        # 4. Define Spine
        # Ensure 'nav' (for EpubNav) is in spine if NavDoc was created.
        # EpubNcx is not typically in the spine.
        spine_items = []
        nav_item_present_in_book = any(isinstance(item, epub.EpubNav) for item in book.items)
        if nav_item_present_in_book: # Check if EpubNav was actually added
            # Attempt to find the nav item, default to 'nav' if standard EpubNav is used
            nav_xhtml_item = next((item for item in book.items if isinstance(item, epub.EpubNav) or (hasattr(item, 'properties') and 'nav' in item.properties)), None)
            if nav_xhtml_item:
                 spine_items.append(nav_xhtml_item) # Use the actual item if found
            else: # Fallback if somehow it was added but not found by type/property
                 spine_items.append('nav')


        spine_items.extend(chapters_content)
        book.spine = spine_items

        # 5. Add CSS, Fonts (if any)
        font_embedding_config = specific_config.get("font_embedding", {})
        if font_embedding_config.get("enable"):
            font_list = font_embedding_config.get("fonts", [])
            # obfuscation_method = font_embedding_config.get("obfuscation", "none") # Not used yet

            for font_spec_name in font_list:
                font_path = self._get_font_path(font_spec_name, specific_config)
                if font_path:
                    try:
                        with open(font_path, 'rb') as f_content:
                            font_content = f_content.read()
                        
                        # Determine filename for EPUB (e.g., fonts/font_name.ttf)
                        base_font_name = os.path.basename(font_spec_name)
                        epub_font_filename = f"fonts/{base_font_name}"
                        if not base_font_name.lower().endswith(('.ttf', '.otf')):
                            epub_font_filename += ".ttf" # Default to .ttf if no extension

                        # Determine media type
                        media_type = 'application/vnd.ms-opentype' # Default for TTF/OTF
                        if epub_font_filename.lower().endswith('.otf'):
                            media_type = 'application/font-sfnt' # More generic for OTF
                        
                        font_item = epub.EpubItem(
                            uid=f"font_{base_font_name.split('.')[0]}",
                            file_name=epub_font_filename,
                            media_type=media_type,
                            content=font_content
                        )
                        book.add_item(font_item)
                    except IOError as e:
                        print(f"Warning: Could not read font file {font_path}: {e}")
        
        style = 'BODY {color: black;}' # Basic style
        # Potentially add @font-face rules here if fonts were embedded
        # For now, just a basic CSS
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

        # 6. Write EPUB file
        epub.write_epub(output_path, book, {})
        
        return output_path

# Example of how epub_components might be used (conceptual)
# This would be inside the generate method or helper methods within EpubGenerator

# def _integrate_epub_components(book, specific_config, global_config):
    # chapters_data = structure.plan_chapters_sections(specific_config, global_config)
    # generated_chapters = []
    # for chap_idx, chap_data in enumerate(chapters_data):
    #     xhtml_content = ""
    #     xhtml_content += headers.generate_chapter_header(chap_data, specific_config)
        
    #     for sec_idx, sec_data in enumerate(chap_data.get("sections", [])):
    #         xhtml_content += headers.generate_section_header(sec_data, specific_config)
    #         # Paragraphs, lists, blockquotes from content_types
    #         # Images from multimedia
    #         # Notes from notes
        
    #     # Create epub.EpubHtml item
    #     # Add to book and generated_chapters list

    # toc.build_toc_files(book, generated_chapters, specific_config)
    # multimedia.embed_fonts_images(book, specific_config)
    # citations.add_bibliography(book, specific_config) # if applicable
    # page_numbers.add_page_markers(book, generated_chapters, specific_config) # if applicable
    # structure.add_front_back_matter(book, specific_config)
    # pass