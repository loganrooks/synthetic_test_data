import pytest
from unittest.mock import patch, MagicMock, mock_open # Added mock_open
import json # Added json

from synth_data_gen import generate_data
# from synth_data_gen.generators.epub import EpubGenerator # Import EpubGenerator
# Assuming ConfigLoader will be imported in synth_data_gen.__init__
# from synth_data_gen.core.config_loader import ConfigLoader

# A simple schema for testing
SIMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "project_name": {"type": "string"},
        "output_directory": {"type": "string"},
        "file_types": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["project_name", "output_directory", "file_types"]
}

@pytest.fixture
def mock_config_loader_instance():
    """Fixture to provide a mocked ConfigLoader instance."""
    mock_instance = MagicMock()
    mock_instance.load_and_validate_config.return_value = {
        "project_name": "TestProject",
        "output_directory_base": "test_output", # Used by MainGenerator
        "output_formats": {
            "epub": {
                "enabled": True, "count": 1, "output_subdir": "epubs",
                # Specific epub settings directly here
                "title": "Test EPUB From Mock", "author": "Test Author EPUB"
            },
            "pdf": {
                "enabled": True, "count": 1, "output_subdir": "pdfs",
                # Specific pdf settings
                "author": "Test PDF Author From Mock", "page_size": "A4"
            },
            "markdown": { # Example for markdown
                "enabled": True, "count": 1, "output_subdir": "mds",
                "flavor": "commonmark" # Specific markdown setting
            }
        },
        "global_settings": {"default_language": "en"}
    }
    # get_generator_config is not directly called by generate_data on the loader instance anymore.
    return mock_instance

@pytest.fixture
def mock_config_loader_class(mock_config_loader_instance):
    """Fixture to patch the ConfigLoader class."""
    with patch('synth_data_gen.ConfigLoader', return_value=mock_config_loader_instance) as mock_class:
        yield mock_class

