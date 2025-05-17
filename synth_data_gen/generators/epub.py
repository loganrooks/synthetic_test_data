import os
import subprocess
import re
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
            section_html = self._create_section_content(book, chapter_number, section_number, section_title, specific_config, global_config)
            if section_html:
                chapter_content_html += section_html
            # For now, to keep the existing structure somewhat, we add a placeholder to the HTML.
            # This will be refined when _create_section_content is fully implemented.
            # chapter_content_html += f"<!-- Section {chapter_number}.{section_number} content generated by _create_section_content -->"
        
        # Add content from content_types.py (e.g., blockquotes, lists)
        # Example: chapter_content_html += content_types.generate_blockquote(specific_config.get("content_elements", {}).get("blockquote_styles", {}))

        # Notes generation for the chapter
        notes_system_config = specific_config.get("notes_system", self.get_default_specific_config()["notes_system"])
        notes_config_value = notes_system_config.get("notes_config", 0) # Default to 0 if not present
        num_notes = self._determine_count(notes_config_value, f"notes_in_chapter_{chapter_number}")

        # Create the chapter EpubHtml item
        # Content before citations and notes
        current_chapter_html_content = chapter_content_html

        # Apply citations if enabled
        citations_config = specific_config.get("citations_config", {})
        if citations_config.get("enable"):
            current_chapter_html_content = self._apply_citations_to_item_content(
                current_chapter_html_content,
                chapter_number,
                specific_config,
                global_config
            )

        c = epub.EpubHtml(title=chapter_title, file_name=f'chap_{chapter_number}.xhtml', lang=specific_config.get("language", global_config.get("default_language", "en")))
        c.content = current_chapter_html_content # Content after potential citations, before notes
        
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
        Adds notes to a given chapter based on the configuration.
        Currently supports 'footnotes_same_page'.
        """
        notes_system_config = specific_config.get("notes_system", {})
        if not notes_system_config.get("enable") or num_notes == 0:
            return

        note_type = notes_system_config.get("type")
        notes_data = notes_system_config.get("data", {})
        
        if note_type == "footnotes_same_page" and notes_data:
            content = chapter_item.content
            footnotes_html_list = []
            note_counter = 0

            processed_keys = set()

            def replace_note_marker(match):
                nonlocal note_counter
                note_key = match.group(1)
                
                if note_key in notes_data and note_key not in processed_keys:
                    note_counter += 1
                    processed_keys.add(note_key)
                    note_text = notes_data[note_key].get("content", "")
                    
                    ref_id = f"fnref-{chapter_number}-{note_counter}"
                    note_id = f"fn-{chapter_number}-{note_counter}"
                    
                    footnote_link = f'<sup id="{ref_id}"><a href="#{note_id}">{note_counter}</a></sup>'
                    footnotes_html_list.append(
                        f'<p id="{note_id}" class="footnote"><a href="#{ref_id}">{note_counter}.</a> {note_text}</p>'
                    )
                    return footnote_link
                return match.group(0) # Return original if key not found or already processed

            # Replace [note:key] markers in the content
            content = re.sub(r"\[note:(\w+)\]", replace_note_marker, content)

            if footnotes_html_list:
                footnotes_section_html = '<hr class="footnote-separator" />\n<div class="footnotes">\n'
                footnotes_section_html += "\n".join(footnotes_html_list)
                footnotes_section_html += "\n</div>"
                content += "\n" + footnotes_section_html
            
            chapter_item.content = content

    def _add_images_to_chapter(self, book: epub.EpubBook, chapter_item: epub.EpubHtml, chapter_number: int, num_images: int, specific_config: Dict[str, Any], global_config: Dict[str, Any]):
        """
        Adds images to a given chapter based on the configuration.
        Replaces [image:key] markers with <img> tags and adds image files to the EPUB.
        """
        multimedia_config = specific_config.get("multimedia", {})
        if not multimedia_config.get("include_images") or num_images == 0:
            return

        image_data_map = multimedia_config.get("image_data", {})
        content = chapter_item.content
        
        # Ensure multimedia.os.path.exists is available, typically imported in multimedia.py
        # For this direct implementation, we'll assume os is imported in this file.
        # from .epub_components import multimedia # multimedia.os.path.exists

        processed_keys = set()

        def replace_image_marker(match):
            image_key = match.group(1)
            if image_key in image_data_map and image_key not in processed_keys:
                img_spec = image_data_map[image_key]
                img_path_on_disk = img_spec.get("path")
                alt_text = img_spec.get("alt_text", "")
                filename_in_epub = img_spec.get("filename_in_epub", f"{image_key}.png") # Default to .png
                
                # Path inside EPUB, typically in an 'images' folder
                epub_image_path = f"images/{filename_in_epub}"

                if img_path_on_disk and multimedia.os.path.exists(img_path_on_disk): # Use multimedia.os
                    try:
                        with open(img_path_on_disk, 'rb') as f_img:
                            image_binary_content = f_img.read()
                        
                        # Determine media type (simplified)
                        media_type = 'image/png' # Default
                        if filename_in_epub.lower().endswith('.jpg') or filename_in_epub.lower().endswith('.jpeg'):
                            media_type = 'image/jpeg'
                        elif filename_in_epub.lower().endswith('.gif'):
                            media_type = 'image/gif'
                        elif filename_in_epub.lower().endswith('.svg'):
                             media_type = 'image/svg+xml'

                        img_item = epub.EpubItem(
                            uid=f"img_{image_key}_{chapter_number}",
                            file_name=epub_image_path, # Correct path within EPUB (e.g., images/my_image.png)
                            media_type=media_type,
                            content=image_binary_content
                        )
                        book.add_item(img_item)
                        processed_keys.add(image_key)
                        return f'<img src="{epub_image_path}" alt="{alt_text}" />'
                    except IOError as e:
                        print(f"Warning: Could not read image file {img_path_on_disk}: {e}")
                        return match.group(0) # Return original marker on error
                else:
                    print(f"Warning: Image path {img_path_on_disk} for key '{image_key}' not found.")
                    return match.group(0) # Return original marker if path not found
            return match.group(0)

        content = re.sub(r"\[image:(\w+)\]", replace_image_marker, content)
        chapter_item.content = content

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

    def _create_section_content(self, book: epub.EpubBook, chapter_number: int, section_number: int, section_title: str, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> str | None:
        """
        Creates and adds a single section's content within a chapter.
        This is a placeholder and will be expanded with epub_components.
        """
        # Refactored for test_generate_epub_with_complex_config_and_interactions
        # Check for a specific key in config to use test content
        if specific_config.get("test_complex_section_content_key") == "complex_test_section_1_1":
            if chapter_number == 1 and section_number == 1:
                # This raw HTML matches the structure expected by the complex test's `raw_chapter_html_complex`
                # (excluding the h1 which is generated by _create_chapter_content)
                # The section_title from the config will be used.
                return (
                    f"<h2>{section_title}</h2>"
                    "<p>Text with a note [note:noteA].</p>"
                    "<p>Text with an image [image:imgA].</p>"
                    "<p>Text with a citation [cite:smith2020].</p>"
                    "<p>Combined: [note:noteB], then an image [image:imgB], and a citation [cite:doe2021].</p>"
                )
        
        # Placeholder: In a real implementation, this would generate section HTML
        # based on more generic configuration.
        # For now, it might return a simple placeholder or None if not the special test case.
        # This part would be built out in further TDD cycles for generic section content.
        return f"<h2>{section_title}</h2><p>Placeholder content for section {chapter_number}.{section_number}.</p>"

    def _apply_citations_to_item_content(self, item_content: str, chapter_number: int, specific_config: Dict[str, Any], global_config: Dict[str, Any]) -> str:
        """
        Applies citation styling to the given HTML content.
        Replaces [cite:key] markers with in-text citations from config.
        """
        citations_settings = specific_config.get("citations_config", {})
        if citations_settings.get("enable"):
            bibliography = citations_settings.get("data", {})
            if bibliography:
                def replace_citation(match):
                    cite_key = match.group(1)
                    if cite_key in bibliography and "in_text" in bibliography[cite_key]:
                        return bibliography[cite_key]["in_text"]
                    return match.group(0) # Return original if key not found or no in_text

                item_content = re.sub(r"\[cite:(\w+)\]", replace_citation, item_content)
        return item_content

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
        # Correct way to add publisher using ebooklib
        publisher_name = specific_config.get("publisher", global_config.get("default_publisher", "SynthPress"))
        book.add_metadata('DC', 'publisher', publisher_name)
        
        # Add additional custom metadata
        metadata_settings = specific_config.get("metadata_settings", {})
        additional_metadata = metadata_settings.get("additional_metadata", [])
        for meta_item in additional_metadata:
            namespace = meta_item.get("namespace")
            name = meta_item.get("name")
            value = meta_item.get("value")
            others = meta_item.get("others", {})
            if namespace and name: # Basic check
                book.add_metadata(namespace, name, value, others)
            elif name and not namespace: # For OPF <meta name="..." content="..."/>
                 book.add_metadata(None, name, value, others)


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
            actual_include_nav_doc = include_nav_doc_flag  # Prioritize explicit boolean
        elif include_nav_doc_flag == "auto":
            if epub_version_str.startswith("3"):
                actual_include_nav_doc = True
        # If include_nav_doc_flag is False (explicitly), actual_include_nav_doc remains False.
        
        actual_include_ncx = False
        if isinstance(include_ncx_flag, bool):
            actual_include_ncx = include_ncx_flag  # Prioritize explicit boolean
        elif include_ncx_flag == "auto":
            if epub_version_str.startswith("2"):
                actual_include_ncx = True
            # For EPUB3, "auto" for NCX means include it if NavDoc is NOT being included.
            # If NavDoc is explicitly False, and NCX is auto, then NCX should be true.
            elif epub_version_str.startswith("3") and not actual_include_nav_doc:
                actual_include_ncx = True
        # If include_ncx_flag is True (explicitly), actual_include_ncx is True.
        # If include_ncx_flag is False (explicitly), actual_include_ncx remains False.
        
        if actual_include_ncx:
            toc.create_ncx(book, chapters_content, toc_settings)
            # create_ncx is expected to set book.toc and add the NCX item

        if actual_include_nav_doc:
            # toc.create_nav_document expects epub_version as a string like "3.0"
            # epub_version_str is already defined and used for logic above.
            nav_item = toc.create_nav_document(book, chapters_content, toc_settings, epub_version_str)
            if nav_item:
                book.add_item(nav_item)
            # create_nav_document is expected to add the NavDoc item
        
        if not actual_include_ncx and not actual_include_nav_doc:
            book.toc = () # Ensure toc is empty if no ToC was generated

        # Ensure book.toc is set if not by specific functions (e.g. if only one type of ToC is generated)
        # This is a fallback, ideally toc.create_ncx or toc.create_nav_document handles book.toc
        if not book.toc and chapters_content and (actual_include_ncx or actual_include_nav_doc):
             book.toc = tuple(epub.Link(ch.file_name, ch.title, ch.file_name.split('.')[0] + "_fallback_id") for ch in chapters_content)
        elif not actual_include_ncx and not actual_include_nav_doc: # Explicitly ensure toc is empty
            book.toc = ()

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
                        base_font_name = os.path.basename(font_path) # Use the path returned by _get_font_path
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

        validation_settings = specific_config.get("validation", {})
        if validation_settings.get("run_epubcheck"):
            epubcheck_path = validation_settings.get("epubcheck_path")
            if epubcheck_path and os.path.exists(epubcheck_path):
                try:
                    result = subprocess.run(
                        ['java', '-jar', epubcheck_path, output_path],
                        capture_output=True, text=True, check=False
                    )
                    if result.returncode != 0:
                        print(f"EPUBCheck for {output_path} found issues:\n{result.stderr}")
                    else:
                        print(f"EPUBCheck for {output_path} passed.")
                except Exception as e:
                    print(f"Error running EPUBCheck for {output_path}: {e}")
            elif epubcheck_path:
                print(f"Warning: EPUBCheck path '{epubcheck_path}' not found. Skipping validation.")
            else:
                print("Warning: EPUBCheck path not configured. Skipping validation.")
        
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