import pytest
import os
import shutil
from pathlib import Path

# Adjust the import path based on your project structure
from synth_data_gen.common import utils

@pytest.fixture
def cleanup_generated_dir():
    # Clean up the base 'generated' directory if it was created
    # This is a bit broad, but ensures a clean state for directory tests
    generated_dir_path = Path(utils.PROJECT_ROOT) / "generated"
    if generated_dir_path.exists():
        shutil.rmtree(generated_dir_path)
    yield
    if generated_dir_path.exists():
        shutil.rmtree(generated_dir_path)

def test_ensure_output_directories_creates_all(cleanup_generated_dir):
    """Test that ensure_output_directories creates all expected subdirectories."""
    # Ensure the base 'generated' directory does not exist before the test
    base_generated_dir = Path(utils.PROJECT_ROOT) / "generated"
    if base_generated_dir.exists():
        shutil.rmtree(base_generated_dir)
    
    utils.ensure_output_directories(utils.BASE_OUTPUT_DIR)

    # Check for the existence of all directories defined in utils.py
    # These paths are relative to utils.PROJECT_ROOT / "generated"
    expected_dirs = [
        Path(utils.EPUB_DIR) / "toc",
        Path(utils.EPUB_DIR) / "headers",
        Path(utils.EPUB_DIR) / "notes",
        Path(utils.EPUB_DIR) / "citations_bibliography",
        Path(utils.EPUB_DIR) / "images_fonts",
        Path(utils.EPUB_DIR) / "structure_metadata",
        Path(utils.EPUB_DIR) / "content_types",
        Path(utils.EPUB_DIR) / "general_edge_cases",
        Path(utils.PDF_DIR) / "text_based",
        Path(utils.PDF_DIR) / "image_based_ocr",
        Path(utils.PDF_DIR) / "structure",
        Path(utils.PDF_DIR) / "notes",
        Path(utils.PDF_DIR) / "general_edge_cases",
        Path(utils.MD_DIR) / "basic",
        Path(utils.MD_DIR) / "extended",
        Path(utils.MD_DIR) / "frontmatter",
        Path(utils.MD_DIR) / "general_edge_cases",
    ]

    for dir_path in expected_dirs:
        # We need to construct the full path from PROJECT_ROOT for assertion
        # as EPUB_DIR etc are already absolute.
        assert dir_path.exists(), f"Directory {dir_path} should be created."