"""
Constants and Enums for the synth_data_gen package.

This module centralizes all magic strings and configuration values
used throughout the codebase for better maintainability and type safety.
"""
from enum import Enum


class GeneratorType(str, Enum):
    """Supported generator types for synthetic data generation."""
    EPUB = "epub"
    PDF = "pdf"
    MARKDOWN = "markdown"

    def __str__(self) -> str:
        return self.value


class PdfVariant(str, Enum):
    """PDF generation variants/templates."""
    SINGLE_COLUMN_TEXT = "single_column_text"
    MULTI_COLUMN_TEXT = "multi_column_text"
    VISUAL_TOC_HYPERLINKED = "visual_toc_hyperlinked"
    RUNNING_HEADERS_FOOTERS = "running_headers_footers"
    BOTTOM_PAGE_FOOTNOTES = "bottom_page_footnotes"
    SIMPLE_TABLE = "simple_table"

    def __str__(self) -> str:
        return self.value


class NotesSystemType(str, Enum):
    """Types of note systems for documents."""
    FOOTNOTES_SAME_PAGE = "footnotes_same_page"
    ENDNOTES_CHAPTER = "endnotes_chapter"
    ENDNOTES_BOOK = "endnotes_book"
    SIDENOTES = "sidenotes"
    NONE = "none"

    def __str__(self) -> str:
        return self.value


class FrontmatterStyle(str, Enum):
    """Frontmatter format styles for Markdown files."""
    YAML = "yaml"
    TOML = "toml"
    JSON = "json"

    def __str__(self) -> str:
        return self.value


class TocStyle(str, Enum):
    """Table of Contents styles for EPUB."""
    NAVDOC_FULL = "navdoc_full"
    NAVDOC_MINIMAL = "navdoc_minimal"
    NCX_ONLY = "ncx_only"
    BOTH_FULL = "both_full"

    def __str__(self) -> str:
        return self.value


class PageNumberStyle(str, Enum):
    """Page number display styles for Visual ToC."""
    DOT_LEADER = "dot_leader"
    NO_PAGE_NUMBERS = "no_page_numbers"
    PLAIN = "plain"
    NONE = "none"

    def __str__(self) -> str:
        return self.value


class LogLevel(str, Enum):
    """Standard logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value


class PageSize(str, Enum):
    """Standard page sizes for PDF generation."""
    LETTER = "letter"
    A4 = "a4"
    LEGAL = "legal"
    A5 = "a5"

    def __str__(self) -> str:
        return self.value


class PageOrientation(str, Enum):
    """Page orientation options."""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

    def __str__(self) -> str:
        return self.value


class FileExtension(str, Enum):
    """File extensions for generated files."""
    EPUB = ".epub"
    PDF = ".pdf"
    MARKDOWN = ".md"
    YAML = ".yaml"
    JSON = ".json"

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Default Values
# =============================================================================

class Defaults:
    """Default configuration values."""

    # Output directories
    OUTPUT_DIR_BASE = "synthetic_output"
    EPUB_SUBDIR = "epub"
    PDF_SUBDIR = "pdf"
    MARKDOWN_SUBDIR = "markdown"

    # PDF defaults
    PDF_VARIANT = PdfVariant.SINGLE_COLUMN_TEXT
    PAGE_SIZE = PageSize.LETTER
    ORIENTATION = PageOrientation.PORTRAIT
    BASE_FONT_FAMILY = "Helvetica"
    BASE_FONT_SIZE_PT = 12

    # EPUB defaults
    EPUB_VERSION = "3.0"
    TOC_STYLE = TocStyle.NAVDOC_FULL
    TOC_MAX_DEPTH = 3

    # Markdown defaults
    FRONTMATTER_STYLE = FrontmatterStyle.YAML

    # Notes system
    NOTES_SYSTEM_TYPE = NotesSystemType.FOOTNOTES_SAME_PAGE

    # Logging
    LOG_LEVEL = LogLevel.WARNING

    # Configuration
    DEFAULT_LANGUAGE = "en"
    DEFAULT_AUTHOR = "Synthetic Data Generator"


# =============================================================================
# Config Keys (to avoid typos in dictionary access)
# =============================================================================

class ConfigKeys:
    """Standard configuration dictionary keys."""

    # Top-level keys
    FILE_TYPES = "file_types"
    GLOBAL_SETTINGS = "global_settings"
    OUTPUT_DIRECTORY_BASE = "output_directory_base"

    # Generator-specific settings keys
    EPUB_SETTINGS = "epub_settings"
    PDF_SETTINGS = "pdf_settings"
    MARKDOWN_SETTINGS = "markdown_settings"

    # Common keys
    TYPE = "type"
    COUNT = "count"
    TITLE = "title"
    AUTHOR = "author"
    LANGUAGE = "language"
    OUTPUT_SUBDIR = "output_subdir"

    # PDF keys
    PDF_VARIANT = "pdf_variant"
    PAGE_SETUP = "page_setup"
    PAGE_SIZE = "page_size"
    ORIENTATION = "orientation"
    ROTATION = "rotation"
    MARGINS_MM = "margins_mm"
    VISUAL_TOC = "visual_toc"
    CHAPTERS_CONFIG = "chapters_config"
    PAGE_COUNT_CONFIG = "page_count_config"

    # EPUB keys
    TOC_SETTINGS = "toc_settings"
    NOTES_SYSTEM = "notes_system"
    STYLE = "style"
    MAX_DEPTH = "max_depth"

    # Markdown keys
    FRONTMATTER = "frontmatter"
    INCLUDE_FRONTMATTER = "include_frontmatter"

    # Boolean/enable keys
    ENABLE = "enable"
    INCLUDE = "include"


# =============================================================================
# Generator ID to Type mapping
# =============================================================================

GENERATOR_TYPE_MAP = {
    GeneratorType.EPUB.value: GeneratorType.EPUB,
    GeneratorType.PDF.value: GeneratorType.PDF,
    GeneratorType.MARKDOWN.value: GeneratorType.MARKDOWN,
}

# Extension mapping
GENERATOR_EXTENSION_MAP = {
    GeneratorType.EPUB: FileExtension.EPUB,
    GeneratorType.PDF: FileExtension.PDF,
    GeneratorType.MARKDOWN: FileExtension.MARKDOWN,
}
