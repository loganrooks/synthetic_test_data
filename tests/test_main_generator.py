import pytest
import os
import shutil
from pathlib import Path
from pytest_mock import MockerFixture

# Adjust the import path based on your project structure
# This assumes tests/ is at the same level as synth_data_gen/
from synth_data_gen import generate_data
from synth_data_gen.generators.epub import EpubGenerator
from synth_data_gen.generators.pdf import PdfGenerator
from synth_data_gen.generators.markdown import MarkdownGenerator

@pytest.fixture
def cleanup_main_generator_output():
    # Clean up any created directories after each test
    yield
    if os.path.exists("synthetic_output"):
        shutil.rmtree("synthetic_output")
    if os.path.exists("custom_test_output"):
        shutil.rmtree("custom_test_output")
    if os.path.exists("synthetic_output_default"): # Added for default config test
        shutil.rmtree("synthetic_output_default")


def test_generate_data_default_config(mocker: MockerFixture, cleanup_main_generator_output):
    """Test generate_data with no arguments (default configuration)."""
    mock_epub_generate = mocker.patch.object(EpubGenerator, 'generate')
    mock_pdf_generate = mocker.patch.object(PdfGenerator, 'generate')
    mock_md_generate = mocker.patch.object(MarkdownGenerator, 'generate')
    
    # Define expected output path from the default config in __init__.py
    expected_output_dir_base = Path("synthetic_output_default") # Matches default in ConfigLoader
    
    # Ensure the directory is clean before the test
    if expected_output_dir_base.exists():
        shutil.rmtree(expected_output_dir_base)

    # Mocks should return the path they were called with, as per BaseGenerator.generate contract
    # The actual file creation is handled by the (mocked) generator's generate method.
    # The test will verify that the mocks were called with the correct output path.
    
    # We need to know which subdir each generator will use. From __init__.py default config:
    # epub: "default_epubs", pdf: "default_pdfs", md: "default_markdown"
    expected_epub_path = expected_output_dir_base / "default_epubs" / "epub_1.epub" # Default filename pattern
    expected_pdf_path = expected_output_dir_base / "default_pdfs" / "pdf_1.pdf"
    expected_md_path = expected_output_dir_base / "default_markdown" / "markdown_1.md"

    mock_epub_generate.return_value = str(expected_epub_path)
    mock_pdf_generate.return_value = str(expected_pdf_path)
    mock_md_generate.return_value = str(expected_md_path)
    
    generated_files = generate_data()

    # Check that the base directory was created by ensure_output_directories
    assert expected_output_dir_base.exists(), f"Default base output directory '{expected_output_dir_base}' should be created."

    # Check if mocks were called correctly (implying subdirectories were handled)
    mock_epub_generate.assert_called_once()
    # The first argument to generate is specific_config, second is global_settings, third is output_file_path
    assert mock_epub_generate.call_args[0][2] == str(expected_epub_path)

    mock_pdf_generate.assert_called_once()
    assert mock_pdf_generate.call_args[0][2] == str(expected_pdf_path)
    
    mock_md_generate.assert_called_once()
    assert mock_md_generate.call_args[0][2] == str(expected_md_path)

    assert str(expected_epub_path) in generated_files
    assert str(expected_pdf_path) in generated_files
    assert str(expected_md_path) in generated_files
    assert len(generated_files) == 3


def test_generate_data_custom_config_obj(mocker: MockerFixture, cleanup_main_generator_output):
    """Test generate_data with a custom config_obj."""
    mock_epub_generate_custom = mocker.patch.object(EpubGenerator, 'generate')
    
    custom_base = "custom_test_output"
    custom_set = "custom_set"
    expected_custom_output_dir = Path(custom_base) / custom_set

    if expected_custom_output_dir.exists():
        shutil.rmtree(expected_custom_output_dir)

    def mock_custom_epub_creation_side_effect(*args, **kwargs):
        # output_file_path is the 3rd positional argument (index 2)
        output_file_path_str = args[2]
        output_file_path = Path(output_file_path_str)
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        output_file_path.touch()
        return str(output_file_path)

    mock_epub_generate_custom.side_effect = mock_custom_epub_creation_side_effect
    
    custom_config = {
        "output_directory_base": "custom_test_output",
        "output_set_name": "custom_set",
        "file_types": [
            {
                "type": "epub",
                "count": 1,
                "output_subdir": "custom_epubs", # Added for consistency with default config structure
                "epub_specific_settings": {"epub_specific_setting": "test_value"}
            }
        ]
    }
    generate_data(config_obj=custom_config)
    # The output_dir is now determined by the mock's side_effect based on call_args
    # We expect it to be called with something like:
    # custom_test_output/custom_set/custom_epubs/epub_1.epub
    
    # Check that the mock was called
    mock_epub_generate_custom.assert_called_once()
    
    # Verify the output directory based on the mock call's output_file_path argument
    called_output_path = Path(mock_epub_generate_custom.call_args[0][2])
    output_dir = called_output_path.parent
    
    assert output_dir.exists(), f"Custom output directory {output_dir} should be created."
    
    files_in_output_dir = list(output_dir.glob("*.epub")) # Check for epub as specified
    assert len(files_in_output_dir) > 0, "At least one EPUB file should be created in the custom output directory."

def test_generate_data_invalid_config_path(cleanup_main_generator_output):
    """Test generate_data with an invalid config_path."""
    with pytest.raises(FileNotFoundError):
        generate_data(config_path="non_existent_config.yaml")