def test_generate_data_calls_config_loader_load_and_validate(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test that generate_data instantiates ConfigLoader and calls
    load_and_validate_config with the correct config_path and schema.
    """
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("""
project_name: TestProject
output_directory: test_output
# ... content to match what load_and_validate_config would process ...
output_formats:
  epub:
    enabled: true
    count: 1
    title: Test EPUB
  pdf:
    enabled: true
    count: 1
    author: Test PDF Author
global_settings:
  default_language: "en"
""")
    
    mocked_schema = {"type": "object", "description": "Mocked Schema for test"}

    # Patch open and json.load in the scope of synth_data_gen module
    # Also patch os.path.exists for schema file checking
    with patch('synth_data_gen.os.path.exists') as mock_path_exists, \
         patch('synth_data_gen.open', mock_open(read_data=json.dumps(mocked_schema))) as mock_file_open, \
         patch('synth_data_gen.json.load', return_value=mocked_schema) as mock_json_load, \
         patch('synth_data_gen.generators.main_generator.EpubGenerator'), \
         patch('synth_data_gen.generators.main_generator.PdfGenerator'), \
         patch('synth_data_gen.generators.main_generator.MarkdownGenerator'):

            mock_path_exists.return_value = True # Assume schema file exists for loading

            generate_data(config_file_path=str(config_file)) # Changed config_path to config_file_path

            mock_config_loader_class.assert_called_once() 
            
            # Check that schema loading was attempted
            # Import the actual variable from the synth_data_gen module for assertion
            from synth_data_gen import _DEFAULT_SCHEMA_PATH as DEFAULT_SCHEMA_PATH_IN_SUT
            mock_path_exists.assert_any_call(DEFAULT_SCHEMA_PATH_IN_SUT)
            mock_file_open.assert_called_once_with(DEFAULT_SCHEMA_PATH_IN_SUT, 'r')
            mock_json_load.assert_called_once_with(mock_file_open())
            
            mock_config_loader_instance.load_and_validate_config.assert_called_once_with(
                file_path=str(config_file),
                schema=mocked_schema,
                config_override_object=None
            )

def test_generate_data_dispatches_epub_config_correctly(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test that generate_data, through MainGenerator, correctly uses EpubGenerator
    with the appropriate configuration.
    """
    config_file = tmp_path / "test_config_epub_dispatch.yaml"
    # This file content is less critical now as mock_config_loader_instance dictates the loaded config.
    # However, it's good practice for it to be plausible.
    config_file.write_text("""
project_name: EpubDispatchTest
output_directory_base: epub_dispatch_output
output_formats:
  epub:
    enabled: true
    count: 1
    output_subdir: epubs
    title: "Dispatched EPUB Title" # Specific setting
    author: "Dispatched Author"   # Specific setting
global_settings:
  default_language: "en"
""")

    full_mock_loaded_config = mock_config_loader_instance.load_and_validate_config.return_value
    # Ensure the fixture provides what we expect for "epub"
    assert "epub" in full_mock_loaded_config["output_formats"], "Fixture mock_config_loader_instance needs epub in output_formats"
    expected_epub_format_config = full_mock_loaded_config["output_formats"]["epub"]

    MockEpubGeneratorClass = MagicMock()
    mock_epub_generator_instance = MockEpubGeneratorClass.return_value

    # Patch EpubGenerator where MainGenerator imports it.
    # Also patch other generators that might be in the mocked config to avoid their actual execution.
    with patch('synth_data_gen.generators.main_generator.EpubGenerator', MockEpubGeneratorClass), \
         patch('synth_data_gen.generators.main_generator.PdfGenerator', MagicMock()), \
         patch('synth_data_gen.generators.main_generator.MarkdownGenerator', MagicMock()):
        
        # We need to ensure that generate_data uses the schema loading logic correctly,
        # so we mock those parts as in the previous test.
        mocked_schema = {"type": "object", "description": "Mocked Schema for dispatch test"}
        with patch('synth_data_gen.os.path.exists') as mock_path_exists, \
             patch('synth_data_gen.open', mock_open(read_data=json.dumps(mocked_schema))) as mock_file_open, \
             patch('synth_data_gen.json.load', return_value=mocked_schema) as mock_json_load:
            
            mock_path_exists.return_value = True # Assume schema file exists

            generate_data(config_file_path=str(config_file)) # Changed config_path to config_file_path

            # Verify EpubGenerator was instantiated correctly by MainGenerator
            MockEpubGeneratorClass.assert_called_once_with(
                full_mock_loaded_config,     # This is the 'global_config' (entire loaded config)
                expected_epub_format_config  # This is the 'format_config' for epub
            )
            
            # Verify its generate method was called (now takes no args other than self)
            mock_epub_generator_instance.generate.assert_called_once_with()
            
            # Ensure schema loading was also done as expected
            mock_json_load.assert_called_once()


def test_generate_data_handles_missing_epub_config_gracefully(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test how MainGenerator handles a format if its specific config details are sparse
    or if the format is requested but not deeply configured in output_formats.
    MainGenerator will pass the format_config as is; the individual generator
    is responsible for its own defaults if format_config is minimal.
    If 'enabled' is false or the format is not in output_formats, it's skipped.
    """
    config_file = tmp_path / "test_config_minimal_epub.yaml"
    config_file.write_text("""
project_name: MinimalEpubTest
output_directory_base: minimal_epub_output
output_formats:
  epub: # EPUB is requested
    enabled: true
    count: 1
    # Deliberately sparse, e.g., no title or author here
    # The EpubGenerator itself should handle defaults.
global_settings:
  default_language: "en"
""")

    # Adjust the mock_config_loader_instance for this specific test case
    # to return a config with a sparse "epub" entry in "output_formats".
    config_with_minimal_epub = {
        "project_name": "MinimalEpubTest",
        "output_directory_base": "minimal_epub_output",
        "output_formats": {
            "epub": { # Enabled, but sparse
                "enabled": True, 
                "count": 1,
                "output_subdir": "epubs_minimal" 
                # Missing title, author etc. that were in the main fixture
            },
            "pdf": { # Include another to ensure it doesn't interfere
                "enabled": True, "count": 1, "output_subdir": "pdfs_minimal",
                "author": "Test PDF Author"
            }
        },
        "global_settings": {"default_language": "en"}
    }
    mock_config_loader_instance.load_and_validate_config.return_value = config_with_minimal_epub
    
    expected_epub_format_config_minimal = config_with_minimal_epub["output_formats"]["epub"]

    MockEpubGeneratorClass = MagicMock()
    mock_epub_generator_instance = MockEpubGeneratorClass.return_value
    # We don't mock get_default_specific_config on the generator instance anymore,
    # as MainGenerator doesn't call it. The generator's __init__ should handle defaults.

    with patch('synth_data_gen.generators.main_generator.EpubGenerator', MockEpubGeneratorClass), \
         patch('synth_data_gen.generators.main_generator.PdfGenerator', MagicMock()), \
         patch('synth_data_gen.generators.main_generator.MarkdownGenerator', MagicMock()):

        mocked_schema = {"type": "object", "description": "Mocked Schema for minimal epub test"}
        with patch('synth_data_gen.os.path.exists') as mock_path_exists, \
             patch('synth_data_gen.open', mock_open(read_data=json.dumps(mocked_schema))), \
             patch('synth_data_gen.json.load', return_value=mocked_schema):
            
            mock_path_exists.return_value = True
            generate_data(config_file_path=str(config_file)) # Changed config_path to config_file_path

            MockEpubGeneratorClass.assert_called_once_with(
                config_with_minimal_epub,
                expected_epub_format_config_minimal 
            )
            mock_epub_generator_instance.generate.assert_called_once_with()


def test_generate_data_end_to_end_with_mocked_generators(tmp_path, mock_config_loader_class, mock_config_loader_instance):
    """
    Test generate_data end-to-end with mocked generators, focusing on config flow
    through MainGenerator.
    """
    config_content = """
project_name: EndToEndTest
output_directory_base: e2e_output # Corrected key for MainGenerator
output_formats:
  epub:
    enabled: true
    count: 1
    output_subdir: epubs
    title: "E2E EPUB Title"
    epub_version: "2.0"
  pdf:
    enabled: true
    count: 2 # PDF to be generated twice
    output_subdir: pdfs
    author: "E2E PDF Author"
    page_size: "A4"
  markdown:
    enabled: true
    count: 1
    output_subdir: mds
    # No specific markdown settings here, generator should use defaults
    flavor: "gfm" 
global_settings:
  default_language: "fr"
"""
    config_file = tmp_path / "e2e_test_config.yaml"
    config_file.write_text(config_content)

    # Use the mock_config_loader_instance fixture's return value for assertions
    # but ensure the test's config_content aligns with what the fixture provides
    # if we were to load it for real. For this test, we'll use a dedicated
    # loaded_config that matches the config_content.
    
    loaded_config_for_e2e = {
        "project_name": "EndToEndTest",
        "output_directory_base": "e2e_output",
        "output_formats": {
            "epub": {
                "enabled": True, "count": 1, "output_subdir": "epubs",
                "title": "E2E EPUB Title", "epub_version": "2.0"
            },
            "pdf": {
                "enabled": True, "count": 2, "output_subdir": "pdfs",
                "author": "E2E PDF Author", "page_size": "A4"
            },
            "markdown": {
                "enabled": True, "count": 1, "output_subdir": "mds",
                "flavor": "gfm"
            }
        },
        "global_settings": {"default_language": "fr"},
    }
    mock_config_loader_instance.load_and_validate_config.return_value = loaded_config_for_e2e
    
    expected_epub_format_config = loaded_config_for_e2e["output_formats"]["epub"]
    expected_pdf_format_config = loaded_config_for_e2e["output_formats"]["pdf"]
    expected_md_format_config = loaded_config_for_e2e["output_formats"]["markdown"]
    
    MockEpubGeneratorClass = MagicMock()
    mock_epub_gen_instance = MockEpubGeneratorClass.return_value
    mock_epub_gen_instance.generate.return_value = ["path/to/epub_1.epub"] # MainGenerator expects a list

    MockPdfGeneratorClass = MagicMock()
    mock_pdf_gen_instance = MockPdfGeneratorClass.return_value
    # MainGenerator calls generate() once per format, but the generator's internal logic
    # handles the 'count'. So, the generator's generate() should return a list of 'count' files.
    mock_pdf_gen_instance.generate.return_value = ["path/to/pdf_1.pdf", "path/to/pdf_2.pdf"]

    MockMarkdownGeneratorClass = MagicMock()
    mock_md_gen_instance = MockMarkdownGeneratorClass.return_value
    mock_md_gen_instance.generate.return_value = ["path/to/md_1.md"]

    # Patch generator classes where MainGenerator imports them
    with patch('synth_data_gen.generators.main_generator.EpubGenerator', MockEpubGeneratorClass), \
         patch('synth_data_gen.generators.main_generator.PdfGenerator', MockPdfGeneratorClass), \
         patch('synth_data_gen.generators.main_generator.MarkdownGenerator', MockMarkdownGeneratorClass):

        mocked_schema = {"type": "object", "description": "Mocked Schema for e2e test"}
        with patch('synth_data_gen.os.path.exists') as mock_path_exists, \
             patch('synth_data_gen.open', mock_open(read_data=json.dumps(mocked_schema))), \
             patch('synth_data_gen.json.load', return_value=mocked_schema):
            
            mock_path_exists.return_value = True
            generated_files_details = generate_data(config_file_path=str(config_file)) # Changed config_path to config_file_path

            # Verify ConfigLoader calls
            mock_config_loader_class.assert_called_once()
            mock_config_loader_instance.load_and_validate_config.assert_called_once_with(
                file_path=str(config_file),
                schema=mocked_schema,
                config_override_object=None
            )
            
            # Verify EpubGenerator
            MockEpubGeneratorClass.assert_called_once_with(loaded_config_for_e2e, expected_epub_format_config)
            mock_epub_gen_instance.generate.assert_called_once_with()

            # Verify PdfGenerator
            MockPdfGeneratorClass.assert_called_once_with(loaded_config_for_e2e, expected_pdf_format_config)
            mock_pdf_gen_instance.generate.assert_called_once_with()

            # Verify MarkdownGenerator
            MockMarkdownGeneratorClass.assert_called_once_with(loaded_config_for_e2e, expected_md_format_config)
            mock_md_gen_instance.generate.assert_called_once_with()

            # Verify returned paths from generate_data
            assert generated_files_details is not None
            assert generated_files_details["epub_files"] == ["path/to/epub_1.epub"]
            assert generated_files_details["pdf_files"] == ["path/to/pdf_1.pdf", "path/to/pdf_2.pdf"]
            assert generated_files_details["markdown_files"] == ["path/to/md_1.md"]

# def test_generate_data_dispatches_pdf_config_correctly():
#     pass