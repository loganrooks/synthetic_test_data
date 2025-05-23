import pytest
import os
import shutil
from pathlib import Path
from pytest_mock import MockerFixture
import yaml # Added for creating dummy config file

from synth_data_gen import generate_data
from synth_data_gen.generators.epub import EpubGenerator
from synth_data_gen.generators.pdf import PdfGenerator
from synth_data_gen.generators.markdown import MarkdownGenerator
from synth_data_gen.core.config_loader import ConfigLoader # For direct instantiation if needed

# Define the root of the project or a base for test file paths
_TEST_ROOT_DIR = Path(__file__).parent.parent # Assuming tests/ is one level down from project root
_DEFAULT_CONFIG_RELATIVE_PATH = "synth_data_gen/core/default_config.yaml"
_ACTUAL_DEFAULT_CONFIG_PATH = _TEST_ROOT_DIR / _DEFAULT_CONFIG_RELATIVE_PATH

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


@pytest.fixture
def setup_test_environment(tmp_path: Path):
    """Creates a temporary directory structure for tests that need a realistic file system layout."""
    temp_core_dir = tmp_path / "synth_data_gen" / "core"
    temp_core_dir.mkdir(parents=True, exist_ok=True)
    temp_default_config_path = temp_core_dir / "default_config.yaml"
    
    default_config_content = {
        "output_directory_base": "synthetic_output_default",
        "output_formats": { # Changed from file_types to output_formats
            "epub": {"enabled": True, "count": 1, "output_subdir": "epubs", "config_ref": "epub_default_settings"},
            "pdf": {"enabled": True, "count": 1, "output_subdir": "pdfs", "config_ref": "pdf_default_settings"},
            "markdown": {"enabled": True, "count": 1, "output_subdir": "markdowns", "config_ref": "md_default_settings"}
        },
        "global_settings": {"max_files_per_type": 5},
        "epub_default_settings": {"title": "Default EPUB", "author": "Tester", "chapters_config": 1},
        "pdf_default_settings": {"title": "Default PDF", "author": "Tester", "page_count_config": 1},
        "md_default_settings": {"title": "Default Markdown", "headings_config": 1}
    }
    with open(temp_default_config_path, 'w') as f:
        yaml.dump(default_config_content, f)
    
    return tmp_path

def test_generate_data_default_config(mocker: MockerFixture, cleanup_main_generator_output, setup_test_environment):
    """Test generate_data with no arguments (default configuration)."""
    mock_epub_generate = mocker.patch.object(EpubGenerator, 'generate')
    mock_pdf_generate = mocker.patch.object(PdfGenerator, 'generate')
    mock_md_generate = mocker.patch.object(MarkdownGenerator, 'generate')

    # The generate_data function will look for default_config.yaml relative to its own location.
    # We need to patch where ConfigLoader looks for the default config, or where __init__ defines it.
    # The `setup_test_environment` fixture creates a dummy default config.
    # We need to make sure `generate_data` (via `ConfigLoader`) uses this dummy default config.

    # Patch the _DEFAULT_CONFIG_PATH in synth_data_gen.__init__ to point to our temp default config
    temp_default_config_path = setup_test_environment / "synth_data_gen" / "core" / "default_config.yaml"
    mocker.patch('synth_data_gen._DEFAULT_CONFIG_PATH', str(temp_default_config_path))

    # Expected output paths based on the dummy default_config_content
    expected_output_dir_base = Path("synthetic_output_default")
    expected_epub_path = expected_output_dir_base / "epubs" / "epub_1.epub"
    expected_pdf_path = expected_output_dir_base / "pdfs" / "pdf_1.pdf"
    expected_md_path = expected_output_dir_base / "markdowns" / "markdown_1.md"

    # Mock side effects to simulate file creation and return path
    # Individual generators' generate() method should return a list of paths
    # These side_effect functions are for the 'generate' method of the *instance*,
    # so they should not take 'config' and 'format_config' as arguments.
    def mock_gen_side_effect_epub(): # Removed config, format_config
        expected_epub_path.parent.mkdir(parents=True, exist_ok=True)
        expected_epub_path.touch() 
        return [str(expected_epub_path)]

    def mock_gen_side_effect_pdf(): # Removed config, format_config
        expected_pdf_path.parent.mkdir(parents=True, exist_ok=True)
        expected_pdf_path.touch()
        return [str(expected_pdf_path)]

    def mock_gen_side_effect_md(): # Removed config, format_config
        expected_md_path.parent.mkdir(parents=True, exist_ok=True)
        expected_md_path.touch()
        return [str(expected_md_path)]

    mock_epub_instance = mocker.MagicMock()
    mock_epub_instance.generate.side_effect = mock_gen_side_effect_epub 
    mocker.patch('synth_data_gen.generators.main_generator.EpubGenerator', return_value=mock_epub_instance)
    
    mock_pdf_instance = mocker.MagicMock()
    mock_pdf_instance.generate.side_effect = mock_gen_side_effect_pdf
    mocker.patch('synth_data_gen.generators.main_generator.PdfGenerator', return_value=mock_pdf_instance)

    mock_md_instance = mocker.MagicMock()
    mock_md_instance.generate.side_effect = mock_gen_side_effect_md
    mocker.patch('synth_data_gen.generators.main_generator.MarkdownGenerator', return_value=mock_md_instance)
    
    # Ensure the target directory is clean before the test
    if expected_output_dir_base.exists():
        shutil.rmtree(expected_output_dir_base)

    generated_files_dict = generate_data()

    assert expected_output_dir_base.exists(), f"Default base output directory '{expected_output_dir_base}' should be created."

    mock_epub_instance.generate.assert_called_once()
    mock_pdf_instance.generate.assert_called_once()
    mock_md_instance.generate.assert_called_once()

    assert generated_files_dict is not None, "generate_data should return a dictionary of generated files."
    assert str(expected_epub_path) in generated_files_dict.get("epub_files", [])
    assert str(expected_pdf_path) in generated_files_dict.get("pdf_files", [])
    assert str(expected_md_path) in generated_files_dict.get("markdown_files", [])
    assert sum(len(v) for v in generated_files_dict.values()) == 3


def test_generate_data_custom_config_obj(mocker: MockerFixture, cleanup_main_generator_output, setup_test_environment):
    """Test generate_data with a custom config_obj."""
    mock_epub_instance_custom = mocker.MagicMock()
    # Patch the constructor of EpubGenerator to return our mock instance
    EpubGenerator_constructor_mock = mocker.patch('synth_data_gen.generators.main_generator.EpubGenerator', return_value=mock_epub_instance_custom)
    
    temp_default_config_path = setup_test_environment / "synth_data_gen" / "core" / "default_config.yaml"
    mocker.patch('synth_data_gen._DEFAULT_CONFIG_PATH', str(temp_default_config_path))

    custom_base = "custom_test_output"
    custom_set = "custom_set" 
    epub_output_subdir = "my_epubs"
    # Define the expected output file path that the mocked generator should produce.
    expected_custom_output_file = Path(custom_base) / custom_set / epub_output_subdir / "epub_c_1.epub" 

    if Path(custom_base).exists():
        shutil.rmtree(custom_base)

    # Define the side effect for the mocked EpubGenerator's generate method
    def mock_custom_epub_generate_side_effect():
        expected_custom_output_file.parent.mkdir(parents=True, exist_ok=True)
        expected_custom_output_file.touch() # Simulate file creation
        return [str(expected_custom_output_file)] # Must return a list of paths

    mock_epub_instance_custom.generate.side_effect = mock_custom_epub_generate_side_effect
    
    custom_config = {
        "output_directory_base": custom_base,
        "output_set_name": custom_set, # This is used by generators to create subfolders
        "output_formats": { 
            "epub": {
                "enabled": True, 
                "count": 1,
                "output_subdir": epub_output_subdir, 
                "config_ref": "custom_epub_settings",
                "base_file_name": "epub_c" # Added for predictable naming
            }
        },
        "global_settings": {"max_files_per_type": 2},
        "custom_epub_settings": { 
            "title": "Custom EPUB",
            "author": "Custom Author",
            "chapters_config": 2
        }
    }
    
    generated_files_dict = generate_data(config_obj=custom_config)

    assert Path(custom_base).exists(), f"Custom base output directory '{custom_base}' should be created."
    assert expected_custom_output_file.parent.exists(), f"Directory for custom epub '{expected_custom_output_file.parent}' should be created."

    mock_epub_instance_custom.generate.assert_called_once()
    
    # Check the arguments passed to the EpubGenerator constructor
    EpubGenerator_constructor_mock.assert_called_once()
    constructor_args = EpubGenerator_constructor_mock.call_args[0]
    passed_full_config = constructor_args[0]
    passed_format_config = constructor_args[1]

    assert passed_full_config["output_directory_base"] == custom_base
    assert passed_format_config["output_subdir"] == epub_output_subdir
    assert passed_format_config["config_ref"] == "custom_epub_settings"

    assert generated_files_dict is not None
    assert str(expected_custom_output_file) in generated_files_dict.get("epub_files", [])
    assert sum(len(v) for v in generated_files_dict.values()) == 1

def test_generate_data_invalid_config_path(cleanup_main_generator_output):
    """Test generate_data with an invalid config_file_path."""
    with pytest.raises(FileNotFoundError):
        generate_data(config_file_path="non_existent_config.yaml")